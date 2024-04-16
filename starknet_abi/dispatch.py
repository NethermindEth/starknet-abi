from dataclasses import dataclass
from typing import Any, Sequence

from starknet_abi.abi_types import (
    STARKNET_ACCOUNT_CALL,
    AbiParameter,
    StarknetArray,
    StarknetType,
)
from starknet_abi.core import StarknetAbi
from starknet_abi.decode import decode_from_params, decode_from_types
from starknet_abi.decoding_types import DecodedEvent, DecodedFunction
from starknet_abi.exceptions import InvalidCalldataError

# fmt: off

# starknet_keccak(b'__execute__')[-8:]
EXECUTE_SIGNATURE = bytes.fromhex("5e85627ee876e5ad")

# starknet_keccak(b'__validate__')[-8:]
VALIDATE_SIGNATURE = bytes.fromhex("0ff0b2189d9c7775")

# starknet_keccak(b'__validate_deploy__')[-8:]
VALIDATE_DEPLOY_SIGNATURE = bytes.fromhex("3972f0af8aa92895")

# starknet_keccak(b'__validate_declare__')[-8:]
VALIDATE_DECLARE_SIGNATURE = bytes.fromhex("fa4008dcdb4963b3")

CORE_FUNCTIONS: dict[bytes, dict[str, Any]] = {
    EXECUTE_SIGNATURE: {
        "name": "__execute__",
        "inputs": [AbiParameter("calls", StarknetArray(STARKNET_ACCOUNT_CALL))],
    },
    VALIDATE_SIGNATURE: {
        "name": "__validate__",
        "inputs": [AbiParameter("calls", StarknetArray(STARKNET_ACCOUNT_CALL))],
    },
    VALIDATE_DEPLOY_SIGNATURE: {
        "name": "__validate_deploy__",
        "inputs": [],
    },
    VALIDATE_DECLARE_SIGNATURE: {
        "name": "__validate_declare__",
        "inputs": [],
    },
}

# fmt: on


@dataclass(slots=True)
class FunctionDispatchInfo:
    """
    Dispatcher storing a function name, and a reference to the type of the event.  The reference is the result of
    hash(AbiFunction.id_str())
    """

    decoder_reference: int  # Result of hash(type.id_str())
    function_name: str


@dataclass(slots=True)
class EventDispatchInfo:
    """
    Dispatcher storing an Event Name, and a reference to the type of the event.  The reference is the hash of the
    event type id_str(), and is stored in a separate mapping to reduce object size
    """

    decoder_reference: int  # Result of hash(type.id_str())
    event_name: str


@dataclass(slots=True)
class ClassDispatcher:
    """
    Dispatcher Entry for a Class.  Contains a mapping from function_ids -> FunctionDispatchInfo and a mapping from
    event_ids -> EventDispatchInfo.  Also contains full class hash, abi name, and will later include additional
    metadata fields/classifications ie. Proxy or ArgentAccount
    """

    function_ids: dict[bytes, FunctionDispatchInfo]
    event_ids: dict[bytes, EventDispatchInfo]
    abi_name: str | None
    class_hash: bytes


