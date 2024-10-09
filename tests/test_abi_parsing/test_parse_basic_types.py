from nethermind.starknet_abi.abi_types import (
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
)
from nethermind.starknet_abi.parse import _parse_type
from nethermind.starknet_abi.utils import starknet_keccak

EMPTY_STRUCT: dict[str, StarknetStruct | StarknetEnum] = {}


def test_parse_int_types():
    assert _parse_type("core::integer::u128", EMPTY_STRUCT) == StarknetCoreType.U128
    assert _parse_type("core::integer::u64", EMPTY_STRUCT) == StarknetCoreType.U64
    assert _parse_type("core::integer::u32", EMPTY_STRUCT) == StarknetCoreType.U32
    assert _parse_type("core::integer::u16", EMPTY_STRUCT) == StarknetCoreType.U16
    assert _parse_type("core::integer::u8", EMPTY_STRUCT) == StarknetCoreType.U8

    assert _parse_type("core::integer::i8", EMPTY_STRUCT) == StarknetCoreType.I8
    assert _parse_type("core::integer::i16", EMPTY_STRUCT) == StarknetCoreType.I16
    assert _parse_type("core::integer::i32", EMPTY_STRUCT) == StarknetCoreType.I32
    assert _parse_type("core::integer::i64", EMPTY_STRUCT) == StarknetCoreType.I64
    assert _parse_type("core::integer::i128", EMPTY_STRUCT) == StarknetCoreType.I128

    assert _parse_type("Uint256", EMPTY_STRUCT) == StarknetCoreType.U256
    assert _parse_type("core::integer::u256", EMPTY_STRUCT) == StarknetCoreType.U256
    assert _parse_type("core::integer::u512", EMPTY_STRUCT) == StarknetCoreType.U512


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
    assert (
        _parse_type("core::starknet::storage_access::StorageAddress", EMPTY_STRUCT)
        == StarknetCoreType.StorageAddress
    )
    assert _parse_type("core::bytes_31::bytes31", EMPTY_STRUCT) == StarknetCoreType.Bytes31


def test_parse_felts():
    assert _parse_type("core::felt252", EMPTY_STRUCT) == StarknetCoreType.Felt


def test_parse_entry_point_felts():
    assert _parse_type("felt", EMPTY_STRUCT) == StarknetCoreType.Felt
    assert _parse_type("felt*", EMPTY_STRUCT) == StarknetArray(StarknetCoreType.Felt)


def test_parse_bool():
    assert _parse_type("core::bool", EMPTY_STRUCT) == StarknetCoreType.Bool


def test_parse_array():
    assert _parse_type("core::array::Array::<core::integer::u256>", EMPTY_STRUCT) == StarknetArray(
        StarknetCoreType.U256
    )
    assert _parse_type("core::array::Array::<core::bool>", EMPTY_STRUCT) == StarknetArray(
        StarknetCoreType.Bool
    )

    assert _parse_type(
        "core::array::Array::<core::bytes_31::bytes31>", EMPTY_STRUCT
    ) == StarknetArray(StarknetCoreType.Bytes31)


def test_parse_option():
    assert _parse_type(
        "core::option::Option::<core::integer::u256>", EMPTY_STRUCT
    ) == StarknetOption(StarknetCoreType.U256)
    assert _parse_type("core::option::Option::<core::bool>", EMPTY_STRUCT) == StarknetOption(
        StarknetCoreType.Bool
    )


def test_legacy_types():
    assert _parse_type("(x: felt, y: felt)", EMPTY_STRUCT) == StarknetTuple(
        [StarknetCoreType.Felt, StarknetCoreType.Felt]
    )


def test_parse_storage_address():
    assert (
        _parse_type("core::starknet::storage_access::StorageAddress", EMPTY_STRUCT)
        == StarknetCoreType.StorageAddress
    )


def test_parse_bytes():
    assert _parse_type("core::bytes_31::bytes31", EMPTY_STRUCT) == StarknetCoreType.Bytes31
