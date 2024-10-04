import pytest

from nethermind.starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
)
from nethermind.starknet_abi.decode import decode_from_types
from nethermind.starknet_abi.encode import encode_from_types
from nethermind.starknet_abi.exceptions import TypeDecodeError, TypeEncodeError
from nethermind.starknet_abi.utils import STARK_FIELD

U128_MAX = 2**128 - 1


@pytest.mark.parametrize(
    ("starknet_type", "calldata", "decoded"),
    [
        (StarknetArray(StarknetCoreType.U256), [0], []),
        (StarknetArray(StarknetCoreType.U256), [2, 16, 0, 48, 0], [16, 48]),
        # 2 nested arrays and last filled with U32s
        (
            StarknetArray(StarknetArray(StarknetArray(StarknetCoreType.U32))),
            [1, 1, 2, 22, 38],
            [[[22, 38]]],
        ),
    ],
)
def test_array_decoding(starknet_type, calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([starknet_type], _calldata)
    encoded_calldata = encode_from_types([starknet_type], [decoded])

    assert decoded_values[0] == decoded
    assert encoded_calldata == calldata
    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("starknet_type", "calldata", "decoded"),
    [
        (StarknetCoreType.U512, [250, 0, 0, 0], 250),
        (StarknetCoreType.U512, [U128_MAX, U128_MAX, U128_MAX, U128_MAX], 2**512 - 1),
        (StarknetCoreType.U256, [U128_MAX, U128_MAX], 2**256 - 1),
        (StarknetCoreType.I32, [STARK_FIELD - 120], -120),
        (StarknetCoreType.I64, [2**63 - 1], 2**63 - 1),
        (
            StarknetCoreType.U32,
            [
                2**32 - 2,
            ],
            2**32 - 2,
        ),
    ],
)
def test_decode_valid_int_types(starknet_type, calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([starknet_type], _calldata)
    encoded_calldata = encode_from_types([starknet_type], [decoded])

    assert decoded_values[0] == decoded
    assert len(decoded_values) == 1
    assert encoded_calldata == calldata

    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("starknet_type", "calldata", "encode_val"),
    [
        (StarknetCoreType.U32, [2**32], 2**32),
        (StarknetCoreType.U64, [2**64], 2**64),
        (StarknetCoreType.U512, [2**128, 0, 0, 0], 2**512),
        (StarknetCoreType.I32, [2**31], 2**31),
        (StarknetCoreType.I64, [STARK_FIELD - (2**63 + 1)], (-1 * (2**63)) - 1),
    ],
)
def test_encode_out_of_range_types(starknet_type, calldata, encode_val):

    with pytest.raises(TypeEncodeError):
        encode_from_types([starknet_type], [encode_val])

    _calldata = calldata.copy()

    with pytest.raises(TypeDecodeError):
        decode_from_types([starknet_type], _calldata)


@pytest.mark.parametrize(
    ("calldata", "decoded"),
    [
        ([0], False),
        ([1], True),
    ],
)
def test_valid_bool_values(calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([StarknetCoreType.Bool], _calldata)
    encoded_calldata = encode_from_types([StarknetCoreType.Bool], [decoded])

    assert decoded_values[0] == decoded
    assert len(decoded_values) == 1
    assert encoded_calldata == calldata

    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("calldata", "decoded"),
    [
        ([0, 100, 0], {"a": 100}),
        ([1, 200], {"b": 200}),
        ([2, 0, 300, 300, 0], {"c": {"my_option": 300, "my_uint": 300}}),
    ],
)
def test_enum_type_encoder(calldata, decoded):
    varied_type_enum = StarknetEnum(
        name="Enum A",
        variants=[
            ("a", StarknetCoreType.U256),
            ("b", StarknetCoreType.U128),
            (
                "c",
                StarknetStruct(
                    name="Struct A",
                    members=[
                        AbiParameter(
                            "my_option", StarknetOption(StarknetCoreType.U128)
                        ),
                        AbiParameter("my_uint", StarknetCoreType.U256),
                    ],
                ),
            ),
        ],
    )

    _calldata = calldata.copy()

    decoded_values = decode_from_types([varied_type_enum], _calldata)
    encoded_calldata = encode_from_types([varied_type_enum], [decoded])

    assert len(_calldata) == 0  # All calldata should be consumed during decoding

    assert encoded_calldata == calldata
    assert decoded_values[0] == decoded


