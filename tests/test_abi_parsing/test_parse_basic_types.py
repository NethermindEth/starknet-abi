from starknet_abi.abi_types import (
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
)
from starknet_abi.parse import _parse_type

EMPTY_STRUCT: dict[str, StarknetStruct | StarknetEnum] = {}


def test_parse_int_types():
    assert _parse_type("core::integer::u256", EMPTY_STRUCT) == StarknetCoreType.U256
    assert _parse_type("core::integer::u128", EMPTY_STRUCT) == StarknetCoreType.U128
    assert _parse_type("core::integer::u64", EMPTY_STRUCT) == StarknetCoreType.U64
    assert _parse_type("core::integer::u32", EMPTY_STRUCT) == StarknetCoreType.U32
    assert _parse_type("core::integer::u16", EMPTY_STRUCT) == StarknetCoreType.U16
    assert _parse_type("core::integer::u8", EMPTY_STRUCT) == StarknetCoreType.U8
    assert _parse_type("Uint256", EMPTY_STRUCT) == StarknetCoreType.U256


def test_parse_address_types():
    assert (
        _parse_type("core::starknet::contract_address::ContractAddress", EMPTY_STRUCT)
        == StarknetCoreType.ContractAddress
    )
    assert (
        _parse_type("core::starknet::class_hash::ClassHash", EMPTY_STRUCT)
        == StarknetCoreType.ClassHash
    )
    assert (
        _parse_type("core::starknet::eth_address::EthAddress", EMPTY_STRUCT)
        == StarknetCoreType.EthAddress
    )


def test_parse_felts():
    assert _parse_type("core::felt252", EMPTY_STRUCT) == StarknetCoreType.Felt


def test_parse_entry_point_felts():
    assert _parse_type("felt", EMPTY_STRUCT) == StarknetCoreType.Felt
    assert _parse_type("felt*", EMPTY_STRUCT) == StarknetArray(StarknetCoreType.Felt)


def test_parse_bool():
    assert _parse_type("core::bool", EMPTY_STRUCT) == StarknetCoreType.Bool


def test_parse_array():
    assert _parse_type(
        "core::array::Array::<core::integer::u256>", EMPTY_STRUCT
    ) == StarknetArray(StarknetCoreType.U256)
    assert _parse_type(
        "core::array::Array::<core::bool>", EMPTY_STRUCT
    ) == StarknetArray(StarknetCoreType.Bool)


def test_parse_option():
    assert _parse_type(
        "core::option::Option::<core::integer::u256>", EMPTY_STRUCT
    ) == StarknetOption(StarknetCoreType.U256)
    assert _parse_type(
        "core::option::Option::<core::bool>", EMPTY_STRUCT
    ) == StarknetOption(StarknetCoreType.Bool)
