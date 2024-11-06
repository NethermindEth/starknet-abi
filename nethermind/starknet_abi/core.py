import warnings
from dataclasses import dataclass
from typing import Any

from nethermind.starknet_abi.decoding_types import AbiEvent, AbiFunction, AbiInterface
from nethermind.starknet_abi.exceptions import InvalidAbiError
from nethermind.starknet_abi.parse import (
    group_abi_by_type,
    parse_abi_event,
    parse_abi_function,
    parse_enums_and_structs,
    topo_sort_type_defs,
)


@dataclass(slots=True)
class StarknetAbi:
    """
    Dataclass representation of a Starknet ABI
    """

    abi_name: str | None
    class_hash: bytes | None

    functions: dict[str, AbiFunction]
    events: dict[str, AbiEvent]

    constructor: AbiFunction | None
    l1_handler: AbiFunction | None

    implemented_interfaces: dict[str, AbiInterface]

    @classmethod
    def from_json(
        cls,
        abi_json: list[dict[str, Any]],
        class_hash: bytes | None = None,
        abi_name: str | None = None,
    ) -> "StarknetAbi":
        """
        Parse a StarknetABI From the JSON ABI of the class.

        :param abi_json:
        :param class_hash:
        :param abi_name:
        """
        grouped_abi = group_abi_by_type(abi_json)

        try:  # ABIs should already be topologically sorted
            defined_types = parse_enums_and_structs(grouped_abi["type_def"])
        except InvalidAbiError:
            sorted_defs = topo_sort_type_defs(grouped_abi["type_def"])
            defined_types = parse_enums_and_structs(sorted_defs)
            warnings.warn(
                "ABI Struct and Enum definitions out of order & required topological sorting"
            )

        # Interfaces
        defined_interfaces = [
            AbiInterface(
                name=interface["name"],
                functions=[parse_abi_function(func, defined_types) for func in interface["items"]],
            )
            for interface in grouped_abi["interface"]
        ]

        functions = {
            function["name"]: parse_abi_function(function, defined_types)
            for function in grouped_abi["function"]
        }

        for interface in defined_interfaces:
            functions.update({function.name: function for function in interface.functions})

        parsed_abi_events = [
            parse_abi_event(event, defined_types) for event in grouped_abi["event"]
        ]
        events = {event.name: event for event in parsed_abi_events if event is not None}

        if len(grouped_abi.get("constructor", [])) == 1:
            constructor = parse_abi_function(grouped_abi["constructor"][0], defined_types)
        else:
            constructor = None

        if len(grouped_abi.get("l1_handler", [])) == 1:
            l1_handler = parse_abi_function(grouped_abi["l1_handler"][0], defined_types)
        else:
            l1_handler = None

        implemented_interfaces = {
            interface.name: interface
            for interface in defined_interfaces
            if interface.name in [impl["interface_name"] for impl in grouped_abi["impl"]]
        }

        return StarknetAbi(
            abi_name=abi_name,
            class_hash=class_hash,
            functions=functions,
            events=events,
            constructor=constructor,
            l1_handler=l1_handler,
            implemented_interfaces=implemented_interfaces,
        )
