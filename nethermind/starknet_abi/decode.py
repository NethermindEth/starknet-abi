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
from nethermind.starknet_abi.exceptions import InvalidCalldataError, TypeDecodeError

# Disable linter line breaks to make assert statements more readable
# fmt: off


def decode_core_type(  # pylint: disable=too-many-return-statements
    decode_type: StarknetCoreType, calldata: list[int]
) -> str | int | bool:
    """
    Decodes Calldata using Starknet Core Type. Takes in two parameters, a StarknetCoreType, and a mutable reference
    to a calldata array. When decoding, calldata is popped off the top of the calldata array. This reference to the
    calldata array is recursively passed between type decoders, so this array is modified during decoding

    .. doctest::
        >>> from nethermind.starknet_abi.decode import decode_core_type, StarknetCoreType
        >>> decode_core_type(StarknetCoreType.Bool, [0])
        False
        >>> decode_core_type(StarknetCoreType.U256, [12345, 0])
        12345
        >>> decode_core_type(StarknetCoreType.Felt, [256])
        '0x0100'

    :param decode_type:  Starknet Core Type to Decode
    :param calldata:  Mutable reference to calldata array. **WARN -- Array is Consumed by Method**
    """
    try:
        match decode_type:
            case (
                StarknetCoreType.U8
                | StarknetCoreType.U16
                | StarknetCoreType.U32
                | StarknetCoreType.U64
                | StarknetCoreType.U128
            ):
                value = calldata.pop(0)

                assert 0 <= value <= decode_type.max_value(), f"{value} exceeds {decode_type} Max Range"
                return value

            case StarknetCoreType.U256:
                low = calldata.pop(0)
                high = calldata.pop(0)

                assert 0 <= low < 2 ** 128, "Low Exceeds U128 Range"
                assert 0 <= high < 2 ** 128, "High Exceeds U128 Range"
                uint_256 = (high << 128) + low

                return uint_256

            case StarknetCoreType.Bool:
                bool_val = calldata.pop(0)

                assert bool_val in (0, 1), "Bool Value must be 0 or 1"
                return bool_val == 1

            case StarknetCoreType.Felt:
                encoded_int = calldata.pop(0)

                assert 0 <= encoded_int <= decode_type.max_value(), f"{encoded_int} larger than Felt"
                hexstr = f"{encoded_int:0x}"
                return f"0x0{hexstr}" if len(hexstr) % 2 else f"0x{hexstr}"

            case StarknetCoreType.ClassHash | StarknetCoreType.ContractAddress | StarknetCoreType.StorageAddress:
                encoded_int = calldata.pop(0)

                assert (
                    0 <= encoded_int <= decode_type.max_value()
                ), f"{encoded_int} larger than Felt Address"
                return f"0x{encoded_int:064x}"

            case StarknetCoreType.EthAddress:
                encoded_int = calldata.pop(0)
                assert 0 <= encoded_int <= decode_type.max_value(), f"{encoded_int:0x} larger than EthAddress"
                return f"0x{encoded_int:040x}"

            case StarknetCoreType.Bytes31:
                encoded_int = calldata.pop(0)
                assert 0 <= encoded_int <= decode_type.max_value(), f"{encoded_int:0x} larger than Bytes31"
                return f"0x{encoded_int:062x}"

            case StarknetCoreType.NoneType:
                return ""

            case _:
                raise TypeError(f"Unable to decode Starknet Core type:  {decode_type}")

    except IndexError:
        raise InvalidCalldataError(  # pylint: disable=raise-missing-from
            f"Not Enough Calldata to decode {decode_type}"
        )

    except AssertionError as assert_err:
        raise TypeDecodeError(  # pylint: disable=raise-missing-from
            f"Could not decode {decode_type}: {assert_err}"
        )


