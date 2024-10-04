import graphlib
import re
from collections import defaultdict
from typing import Any

from nethermind.starknet_abi.abi_types import (
    AbiMemberType,
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetNonZero,
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
    "core::integer::usize",
    "core::integer::u16",
    "core::integer::u8",
    "core::integer::i128",
    "core::integer::i64",
    "core::integer::i32",
    "core::integer::i16",
    "core::integer::i8",
    "core::felt252",
    "core::bool",
    "core::bytes_31::bytes31",
    "core::starknet::storage_access::StorageAddress",
    "core::starknet::contract_address::ContractAddress",
    "core::starknet::class_hash::ClassHash",
    "core::starknet::eth_address::EthAddress",
}


def _build_type_graph(type_defs: list[dict]) -> dict[str, set[str]]:
    output_graph = {}

    for type_def in type_defs:
        referenced_types: list[str] = [
            member["type"]
            for member in (
                type_def["members"]
                if type_def["type"] == "struct"
                else type_def["variants"]
            )
        ]

        ref_types = set()
        for type_str in referenced_types:
            if type_str in STARKNET_CORE_TYPES:
                continue

            if type_str.startswith(("core::array", "@core::array")):  # Handle Arrays
                if extract_inner_type(type_str) not in STARKNET_CORE_TYPES:
                    ref_types.add(
                        extract_inner_type(type_str)
                    )  # Add inner type of array as dependency

                continue  # If inner type of array in core types, continue

            if type_str.startswith("("):
                tuple_vals = _extract_tuple_types(type_str)
                tuple_ref_types = _flatten_tuple_types(tuple_vals)

                ref_types.update(tuple_ref_types - STARKNET_CORE_TYPES)

            ref_types.add(type_str)

        output_graph.update({type_def["name"]: ref_types})

    return output_graph