@pytest.mark.parametrize(
    ("calldata", "decoded"),
    [
        ([0], {"Submitted": ""}),
        ([1], {"Executed": ""}),
        ([2], {"Finalized": ""}),
    ],
)
def test_literal_enum(calldata, decoded):
    literal_enum = StarknetEnum(
        name="TxStatus",
        variants=[
            ("Submitted", StarknetCoreType.NoneType),
            ("Executed", StarknetCoreType.NoneType),
            ("Finalized", StarknetCoreType.NoneType),
        ],
    )

    _calldata = calldata.copy()

    decoded_values = decode_from_types([literal_enum], _calldata)
    encoded_calldata = encode_from_types([literal_enum], [decoded])

    assert decoded_values[0] == decoded
    assert encoded_calldata == calldata
    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("starknet_type", "calldata", "decoded"),
    [
        (
            StarknetCoreType.Felt,
            [0x0123456789ABCDEF],
            "0x0123456789abcdef",
        ),
        (
            StarknetCoreType.ContractAddress,
            [0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7],
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
        ),
        (
            StarknetCoreType.ClassHash,
            [0x05FFBCFEB50D200A0677C48A129A11245A3FC519D1D98D76882D1C9A1B19C6ED],
            "0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed",
        ),
    ],
)
def test_hex_types(starknet_type, decoded, calldata):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([starknet_type], _calldata)
    encoded_calldata = encode_from_types([starknet_type], [decoded])

    assert encoded_calldata == calldata
    assert decoded_values[0] == decoded
    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("starknet_type", "decoded", "calldata"),
    [
        (StarknetOption(StarknetCoreType.U128), 123, [0, 123]),
        (StarknetOption(StarknetCoreType.U256), 1, [0, 1, 0]),
        (StarknetOption(StarknetCoreType.U128), None, [1]),
        (StarknetOption(StarknetCoreType.U256), None, [1]),
    ],
)
def test_option_encoder(starknet_type, decoded, calldata):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([starknet_type], _calldata)
    encoded_calldata = encode_from_types([starknet_type], [decoded])

    assert encoded_calldata == calldata
    assert decoded_values[0] == decoded
    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("struct_type", "calldata", "decoded"),
    [
        (
            StarknetStruct(
                name="CartesianPoint",
                members=[
                    AbiParameter("x", StarknetCoreType.U128),
                    AbiParameter("y", StarknetCoreType.U128),
                ],
            ),
            [1, 2],
            {"x": 1, "y": 2},
        ),
        (
            StarknetStruct(
                name="Queue",
                members=[
                    AbiParameter("head", StarknetCoreType.U8),
                    AbiParameter("items", StarknetArray(StarknetCoreType.U128)),
                    AbiParameter(
                        "metadata",
                        StarknetStruct(
                            name="MetaData",
                            members=[
                                AbiParameter("version", StarknetCoreType.U8),
                                AbiParameter("init_timestamp", StarknetCoreType.U64),
                            ],
                        ),
                    ),
                ],
            ),
            [22, 2, 38, 334, 5, 123456],
            {
                "head": 22,
                "items": [38, 334],
                "metadata": {"version": 5, "init_timestamp": 123456},
            },
        ),
    ],
)
def test_struct_encoder_valid_values(struct_type, calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([struct_type], _calldata)
    encoded_calldata = encode_from_types([struct_type], [decoded])

    assert decoded_values[0] == decoded
    assert encoded_calldata == calldata

    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("starknet_type", "calldata", "decoded"),
    [
        (StarknetTuple([StarknetCoreType.U32, StarknetCoreType.U32]), [1, 2], (1, 2)),
        (
            StarknetTuple([StarknetCoreType.U32, StarknetArray(StarknetCoreType.U32)]),
            [1, 2, 22, 38],
            (1, [22, 38]),
        ),
        (
            # 3 nested tuples
            StarknetTuple(
                [
                    StarknetTuple([StarknetTuple([StarknetCoreType.U32])]),
                    StarknetCoreType.Bool,
                ]
            ),
            [1, 0],
            (((1,),), False),
        ),
    ],
)
def test_tuple_valid_values(starknet_type, calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([starknet_type], _calldata)
    encoded_calldata = encode_from_types([starknet_type], [decoded])

    assert decoded_values[0] == decoded
    assert encoded_calldata == calldata

    assert len(_calldata) == 0


@pytest.mark.parametrize(
    ("calldata", "decoded"),
    [
        (
            [0x3DC782D803B8A574D29E3383A4885EBDDDA9D8D7E15CD5A5F1FB1651EE052E],
            "0x3dc782d803b8a574d29e3383a4885ebddda9d8d7e15cd5a5f1fb1651ee052e",
        ),
    ],
)
def test_bytes_31(calldata, decoded):
    _calldata = calldata.copy()

    decoded_values = decode_from_types([StarknetCoreType.Bytes31], _calldata)
    encoded_calldata = encode_from_types([StarknetCoreType.Bytes31], [decoded])

    assert len(decoded_values[0]) == 64  # instead of 66...
    assert decoded_values[0] == decoded
    assert encoded_calldata == calldata
    assert len(_calldata) == 0