def decode_from_types(
    types: Sequence[StarknetType],
    calldata: list[int],
) -> list[Any]:
    """
    Decodes calldata array using a list of StarknetTypes.

    .. warning::

        The calldata array passed to decode_from_types is mutated during decoding.  Calldata is recursively
        popped off the stack as decoding occurs

    .. doctest::
        >>> from nethermind.starknet_abi.decode import decode_from_types, StarknetCoreType, StarknetArray
        >>> decode_from_types([StarknetArray(StarknetCoreType.U8), StarknetCoreType.Bool], [3, 123, 244, 210, 0])
        [[123, 244, 210], False]
        >>> decode_from_types(
        ...     [StarknetCoreType.ContractAddress, StarknetCoreType.U256, StarknetCoreType.Bool],
        ...     [0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 250_000, 0, 1]
        ... )
        ['0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', 250000, True]


    :param types:  Sequence of StarknetType to decode
    :param calldata: Mutable Array of Calldata
    """

    output_data: list[Any] = []

    for starknet_type in types:
        # Starknet Core Type decoding does not require the recursive try/except handler
        if isinstance(starknet_type, StarknetCoreType):
            output_data.append(decode_core_type(starknet_type, calldata))
            continue

        try:
            if isinstance(starknet_type, StarknetArray):
                array_len = calldata.pop(0)
                output_data.append(
                    [
                        decode_from_types([starknet_type.inner_type], calldata)[0]
                        for _ in range(array_len)
                    ]
                )
                continue

            if isinstance(starknet_type, StarknetOption):
                if calldata.pop(0) == 1:
                    output_data.append(None)
                    continue

                output_data.append(
                    decode_from_types([starknet_type.inner_type], calldata)[0]
                )
                continue

            if isinstance(starknet_type, StarknetStruct):
                output_data.append(decode_from_params(starknet_type.members, calldata))
                continue

            if isinstance(starknet_type, StarknetEnum):
                enum_index = calldata.pop(0)
                variant_name, variant_type = starknet_type.variants[enum_index]
                output_data.append(
                    {variant_name: decode_from_types([variant_type], calldata)[0]}
                )
                continue

            if isinstance(starknet_type, StarknetTuple):
                output_data.append(
                    tuple(
                        decode_from_types([tuple_member], calldata)[0]
                        for tuple_member in starknet_type.members
                    )
                )
                continue

            raise TypeError(f"Cannot Decode Calldata for Type: {starknet_type}")

        except IndexError:
            # Raised When calldata.pop() fails for a StarknetOption, a StarknetArray, or a StarknetEnum
            raise InvalidCalldataError(  # pylint: disable=raise-missing-from
                f"Insufficient Calldata to decode {starknet_type}"
            )

        except InvalidCalldataError as calldata_err:
            # Recursive Decode calls
            raise InvalidCalldataError(
                f"Insufficient Calldata to decode {starknet_type}"
            ) from calldata_err

        except TypeDecodeError as type_err:
            raise TypeDecodeError(f"Could not decode {starknet_type}") from type_err

    return output_data


def decode_from_params(
    params: Sequence[AbiParameter],
    calldata: list[int],
) -> dict[str, Any]:
    """
    Decodes Calldata using AbiParameters, which have names and types

    .. warning::

        Calldata list is consumed during decoding, as calldata is recursively popped off the top of the calldata
        throughout the decoding process

    .. doctest::

        >>> from nethermind.starknet_abi.decode import AbiParameter, decode_from_params, StarknetCoreType
        >>> decode_from_params(
        ...     [AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
        ...     [123456, 654321]
        ... )
        {'a': 123456, 'b': 654321}

    :param params: Sequence of AbiParameters
    :param calldata: Mutable calldata Array
    :return: Dict mapping Parameter names to decoded types
    """

    parameter_names = [param.name for param in params]
    parameter_types = [param.type for param in params]

    decoded_values = decode_from_types(parameter_types, calldata)
    return dict(zip(parameter_names, decoded_values, strict=True))
