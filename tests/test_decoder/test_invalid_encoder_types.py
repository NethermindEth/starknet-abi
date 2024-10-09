import pytest

from nethermind.starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetStruct,
)
from nethermind.starknet_abi.decode import decode_from_types
from nethermind.starknet_abi.encode import encode_from_types
from nethermind.starknet_abi.exceptions import (
    InvalidCalldataError,
    TypeDecodeError,
    TypeEncodeError,
)

test_enum = StarknetEnum(
    name="TestEnum",
    variants=[
        ("a", StarknetCoreType.U256),
        ("b", StarknetCoreType.U64),
        ("c", StarknetCoreType.Bool),
    ],
)
MAX_U128 = 2 << 128 - 1

raw_uint_struct = StarknetStruct(
    name="CustomUint256",
    members=[
        AbiParameter("low", StarknetCoreType.U128),
        AbiParameter("high", StarknetCoreType.U128),
    ],
)


def test_encode_invalid_enums_raises():
    error_message = "Enum Value (.*?) must have exactly one key-value pair"
    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([test_enum], [{"a": 100, "b": 200}])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([test_enum], [{}])


def test_encode_invalid_felts():
    error_message = "\\d+ Does not Fit into Starknet Felt"
    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([StarknetCoreType.Felt], [StarknetCoreType.Felt.max_value() + 1])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types(
            [StarknetCoreType.ContractAddress],
            [StarknetCoreType.ContractAddress.max_value() + 1],
        )

    with pytest.raises(TypeEncodeError, match="\\d+ Is larger than an Eth Address"):
        encode_from_types(
            [StarknetCoreType.EthAddress],
            [0x0123456789012345678901234567890123456789012],
        )


def test_decode_extra_calldata():
    with pytest.raises(
        InvalidCalldataError,
        match="Not Enough Calldata to decode StarknetCoreType.U256",
    ):
        decode_from_types([StarknetCoreType.U8, StarknetCoreType.U256], [123, 0])


def test_decode_invalid_uint_values():
    low_error_message = "Could not decode StarknetCoreType.U256: Low Exceeds U128 Range"
    high_error_message = "Could not decode StarknetCoreType.U256: High Exceeds U128 Range"

    with pytest.raises(TypeDecodeError, match=low_error_message):
        decode_from_types([StarknetCoreType.U256], [MAX_U128 + 1, 0])

    with pytest.raises(TypeDecodeError, match=low_error_message):
        decode_from_types([StarknetCoreType.U256], [MAX_U128 + 1, MAX_U128 + 1])

    with pytest.raises(TypeDecodeError, match=low_error_message):
        decode_from_types([StarknetCoreType.U256], [-1, 0])

    with pytest.raises(TypeDecodeError, match=high_error_message):
        decode_from_types([StarknetCoreType.U256], [0, MAX_U128 + 1])

    with pytest.raises(TypeDecodeError, match=high_error_message):
        decode_from_types([StarknetCoreType.U256], [0, -1])


def test_encode_invalid_int_value():
    error_message = "Integer (.*?) is out of range for StarknetCoreType."

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([StarknetCoreType.U256], [2**256])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([StarknetCoreType.U128], [-1])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([StarknetCoreType.U64], [2**64])


def test_encode_invalid_dict_values():
    error_message = "Failed to Encode (.*?) to StarknetStruct"

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([raw_uint_struct], [{"low": -1, "high": 12324}])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([raw_uint_struct], [{"low": MAX_U128 + 1, "high": 4543535}])

    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([raw_uint_struct], [{"low": 652432, "high": -1}])
    with pytest.raises(TypeEncodeError, match=error_message):
        encode_from_types([raw_uint_struct], [{"low": 0, "high": MAX_U128 + 1}])


@pytest.mark.parametrize(
    ("encode_type", "encode_values", "error_message"),
    [
        (
            StarknetCoreType.U64,
            ["wololoo", None, {"low": 12}, "0xaabbccddff001122334455"],
            "Cannot Encode Non-Integer Value '(.*?)' to StarknetCoreType.U64",
        ),
        (
            StarknetCoreType.Bool,
            [None, [None, True, False], 123, {"low": 1234, "high": 0}],
            "Cannot Encode Non-Boolean Value '(.*?)' to StarknetCoreType.Bool",
        ),
        (
            StarknetArray(StarknetCoreType.U64),
            [None, "0x12334455", {"low": 1234, "high": 0}, False],
            "(.*?) cannot be encoded into a StarknetArray",
        ),
    ],
)
def test_encode_invalid_type(encode_type, encode_values, error_message):
    for encode_value in encode_values:
        with pytest.raises(TypeEncodeError, match=error_message) as pytest_exception:
            encode_from_types([encode_type], [encode_value])
