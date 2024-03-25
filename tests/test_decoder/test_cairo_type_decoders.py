import pytest

from starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
)
from starknet_abi.decode import decode_from_types
from starknet_abi.encode import encode_from_types


@pytest.mark.parametrize(
    ["starknet_type", "calldata", "decoded"],
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
def test_enum_type_serializer(calldata, decoded):
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
            "0x0000000000000000000000000000000000000000000000000123456789abcdef",
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
def test_option_serializer(starknet_type, decoded, calldata):
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
def test_struct_serializer_valid_values(struct_type, calldata, decoded):
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
