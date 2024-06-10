import re
from collections import defaultdict
from graphlib import TopologicalSorter
from typing import Any

from nethermind.starknet_abi.abi_types import (
    AbiMemberType,
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
    StarknetType,
)
from nethermind.starknet_abi.decoding_types import AbiEvent, AbiFunction
from nethermind.starknet_abi.exceptions import InvalidAbiError


def group_abi_by_type(abi_json: list[dict]) -> defaultdict[AbiMemberType, list[dict]]:
    """
    Groups ABI JSON by ABI Type.  If type is 'struct' or 'enum', it is grouped as a 'type_def'

    :return:
    """
    grouped: defaultdict[AbiMemberType, list[dict]] = defaultdict(list)

    for entry in abi_json:
        assert isinstance(entry, dict)
        if entry["type"] in ["struct", "enum"]:
            grouped["type_def"].append(entry)
        else:
            grouped[entry["type"]].append(entry)
    return grouped


# Non-Struct Defined Types
# Used for Topological Sorting abi struct and enum definitions of incorrectly ordered abis
STARKNET_CORE_TYPES = {
    "felt",  # Old Syntax for core::felt252
    "felt*",  # Old Syntax for arrays
    "core::integer::u128",
    "core::integer::u64",
    "core::integer::u32",
    "core::integer::u16",
    "core::integer::u8",
    "core::felt252",
    "core::bool",
    "core::starknet::contract_address::ContractAddress",
    "core::starknet::class_hash::ClassHash",
    "core::starknet::eth_address::EthAddress",
}


def _build_type_graph(type_defs: list[dict]) -> dict[str, set[str]]:
    output_graph = {}

    for type_def in type_defs:
        referenced_types = [
            member["type"]
            for member in (
                type_def["members"]
                if type_def["type"] == "struct"
                else type_def["variants"]
            )
        ]

        output_graph.update(
            {type_def["name"]: set(referenced_types) - STARKNET_CORE_TYPES}
        )

    return output_graph


def topo_sort_type_defs(type_defs: list[dict]) -> list[dict]:
    """
    Topographically sorts Struct and Enum definitions.  If ABI Parsing fails.

    Since most StarknetABIs are already sorted, the parser optimistically runs through the ABI, and if an error
    occurs, the Enum and Struct definitions are sorted before re-parsing.  If this second attempt at parsing fails,
    it raises a detailed error message with the ABI Type that is not defined.

    :param type_defs:
    :return:
    """
    type_graph = _build_type_graph(type_defs)
    sorted_defs = TopologicalSorter(type_graph).static_order()

    try:
        sorted_type_def_json = []
        for sorted_type_name in sorted_defs:
            abi_definition = [
                type_def
                for type_def in type_defs
                if type_def["name"] == sorted_type_name
            ]
            # fmt: off
            assert len(abi_definition) != 0, f"Type {sorted_type_name} not defined in ABI"
            assert len(abi_definition) == 1, f"Type {sorted_type_name} defined multiple times in ABI"
            # fmt: on

            sorted_type_def_json.append(abi_definition[0])

        return sorted_type_def_json

    except AssertionError as assert_err_message:
        raise InvalidAbiError(assert_err_message)  # pylint: disable=raise-missing-from


def parse_enums_and_structs(
    abi_structs: list[dict],
) -> dict[str, StarknetStruct | StarknetEnum]:
    """
    Parses an **ordered** array of ABI structs into a dictionary of StarknetStructs, mapping struct name to struct.

    :param abi_structs:
    :return:
    """

    output_types: dict[str, StarknetStruct | StarknetEnum] = {}
    for struct in abi_structs:
        type_name = struct["name"]

        match type_name.split("::"):
            case ["Uint256"]:  # Old Syntax
                continue
            case ["core", "array" | "integer" | "bool" | "option", *_]:
                # Automatically parses Array/Span, u256, bool, and Option types as StarknetCoreType
                continue

            # Can Hard code in structs like openzeppelin's ERC20 & Events for faster parsing

        match struct["type"]:
            case "struct":
                output_types.update({type_name: _parse_struct(struct, output_types)})

            case "enum":
                output_types.update({type_name: _parse_enum(struct, output_types)})
    return output_types


def _parse_struct(
    abi_struct: dict, type_context: dict[str, StarknetStruct | StarknetEnum]
):
    return StarknetStruct(
        name=abi_struct["name"],
        members=[
            AbiParameter(
                name=member["name"], type=_parse_type(member["type"], type_context)
            )
            for member in abi_struct["members"]
        ],
    )