@dataclass(slots=True)
class DecodingDispatcher:
    """

    Decoding Dispatcher Class for Efficiently Decoding several thousand ABIs at once.  Maps Class Ids to Function
    and Event Ids.  For more efficient in-memory representation, the last 8 bytes of class hashes and selectors
    are used as Class/Function/Event Ids.

    Each tier in the decoding dispatcher has a dispatcher dataclass which stores data like abi_name, and other
    parameters that can be configured to provide more detailed info about which abis are being decoded
    """

    class_ids: dict[bytes, ClassDispatcher]

    function_types: dict[
        int,  # Result of hash(type.id_str())  --> 8 bytes on 64bit machines
        tuple[
            Sequence[AbiParameter],  # Parameters for Function Inputs
            Sequence[StarknetType],  # Types of Function Outputs
        ],
    ]

    event_types: dict[
        int,  # Result of hash(type.id_str())  --> 8 bytes on 64bit machines
        tuple[
            Sequence[AbiParameter],  # Parameters for Event Data
            Sequence[AbiParameter],  # Parameters for Event Keys
        ],
    ]

    def __init__(self):
        self.class_ids = {}
        self.event_types = {}
        self.function_types = {}

    def _add_abi_functions(self, abi: StarknetAbi) -> dict[bytes, FunctionDispatchInfo]:
        """
        Parse the list of ABI Functions to a dictionary of FunctionDispatchInfo objects.
        For each function, in the ABI, compute the id_str(), and hash that id-str.  If the hash of the id-str is not
        present in DecodingDispatcher.function_types, add it.

        :param abi: Starknet ABI to Add
        :return: dict[function_signature[-8:]: FunctionDispatchInfo]
        """

        function_ids = {}
        for function in abi.functions.values():
            function_type_id = hash(function.id_str())
            if function_type_id not in self.function_types:
                self.function_types.update(
                    {function_type_id: (function.inputs, function.outputs)}
                )
            function_ids.update(
                {
                    function.signature[-8:]: FunctionDispatchInfo(
                        decoder_reference=function_type_id,
                        function_name=function.name,
                    )
                }
            )
        return function_ids

    def _add_abi_events(self, abi: StarknetAbi) -> dict[bytes, EventDispatchInfo]:
        """
        Parse the list of ABI Events to a dictionary of EventDispatchInfo objects.
        For each event, in the ABI, compute the id_str(), and hash that id-str.  If the hash of the id-str is not
        present in DecodingDispatcher.event_types, add it.

        :param abi: Starknet ABI to add
        :return: dict[event_signature[-8:]: EventDispatchInfo]
        """
        event_ids = {}
        for event in abi.events.values():
            event_type_id = hash(event.id_str())
            if event_type_id not in self.event_types:
                self.event_types.update({event_type_id: (event.data, event.keys)})

            event_ids.update(
                {
                    event.signature[-8:]: EventDispatchInfo(
                        decoder_reference=event_type_id,
                        event_name=event.name,
                    )
                }
            )
        return event_ids

    def add_abi(self, abi: StarknetAbi):
        """
        Adds a parsed StarknetAbi to the DecodingDispatcher, storing all functions and events in the mapping.
        If a function or event has the same type as another already loaded abi, the reference to the parsed type
        is cached and shared between the identical functions

        :param abi:
        :return:
        """
        class_id = abi.class_hash[-8:]

        class_dispatcher = ClassDispatcher(
            abi_name=abi.abi_name,
            class_hash=abi.class_hash,
            function_ids=self._add_abi_functions(abi),
            event_ids=self._add_abi_events(abi),
        )
        self.class_ids.update({class_id: class_dispatcher})

    def decode_function(  # pylint: disable=too-many-locals
        self,
        calldata: list[int],
        result: list[int],
        function_selector: bytes,
        class_hash: bytes,
    ) -> DecodedFunction | None:
        """
        Attempts to decode the input calldata and result array into a DecodedFunction.

        If the class-hash is not present in the Dispatcher, None is returned

        :param calldata: array of calldata as integers
        :param result: array of calldata as intergers
        :param function_selector: function_selector of the trace or transaction
        :param class_hash:  class hash of the trace or transaction
        :return:
        """
        decode_id = function_selector[-8:]

        if decode_id in CORE_FUNCTIONS:
            input_types: Sequence[AbiParameter] = CORE_FUNCTIONS[decode_id]["inputs"]
            function_name = CORE_FUNCTIONS[decode_id]["name"]
            output_types: Sequence[StarknetType] = []
            abi_name = None

        else:
            class_dispatcher = self.class_ids.get(class_hash[-8:])
            if class_dispatcher is None:
                return None

            # Both function_dispatcher and function_type should throw if keys not found
            function_dispatcher = class_dispatcher.function_ids[function_selector[-8:]]
            input_types, output_types = self.function_types[
                function_dispatcher.decoder_reference
            ]
            function_name, abi_name = (
                function_dispatcher.function_name,
                class_dispatcher.abi_name,
            )

        # Copy Arrays that can be consumed by decoder
        _calldata, _result = calldata.copy(), result.copy()
        decoded_inputs = decode_from_params(input_types, _calldata)
        decoded_outputs = decode_from_types(output_types, _result)

        if len(_calldata) > 0:
            raise InvalidCalldataError(
                f"Calldata Remaining after decoding function input {calldata} from {input_types}"
            )

        if len(_result) > 0:
            raise InvalidCalldataError(
                f"Calldata Remaining after decoding function result {result} from {output_types}"
            )

        return DecodedFunction(
            abi_name=abi_name,
            func_name=function_name,
            inputs=decoded_inputs,
            outputs=decoded_outputs,
        )

    def decode_event(
        self,
        data: list[int],
        keys: list[int],
        class_hash: bytes,
    ) -> DecodedEvent | None:
        """
        Decodes an emitted event.  If the ClassHash is not present in the Dispatcher, returns None

        The class hash, and keys[0] are used to select the dispatcher entry for the specific event

        :param data:
        :param keys:
        :param class_hash:
        :return:
        """
        class_dispatcher = self.class_ids.get(class_hash[-8:])
        if class_dispatcher is None:
            return None

        if len(keys) == 0:
            raise InvalidCalldataError(
                "Events require at least 1 key parameter as the selector"
            )

        event_selector = keys.pop(0).to_bytes(length=32, byteorder="big")

        # These two should never fail if class_dispatcher is valid
        event_dispatcher = class_dispatcher.event_ids[event_selector[-8:]]
        event_type = self.event_types[event_dispatcher.decoder_reference]

        _data, _keys = data.copy(), keys.copy()
        decoded_data = decode_from_params(event_type[0], _data)

        if len(_data) > 0:
            raise InvalidCalldataError(
                f"Calldata Remaining after decoding event data {data} from {event_type[0]}"
            )

        return DecodedEvent(
            abi_name=class_dispatcher.abi_name,
            name=event_dispatcher.event_name,
            data=decoded_data,
        )