def topo_sort_type_defs(type_defs: list[dict]) -> list[dict]:
    """
    Topographically sorts Struct and Enum definitions.  If ABI Parsing fails.

    Since most StarknetABIs are already sorted, the parser optimistically runs through the ABI, and if an error
    occurs, the Enum and Struct definitions are sorted before re-parsing.  If this second attempt at parsing fails,
    it raises a detailed error message with the ABI Type that is not defined.

    :param type_defs:
    """
    type_graph = _build_type_graph(type_defs)

    try:
        sorted_defs = graphlib.TopologicalSorter(type_graph).static_order()
        sorted_defs = list(
            sorted_defs
        )  # Unwrap iterator into list to catch any CycleErrors
    except graphlib.CycleError as e:
        error_str = str(e).replace("('nodes are in a cycle', ", "")
        raise InvalidAbiError(  # pylint: disable=raise-missing-from
            f"Cyclic Struct Dependencies in ABI: {error_str[:-1]}"
        )

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
    """

    output_types: dict[str, StarknetStruct | StarknetEnum] = {}
    for struct in abi_structs:
        type_name = struct["name"]

        match type_name.split("::"):
            case ["Uint256"]:  # Old Syntax
                continue
            case [
                "core" | "@core",
                "array" | "integer" | "bool" | "option" | "zeroable",
                *_,
            ]:
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


def _extract_tuple_types(tuple_abi_type: str) -> list[str | list[Any]]:
    """
    Parse a tuple type string into a nested structure of the tuple types.  Needs to be able to handle
    nested tuples, as well as named tuples

    .. doctest::
        >>> from nethermind.starknet_abi.parse import _extract_tuple_types
        >>> _extract_tuple_types("(core::integer::u64, core::integer::i128)")
        ['core::integer::u64', 'core::integer::i128']
        >>> _extract_tuple_types("(core::integer::u64, (core::integer::u16, core::integer::u16))")
        ['core::integer::u64', ['core::integer::u16', 'core::integer::u16']]
    """
    # Begin the spaghetti...

    def _is_named_tuple(type_str):
        match = re.search(r"(?<!:):(?!:)", type_str)
        if match:
            return match.start()
        # If no match is found, return -1
        return False

    # Remove Outer Parentheses & Whitespace
    stripped_tuple = tuple_abi_type[1:-1].replace(" ", "")

    output_types: list[str | list[Any]] = []
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
            output_types.append(
                type_string
                if not _is_named_tuple(type_string)
                else type_string[_is_named_tuple(type_string) + 1 :]
            )

        if tuple_close:
            for _ in range(tuple_close):
                parenthesis_cache.pop(-1)

            if len(parenthesis_cache) == 0:
                # Final tuple close detected, add new tuple to output types
                output_types.append(_extract_tuple_types(",".join(type_cache)))

    return output_types


def _flatten_tuple_types(tuple_types: list[str | list]) -> set[str]:
    """
    Flatten a nested list of tuple datatypes into a set of abi datatypes.

    .. doctest::
        >>> from nethermind.starknet_abi.parse import _flatten_tuple_types
        >>> sorted(_flatten_tuple_types(["core::bool", "core::integer::u8", ["core::bool", "core::felt252"]]))
        ['core::bool', 'core::felt252', 'core::integer::u8']
    """
    output = set()
    for type_ in tuple_types:
        if isinstance(type_, list):
            output.update(_flatten_tuple_types(type_))
        else:
            output.add(type_)

    return output


def _parse_tuple(
    abi_type: str, custom_types: dict[str, StarknetStruct | StarknetEnum]
) -> StarknetTuple:
    """
    :param abi_type:  ABI type string
    :param custom_types:  Custom Struct Definitions for ABI

    .. doctest::
        >>> from nethermind.starknet_abi.parse import _parse_tuple
        >>> _parse_tuple("(core::integer::u64, core::integer::i128)", {})
        StarknetTuple(members=[StarknetCoreType.U64, StarknetCoreType.I128])

        >>> _parse_tuple("((core::array::Array::<core::integer::u8>, core::integer::u64), core::felt252)", {})
        StarknetTuple(members=[StarknetTuple(members=[StarknetArray(inner_type=StarknetCoreType.U8), StarknetCoreType.U64]), StarknetCoreType.Felt])
    """

    def _parse_tuple_types(types: list[str | list]) -> list[StarknetType]:
        output = []

        for type_ in types:
            if isinstance(type_, str):
                output.append(_parse_type(type_, custom_types))
            if isinstance(type_, list):
                output.append(StarknetTuple(_parse_tuple_types(type_)))

        return output

    tuple_type_strings = _extract_tuple_types(abi_type)

    return StarknetTuple(_parse_tuple_types(tuple_type_strings))


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

        case ["zeroable", "NonZero", *_]:
            return StarknetNonZero(
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
    """
    if "kind" in abi_event:  # Version 2 Abi
        if abi_event["kind"] == "struct":
            event_parameters = abi_event["members"]
        else:
            return None

    elif "inputs" in abi_event:  # Version 0 Abi
        # Inputs cannot be indexed and are treated as data
        event_parameters = [{"kind": "data", **e} for e in abi_event["inputs"]]

    elif "data" in abi_event:  # Version 1 Abi
        event_parameters = [{"kind": "key", **e} for e in abi_event["keys"]]
        event_parameters.extend([{"kind": "data", **e} for e in abi_event["data"]])
    else:
        return None

    decoded_params = parse_abi_parameters(
        types=[e["type"] for e in event_parameters],
        names=[e["name"] for e in event_parameters],
        custom_types=custom_types,
    )

    event_kinds = {
        abi_input["name"]: abi_input["kind"] for abi_input in event_parameters
    }
    event_data = {
        param.name: param.type
        for param in decoded_params
        if event_kinds[param.name] == "data"
    }
    event_keys = {
        param.name: param.type
        for param in decoded_params
        if event_kinds[param.name] == "key"
    }

    return AbiEvent(
        name=abi_event["name"].split("::")[-1],
        parameters=[param.name for param in decoded_params],
        data=event_data,
        keys=event_keys,
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