def _parse_enum(
    abi_enum: dict, type_context: dict[str, StarknetStruct | StarknetEnum]
) -> StarknetEnum:
    return StarknetEnum(
        name=abi_enum["name"],
        variants=[
            (variant["name"], _parse_type(variant["type"], type_context))
            for variant in abi_enum["variants"]
        ],
    )


def _parse_tuple(
    abi_type: str, custom_types: dict[str, StarknetStruct | StarknetEnum]
) -> StarknetTuple:
    """

    :param abi_type:
    :param custom_types:
    :return:
    """

    def _is_named_tuple(type_str):
        match = re.search(r"(?<!:):(?!:)", type_str)
        if match:
            return match.start()
        # If no match is found, return -1
        return False

    # Remove Outer Parentheses & Whitespace
    stripped_tuple = abi_type[1:-1].replace(" ", "")

    output_types = []
    parenthesis_cache = []  # Tracks tuple opens and closes
    type_cache = []  # Tracks contents for sub-tuples

    for type_string in stripped_tuple.split(","):
        # There are no single item tuples, so there should either be close or open tuples
        # in the split type string, but not both
        tuple_open = type_string.count("(")
        tuple_close = type_string.count(")")

        if tuple_open:
            parenthesis_cache.extend(["(" for _ in range(tuple_open)])

        if parenthesis_cache:  # Currently Parsing Types inside Nested Tuple
            type_cache.append(type_string)
        else:  # Append Types To Root Tuple
            if _is_named_tuple(type_string):
                output_types.append(
                    _parse_type(
                        type_string[_is_named_tuple(type_string) + 1 :], custom_types
                    )
                )
            else:
                output_types.append(_parse_type(type_string, custom_types))

        if tuple_close:
            for _ in range(tuple_close):
                parenthesis_cache.pop(-1)

            if len(parenthesis_cache) == 0:
                # Final tuple close detected, add new tuple to output types
                output_types.append(_parse_tuple(",".join(type_cache), custom_types))

    return StarknetTuple(output_types)


def extract_inner_type(abi_type: str) -> str:
    """
    Extracts the inner type from a type string

    .. doctest::
        >>> from nethermind.starknet_abi.parse import extract_inner_type
        >>> extract_inner_type("core::array::Array::<core::integer::u256>")
        'core::integer::u256'

        >>> extract_inner_type("core::array::Array::<core::option::Option::<core::felt252>>")
        'core::option::Option::<core::felt252>'
    """

    return abi_type[abi_type.find("<") + 1 : abi_type.rfind(">")]


def _parse_type(  # pylint: disable=too-many-return-statements
    abi_type: str, custom_types: dict[str, StarknetStruct | StarknetEnum]
) -> StarknetType:
    if abi_type == "()":
        return StarknetCoreType.NoneType

    if abi_type.startswith("("):
        return _parse_tuple(abi_type, custom_types)

    match abi_type.split("::")[1:]:
        case ["integer", integer_type]:  # 'core::integer::<int_type>'
            return StarknetCoreType.int_from_string(integer_type)

        case ["felt252"]:  # 'core::felt252'
            return StarknetCoreType.Felt

        case ["bool"]:  # 'core::bool'
            return StarknetCoreType.Bool

        # 'core::starknet::contract_address::ContractAddress'
        case ["starknet", "contract_address", "ContractAddress"]:
            return StarknetCoreType.ContractAddress

        # 'core::starknet::class_hash::ClassHash'
        case ["starknet", "class_hash", "ClassHash"]:
            return StarknetCoreType.ClassHash

        # 'core::starknet::eth_address::EthAddress'
        case ["starknet", "eth_address", "EthAddress"]:
            return StarknetCoreType.EthAddress

        case ["bytes_31", "bytes31"]:
            return StarknetCoreType.Bytes31

        case ["starknet", "storage_access", "StorageAddress"]:
            return StarknetCoreType.StorageAddress

        ############################################################
        #  Complex Types: Structs, Arrays, etc.
        ############################################################

        # Matches 'core::array::Array | Span::*'
        case ["array", "Array" | "Span", *_]:
            return StarknetArray(
                _parse_type(extract_inner_type(abi_type), custom_types)
            )

        # Matches 'core::option::Option::*'
        case ["option", "Option", *_]:
            return StarknetOption(
                _parse_type(extract_inner_type(abi_type), custom_types)
            )

        case _:
            # If unknown type is defined in struct context, return struct
            if abi_type in custom_types:
                return custom_types[abi_type]

            # Fallback for rarely encountered types
            if abi_type == "felt":  # Only present in L1 Handler ABIs?
                return StarknetCoreType.Felt
            if abi_type.endswith("*"):  # Old Syntax for Arrays
                return StarknetArray(_parse_type(abi_type[:-1], custom_types))
            if abi_type == "Uint256":  # Only present in L1 Handler ABIs?
                return StarknetCoreType.U256

            raise InvalidAbiError(f"Invalid ABI Type: {abi_type}")


