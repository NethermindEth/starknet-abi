from graphlib import TopologicalSorter

from starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
)
from starknet_abi.parse import (
    _build_type_graph,
    _parse_struct,
    _parse_tuple,
    group_abi_by_type,
    parse_enums_and_structs,
    topo_sort_type_defs,
)
from tests.utils import load_abi

ETH_ABI_JSON = load_abi("starknet_eth.json", 2)
ARGENT_ACCOUNT_ABI = load_abi("argent_account.json", 2)


def test_struct_ordering():
    # Structs are ordered in ABI Definitions to ensure that they are defined before they are used.
    # Parser is dependent on correct ordering
    # This test ensures that the default group_abi_by_type() maintains the definition order for

    grouped_abi = group_abi_by_type(ETH_ABI_JSON)

    structs = grouped_abi["type_def"]

    assert structs[0]["name"] == "core::integer::u256"
    assert structs[0]["type"] == "struct"

    assert structs[1]["name"] == "core::array::Span::<core::felt252>"
    assert structs[1]["type"] == "struct"

    assert structs[2]["name"] == "src::replaceability_interface::EICData"
    assert structs[2]["type"] == "struct"

    assert (
        structs[3]["name"]
        == "core::option::Option::<src::replaceability_interface::EICData>"
    )
    assert structs[3]["type"] == "enum"

    assert structs[4]["name"] == "core::bool"
    assert structs[4]["type"] == "enum"

    assert structs[5]["name"] == "src::replaceability_interface::ImplementationData"
    assert structs[5]["type"] == "struct"


def test_exclude_common_structs_and_enums():
    grouped_abi = group_abi_by_type(ETH_ABI_JSON)

    struct_dict = parse_enums_and_structs(grouped_abi["type_def"])

    assert len(struct_dict) == 2

    expected_eic_data_struct = StarknetStruct(
        name="src::replaceability_interface::EICData",
        members=[
            AbiParameter(name="eic_hash", type=StarknetCoreType.ClassHash),
            AbiParameter(
                name="eic_init_data", type=StarknetArray(StarknetCoreType.Felt)
            ),
        ],
    )
    assert (
        struct_dict["src::replaceability_interface::EICData"]
        == expected_eic_data_struct
    )
    assert struct_dict[
        "src::replaceability_interface::ImplementationData"
    ] == StarknetStruct(
        name="src::replaceability_interface::ImplementationData",
        members=[
            AbiParameter(name="impl_hash", type=StarknetCoreType.ClassHash),
            AbiParameter(
                name="eic_data", type=StarknetOption(expected_eic_data_struct)
            ),
            AbiParameter(name="final", type=StarknetCoreType.Bool),
        ],
    )


def test_enum_parsing():
    grouped_abi = group_abi_by_type(ARGENT_ACCOUNT_ABI)

    type_dict = parse_enums_and_structs(grouped_abi["type_def"])

    assert len(type_dict) == 5

    assert type_dict["account::escape::EscapeStatus"] == StarknetEnum(
        name="account::escape::EscapeStatus",
        variants=[
            ("None", StarknetCoreType.NoneType),
            ("NotReady", StarknetCoreType.NoneType),
            ("Ready", StarknetCoreType.NoneType),
            ("Expired", StarknetCoreType.NoneType),
        ],
    )


def test_tuple_parsing():
    single_tuple = _parse_tuple("(core::felt252, core::bool)", {})

    nested_tuple_1 = _parse_tuple(
        "(core::felt252, (core::bool, core::integer::u256))", {}
    )
    nested_tuple_2 = _parse_tuple(
        "(core::felt252, ((core::integer::u16, core::integer::u32), core::bool), core::integer::u256)",
        {},
    )

    assert single_tuple == StarknetTuple([StarknetCoreType.Felt, StarknetCoreType.Bool])

    assert nested_tuple_1 == StarknetTuple(
        [
            StarknetCoreType.Felt,
            StarknetTuple([StarknetCoreType.Bool, StarknetCoreType.U256]),
        ]
    )

    assert nested_tuple_2 == StarknetTuple(
        [
            StarknetCoreType.Felt,
            StarknetTuple(
                [
                    StarknetTuple([StarknetCoreType.U16, StarknetCoreType.U32]),
                    StarknetCoreType.Bool,
                ]
            ),
            StarknetCoreType.U256,
        ]
    )


# fmt: off
UNORDERED_STRUCTS = [
    {'type': 'struct', 'name': 'betting::betting::Bet', 'members': [
        {'name': 'expire_timestamp', 'type': 'core::integer::u64'},
        {'name': 'bettor', 'type': 'betting::betting::UserData'},
        {'name': 'counter_bettor', 'type': 'betting::betting::UserData'},
        {'name': 'amount', 'type': 'core::integer::u256'},
    ]},
    {'type': 'struct', 'name': 'betting::betting::UserData', 'members': [
        {'name': 'address', 'type': 'core::starknet::contract_address::ContractAddress'},
        {'name': 'total_assets', 'type': 'core::integer::u256'},
    ]},
    {"type": "struct", "name": "core::integer::u256", "members": [
        {"name": "low", "type": "core::integer::u128"},
        {"name": "high", "type": "core::integer::u128"}
    ]},
]

# fmt: on


def test_build_type_graph():
    type_graph = _build_type_graph(UNORDERED_STRUCTS)

    assert type_graph == {
        "betting::betting::Bet": {"betting::betting::UserData", "core::integer::u256"},
        "betting::betting::UserData": {"core::integer::u256"},
        "core::integer::u256": set(),
    }

    assert list(TopologicalSorter(type_graph).static_order()) == [
        "core::integer::u256",
        "betting::betting::UserData",
        "betting::betting::Bet",
    ]


def test_struct_topo_sorting():
    topo_sorted_type_defs = topo_sort_type_defs(UNORDERED_STRUCTS)

    # fmt: off
    assert topo_sorted_type_defs == [
        {"type": "struct", "name": "core::integer::u256", "members": [
            {"name": "low", "type": "core::integer::u128"},
            {"name": "high", "type": "core::integer::u128"}
        ]},
        {'type': 'struct', 'name': 'betting::betting::UserData', 'members': [
            {'name': 'address', 'type': 'core::starknet::contract_address::ContractAddress'},
            {'name': 'total_assets', 'type': 'core::integer::u256'},
        ]},
        {'type': 'struct', 'name': 'betting::betting::Bet', 'members': [
            {'name': 'expire_timestamp', 'type': 'core::integer::u64'},
            {'name': 'bettor', 'type': 'betting::betting::UserData'},
            {'name': 'counter_bettor', 'type': 'betting::betting::UserData'},
            {'name': 'amount', 'type': 'core::integer::u256'},
        ]},
    ]
    # fmt: on
