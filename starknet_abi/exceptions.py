class InvalidAbiError(Exception):
    """
    Raised when Malformed ABI JSON is supplied to parser.
    """


class InvalidCalldataError(Exception):
    """
    Raised when there is not enough calldata to decode the type.

    .. doctest::

        >>> from starknet_abi.decode import decode_from_types, StarknetCoreType
        >>> decode_from_types([StarknetCoreType.U256], [12345])
        Traceback (most recent call last):
        ...
        starknet_abi.exceptions.InvalidCalldataError: Not Enough Calldata to decode StarknetCoreType.U256

    """


class TypeDecodeError(Exception):
    """
    Raised when a type cannot be decoded from the calldata.

    # TODO: Think through whether this is the correct error to raise & behavior
    # TODO: Make Example Correct

    .. doctest::

        >>> from starknet_abi.decode import decode_from_types, StarknetCoreType

        >>> decode_from_types([StarknetCoreType.Bool], [3])
        Traceback (most recent call last):
        ...
        starknet_abi.exceptions.TypeDecodeError: Could not decode StarknetCoreType.Bool: Bool Value must be 0 or 1

    """


class TypeEncodeError(Exception):
    """
    Raised when a type cannot be encoded from the calldata.

    .. doctest::

        >>> from starknet_abi.encode import encode_from_types, StarknetCoreType

        >>> encode_from_types([StarknetCoreType.Bool], [{'a': 123}])
        Traceback (most recent call last):
        ...
        starknet_abi.exceptions.TypeEncodeError: Cannot Encode Non-Boolean Value '{'a': 123}' to StarknetCoreType.Bool

        >>> encode_from_types([StarknetCoreType.U16], [2**17])
        Traceback (most recent call last):
        ...
        starknet_abi.exceptions.TypeEncodeError: Integer 131072 is out of range for StarknetCoreType.U16

    """