def parse_abi_parameters(
    names: list[str],
    types: list[str],
    custom_types: dict[str, StarknetStruct | StarknetEnum],
):
    """
    Parses ABIs with wildcard syntax.  If felt* is detected, it is parsed as an array of Felt, and the felt_len
    parameter is omitted from the parsed type
    """
    output_parameters: list[AbiParameter] = []

    for name, json_type_str in zip(names, types, strict=True):
        if json_type_str.endswith("*"):
            len_param = output_parameters.pop(-1)
            assert len_param.name.endswith(
                ("_len", "_size")
            ), f"Type {json_type_str} not preceded by a length parameter"

        output_parameters.append(
            AbiParameter(
                name=name,
                type=_parse_type(json_type_str, custom_types),
            )
        )

    return output_parameters


def parse_abi_types(
    types: list[str],
    custom_types: dict[str, StarknetStruct | StarknetEnum],
):
    """
    Parses a list of ABI types into StarknetTypes while maintaining wildcard syntax definitions.
    """
    output_types: list[StarknetType] = []

    for json_type_str in types:
        if json_type_str.endswith("*"):
            len_type = output_types.pop(-1)
            assert (
                len_type == StarknetCoreType.Felt
            ), f"Type {json_type_str} not preceded by a Felt Length Param"

        output_types.append(_parse_type(json_type_str, custom_types))

    return output_types


def parse_abi_function(
    abi_function: dict[str, Any],
    custom_types: dict[str, StarknetStruct | StarknetEnum],
) -> AbiFunction:
    """
    Parses JSON Representation of a Function into an AbiFunction object.

    :param abi_function:
    :param custom_types:
    :return:
    """

    parsed_inputs = parse_abi_parameters(
        names=[abi_input["name"] for abi_input in abi_function["inputs"]],
        types=[abi_input["type"] for abi_input in abi_function["inputs"]],
        custom_types=custom_types,
    )
    parsed_outputs = parse_abi_types(
        types=[abi_output["type"] for abi_output in abi_function["outputs"]],
        custom_types=custom_types,
    )

    return AbiFunction(
        name=abi_function["name"],
        inputs=parsed_inputs,
        outputs=parsed_outputs,
    )


def parse_abi_event(
    abi_event: dict[str, Any],
    custom_types: dict[str, StarknetStruct | StarknetEnum],
) -> AbiEvent | None:
    """
    Parses JSON Representation of an Event into an AbiEvent object.

    :param abi_event:
    :param custom_types:
    :return:
    """
    if "kind" in abi_event:  # Version 2 Abi
        if abi_event["kind"] == "struct":
            event_parameters = abi_event["members"]
        else:
            return None

    elif "inputs" in abi_event:  # Version 1 Abi
        event_parameters = abi_event["inputs"]

    elif "data" in abi_event:
        event_parameters = abi_event["data"]
    else:
        return None

    parsed_data = parse_abi_parameters(
        names=[abi_input["name"] for abi_input in event_parameters],
        types=[abi_input["type"] for abi_input in event_parameters],
        custom_types=custom_types,
    )

    return AbiEvent(
        name=abi_event["name"],
        data=parsed_data,
    )


# ---- Notes ----
# When the event is emitted, the serialization to keys and data happens as follows:

#   Since the TestEnum variant has kind nested, add the first key: sn_keccak(TestEnum),
#   and the rest of the serialization to keys and data is done recursively via
#   the starknet::event trait implementation of MyEnum.

#   Next, you can handle a "kind": "nested" variant (previously it was TestEnum, now it’s Var1),
#   which means you can add another key depending on the sub-variant: sn_keccak(Var1), and proceed
#   to serialize according to the starknet::event implementation of MyStruct.
#
#   Finally, proceed to serialize MyStruct, which gives us a single data member.
#
#   This results in keys = [sn_keccak(TestEnum), sn_keccak(Var1)] and data=[5]
