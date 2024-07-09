from typing import Any, Sequence

from nethermind.starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetEnum,
    StarknetOption,
    StarknetStruct,
    StarknetTuple,
    StarknetType,
)
from nethermind.starknet_abi.exceptions import TypeEncodeError

# Disables Assert statements from being formatted into multi-line messes
# fmt: off
# pylint: disable=too-many-return-statements,raise-missing-from


def _get_enum_index(enum_type: StarknetEnum, enum_key: str) -> tuple[int, StarknetType]:
    """
    Get the index of the enum key and the enum type.

    :param enum_type:
    :param enum_key:
    :return:
    """
    for idx, (key, value) in enumerate(enum_type.variants):
        if key == enum_key:
            return idx, value

    raise ValueError(f"Enum Key {enum_key} not found in Enum {enum_type}")


def encode_core_type(  # pylint: disable=too-many-return-statements,too-many-branches
    encode_type: StarknetCoreType,
    value: bytes | int | bool | str,
) -> list[int]:
    """
    Encode data from types.

    :param encode_type:
    :param value:
    """

    try:
        match encode_type:
            case (
                StarknetCoreType.U8
                | StarknetCoreType.U16
                | StarknetCoreType.U32
                | StarknetCoreType.U64
                | StarknetCoreType.U128
            ):
                assert isinstance(value, int), f"Cannot Encode Non-Integer Value '{value!r}' to {encode_type}"
                assert 0 <= value <= encode_type.max_value(), f"Integer {value!r} is out of range for {encode_type}"

                return [value]

            case StarknetCoreType.U256:
                assert isinstance(value, int), f"Cannot Encode Non-Integer Value '{value!r}' to {encode_type}"
                assert 0 <= value <= encode_type.max_value(), f"Integer {value!r} is out of range for {encode_type}"

                high = value >> 128
                low = value & ((1 << 128) - 1)
                return [low, high]

            case StarknetCoreType.Bool:
                assert isinstance(value, bool), f"Cannot Encode Non-Boolean Value '{value!r}' to {encode_type}"

                return [1] if value else [0]

            case (
                StarknetCoreType.Felt
                | StarknetCoreType.ClassHash
                | StarknetCoreType.ContractAddress
                | StarknetCoreType.EthAddress
                | StarknetCoreType.StorageAddress
                | StarknetCoreType.Bytes31
            ):
                if isinstance(value, str):
                    assert value.startswith("0x"), "Hex Strings must be 0x Prefixed"
                    int_encoded = int(value, 16)
                    if encode_type == StarknetCoreType.EthAddress:
                        assert int_encoded <= encode_type.max_value(), f"{value!r} Is larger than an Eth Address"
                    elif encode_type == StarknetCoreType.Bytes31:
                        assert 0 <= int_encoded <= encode_type.max_value(), f"{value!r} Does not Fit into 31 Bytes"
                    else:
                        assert int_encoded <= encode_type.max_value(), f"{value!r} Does not Fit into Starknet Felt"

                    return [int_encoded]

                if isinstance(value, int):
                    if encode_type == StarknetCoreType.EthAddress:
                        assert value <= encode_type.max_value(), f"{value!r} Is larger than an Eth Address"
                    elif encode_type == StarknetCoreType.Bytes31:
                        assert 0 <= value <= encode_type.max_value(), f"{value!r} Does not Fit into 31 Bytes"
                    else:
                        assert 0 <= value <= encode_type.max_value(), f"{value!r} Does not Fit into Starknet Felt"

                    return [value]

                if isinstance(value, bytes):
                    int_encoded = int.from_bytes(value, "big")
                    if encode_type == StarknetCoreType.EthAddress:
                        assert int_encoded <= encode_type.max_value(), f"{value!r} Is larger than an Eth Address"
                    elif encode_type == StarknetCoreType.Bytes31:
                        assert 0 <= int_encoded <= encode_type.max_value(), f"{value!r} Does not Fit into 31 Bytes"
                    else:
                        assert value <= encode_type.max_value(), f"{value!r} Does not Fit into Starknet Felt"

                    return [int_encoded]

                raise TypeError(
                    f"Cannot Encode Python {type(value)} Type to {encode_type}.  Represent Felt Types "
                    f"as int, hex strings, or big-endian bytes"
                )

            case StarknetCoreType.NoneType:
                return []

            case _:
                raise TypeError(f"Unable to encode Type {encode_type}")

    except AssertionError as assert_err:
        raise TypeEncodeError(assert_err)


def encode_from_types(  # pylint: disable=too-many-branches
    types: Sequence[StarknetType],
    values: list[Any],
) -> list[int]:
    """
    Decode data from types.
    """
    encoded_calldata = []
    for encode_type, encode_value in zip(types, values, strict=True):
        if isinstance(encode_type, StarknetCoreType):
            encoded_calldata += encode_core_type(encode_type, encode_value)
            continue

        try:
            if isinstance(encode_type, StarknetArray):
                assert isinstance(encode_value, (list, tuple)), f"{encode_value} cannot be encoded into a StarknetArray"

                encoded_calldata.append(len(encode_value))

                for array_element in encode_value:
                    encoded_calldata += encode_from_types(
                        [encode_type.inner_type], [array_element]
                    )
                continue

            if isinstance(encode_type, StarknetOption):
                if encode_value is None:
                    encoded_calldata.append(1)
                else:
                    encoded_calldata.append(0)
                    encoded_calldata += encode_from_types(
                        [encode_type.inner_type], [encode_value]
                    )
                continue

            if isinstance(encode_type, StarknetStruct):
                assert isinstance(encode_value, dict), f"{encode_value} cannot be encoded into a StarknetStruct"

                encoded_calldata += encode_from_params(
                    encode_type.members, encode_value
                )
                continue

            if isinstance(encode_type, StarknetEnum):
                assert isinstance(encode_value, dict), f"{encode_value} cannot be encoded into a StarknetEnum"
                enum_items = list(encode_value.items())
                assert len(enum_items) == 1, f"Enum Value {encode_value} must have exactly one key-value pair"

                enum_key, enum_value = enum_items[0]

                enum_index, enum_type = _get_enum_index(encode_type, enum_key)

                encoded_calldata.append(enum_index)
                encoded_calldata += encode_from_types([enum_type], [enum_value])
                continue

            if isinstance(encode_type, StarknetTuple):
                assert isinstance(encode_value, tuple), f"{encode_value} cannot be encoded into a StarknetTuple"
                for tuple_type, tuple_value in zip(encode_type.members, encode_value):
                    encoded_calldata += encode_from_types([tuple_type], [tuple_value])
                continue

            raise TypeError(
                f"Cannot Encode {encode_value} for Type {encode_type}"
            )

        except AssertionError as assert_err:
            raise TypeEncodeError(assert_err)

        except TypeEncodeError as encode_err:
            raise TypeEncodeError(f"Failed to Encode {encode_value} to {encode_type}") from encode_err

    return encoded_calldata


def encode_from_params(
    params: Sequence[AbiParameter],
    encode_values: dict[str, Any],
) -> list[int]:
    """
    Decode data from types.
    """
    if len(encode_values) != len(params):
        raise ValueError(
            f"Number of Encode Values '{len(encode_values)}' does not match Number of Abi Params '{len(params)}'"
        )

    parameter_names = [param.name for param in params]
    parameter_types = [param.type for param in params]

    encode_values_list = []

    for name in parameter_names:
        try:
            encode_values_list.append(encode_values[name])
        except KeyError:
            raise ValueError(f"Missing Encode Value for Param: {name}")

    return encode_from_types(parameter_types, encode_values_list)
