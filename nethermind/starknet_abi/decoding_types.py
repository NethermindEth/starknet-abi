from dataclasses import dataclass
from typing import Any, Sequence

from nethermind.starknet_abi.abi_types import AbiParameter, StarknetType
from nethermind.starknet_abi.decode import decode_from_params, decode_from_types
from nethermind.starknet_abi.encode import encode_from_params
from nethermind.starknet_abi.exceptions import InvalidCalldataError, TypeDecodeError
from nethermind.starknet_abi.utils import starknet_keccak


@dataclass(slots=True)
class DecodedFunction:
    """
    Dataclass representing the result of decoding an ABI
    """

    abi_name: str | None
    name: str

    inputs: dict[str, Any]
    outputs: list[Any] | None


@dataclass(slots=True)
class DecodedEvent:
    """
    Dataclass representing the result of decoding an ABI Event
    """

    abi_name: str | None
    name: str

    data: dict[str, Any]


@dataclass(slots=True)
class AbiFunction:
    """
    Dataclass Representing an ABI Function.  Includes a function name, the function signature, and the input
    and output parameters.
    """

    name: str
    abi_name: str | None
    signature: bytes

    inputs: Sequence[AbiParameter]
    outputs: Sequence[StarknetType]

    def __init__(
        self,
        name: str,
        inputs: list[AbiParameter],
        outputs: list[StarknetType],
        abi_name: str | None = None,
    ):
        self.name = name
        self.abi_name = abi_name
        self.inputs = inputs
        self.outputs = outputs
        self.signature = starknet_keccak(self.name.encode())

    def id_str(self):
        """
        Returns a string representation of the ABI Function Types.  Functions with identical types & parameter names
        will have an identical id_str()

        .. doctest::

            >>> from nethermind.starknet_abi.decoding_types import AbiFunction
            >>> from nethermind.starknet_abi.abi_types import StarknetCoreType
            >>> add_function = AbiFunction(
            ...    name="add",
            ...    inputs=[AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
            ...    outputs=[StarknetCoreType.U64]
            ... )
            >>> add_function.id_str()
            'Function(a:U32,b:U32) -> (U64)'

        :return: Function(<parameters>) -> (<output-types>)
        """
        inputs_str = ",".join([param.id_str() for param in self.inputs])
        outputs_str = ",".join([output.id_str() for output in self.outputs])
        return f"Function({inputs_str}) -> ({outputs_str})"

    def decode(  # pylint: disable=line-too-long
        self,
        calldata: list[int],
        result: list[int] | None = None,
    ) -> DecodedFunction:
        """
        Decode the calldata and result of a function.

        .. doctest::

            >>> from nethermind.starknet_abi.decoding_types import AbiFunction
            >>> from nethermind.starknet_abi.abi_types import StarknetCoreType
            >>> add_function = AbiFunction(
            ...    name="add",
            ...    inputs=[AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
            ...    outputs=[StarknetCoreType.U64]
            ... )
            >>> add_function.decode([123456, 654321], [777777])
            DecodedFunction(abi_name=None, name='add', inputs={'a': 123456, 'b': 654321}, outputs=[777777])

        :param calldata:
        :param result:
        """
        _calldata = calldata.copy()
        decoded_inputs = decode_from_params(self.inputs, _calldata)

        if result:
            _result = result.copy()
            decoded_outputs = decode_from_types(self.outputs, _result)
        else:
            decoded_outputs = None

        return DecodedFunction(
            abi_name=self.abi_name,
            name=self.name,
            inputs=decoded_inputs,
            outputs=decoded_outputs,
        )

    def encode(
        self,
        inputs: dict[str, Any],
    ) -> list[int]:
        """
        Encode the inputs of a function into calldata.

        .. doctest::

            >>> from nethermind.starknet_abi.decoding_types import AbiFunction
            >>> from nethermind.starknet_abi.abi_types import StarknetCoreType, StarknetArray
            >>> add_function = AbiFunction(
            ...    name="add",
            ...    inputs=[AbiParameter("add_vals", StarknetArray(StarknetCoreType.U8))],
            ...    outputs=[StarknetCoreType.U128]
            ... )
            >>> add_function.encode({"add_vals": [122, 212, 221]})
            [3, 122, 212, 221]

        :param inputs: dict[function-param: value]
        :return: calldata array
        """

        return encode_from_params(self.inputs, inputs)


@dataclass(slots=True)
class AbiEvent:
    """
    Dataclass representing an ABI Event.  Includes an event name, the event signature, and the data parameters.
    """

    name: str
    abi_name: str | None
    signature: bytes

    parameters: list[str]
    keys: dict[str, StarknetType]
    data: dict[str, StarknetType]

    def __init__(
        self,
        name: str,
        parameters: list[str],
        data: dict[str, StarknetType],
        keys: dict[str, StarknetType] | None = None,
        abi_name: str | None = None,
    ):
        self.name = name
        self.data = data
        self.parameters = parameters
        self.keys = keys or {}
        self.abi_name = abi_name
        self.signature = starknet_keccak(self.name.encode())

    def id_str(self):
        """
        Returns a string representation of the ABI Function.

        .. doctest::

            >>> from nethermind.starknet_abi.decoding_types import AbiEvent
            >>> from nethermind.starknet_abi.abi_types import StarknetCoreType
            >>> add_event = AbiEvent(
            ...     name="Create",
            ...     parameters=["address"],
            ...     data={"address": StarknetCoreType.ContractAddress},
            ... )
            >>> add_event.id_str()
            'Event(address:ContractAddress)'

        :return: Event(<data keys>)
        """
        event_params = []
        for param in self.parameters:
            if param in self.data:
                event_params.append(f"{param}:{self.data[param].id_str()}")
            elif param in self.keys:
                event_params.append(f"<{param}>:{self.keys[param].id_str()}")
            else:
                raise TypeDecodeError(f"Event Parameter {param} not part of event keys or Data")

        return f"Event({','.join(event_params)})"

    def decode(self, data: list[int], keys: list[int]) -> DecodedEvent:
        """
        Decode the keys and data of an event.

        :param data: Data array for decoding
        :param keys: Optional data array of event keys
        :return: DecodedEvent
        """

        _data = data.copy()
        _keys = keys[1:].copy()  # Key[0] is the event signature

        decoded_data = {}

        for param in self.parameters:
            if param in self.data:
                decoded_data.update({param: decode_from_types([self.data[param]], _data)[0]})
            elif param in self.keys:
                decoded_data.update({param: decode_from_types([self.keys[param]], _keys)[0]})
            else:
                raise TypeDecodeError(
                    f"Event Parameter {param} not present in Keys or Data for Event {self.name}"
                )

        if len(_data) != 0 or len(_keys) != 0:
            raise InvalidCalldataError(
                f"Calldata Not Completely Consumed decoding Event: {self.id_str()}"
            )

        return DecodedEvent(abi_name=self.abi_name, name=self.name, data=decoded_data)


@dataclass(slots=True)
class AbiInterface:
    """
    Dataclass Representing an ABI Interface.  Includes a name and a list of functions.
    """

    name: str
    functions: Sequence[AbiFunction]
