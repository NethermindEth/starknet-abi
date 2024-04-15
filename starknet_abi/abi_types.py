from dataclasses import dataclass
from enum import Enum
from typing import Literal, Sequence, Union

# Disable Invalid Name check to allow lower-cased enum names

# pylint: disable=invalid-name

AbiMemberType = Literal[
    "function",
    "l1_handler",
    "struct",
    "constructor",
    "event",
    "interface",
    "impl",
    "type_def",  # Internal Definition:  type_def = Union[struct, enum]
]


class StarknetAbiEventKind(Enum):
    """Represents kinds of Abi Events"""

    enum = "enum"
    struct = "struct"
    data = "data"
    nested = "nested"
    key = "key"
    flat = "flat"


class StarknetCoreType(Enum):
    """
    Dataclasses representing the Core datatypes.
    """

    # Uint Datatype Enum Values are used to represent the number of bytes in the datatype
    U8 = 1
    U16 = 2
    U32 = 4
    U64 = 8
    U128 = 16
    U256 = 32

    # Enum Values are arbitrary for other types
    Bool = 3
    Felt = 5
    ContractAddress = 6
    EthAddress = 7
    ClassHash = 9
    NoneType = 10  # No decoder, used in enums literals

    def __repr__(self):
        # Override __repr__ to return the Enum Name without value
        return f"StarknetCoreType.{self.name}"

    @classmethod
    def int_from_string(cls, type_str):
        """
        parses a core::integer::<type_str> into a Starknet Core type

        .. doctest::
            >>> from starknet_abi.abi_types import StarknetCoreType
            >>> StarknetCoreType.int_from_string('u16')
            StarknetCoreType.U16
            >>> StarknetCoreType.int_from_string('u256')
            StarknetCoreType.U256

        :param type_str:
        :return:
        """
        match type_str:
            case "u8":
                return cls.U8
            case "u16":
                return cls.U16
            case "u32":
                return cls.U32
            case "u64":
                return cls.U64
            case "u128":
                return cls.U128
            case "u256":
                return cls.U256
            case _:
                raise ValueError(f"Invalid integer type: {type_str}")

    def id_str(self):
        """
        Returns the name of the enum field

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetCoreType
            >>> StarknetCoreType.U128.id_str()
            'U128'
            >>> StarknetCoreType.Bool.id_str()
            'Bool'
            >>> StarknetCoreType.ContractAddress.id_str()
            'ContractAddress'
            >>> StarknetCoreType.NoneType.id_str()
            'NoneType'

        :return:
        """
        return self.name

    def max_value(self):
        """
        Returns the maximum value of the Starknet Core Type

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetCoreType
            >>> StarknetCoreType.U256.max_value()
            115792089237316195423570985008687907853269984665640564039457584007913129639935

        :return:
        """
        if self.name.startswith("U"):
            return 2 ** (8 * self.value) - 1

        if self.name in ("Felt", "ContractAddress", "ClassHash"):
            return (2**251) + (17 * (2**192)) + 1

        if self.name == "EthAddress":
            return 2**160 - 1

        raise ValueError(f"Cannot get max value for type: {self.name}")


@dataclass(slots=True)
class StarknetArray:
    """
    Dataclass representing a Starknet ABI Array.  Both core::array::Array and core::array::Span are mapped to this
    dataclass since their ABI Encoding & Decoding are identical

    """

    inner_type: "StarknetType"

    def id_str(self):
        """

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetArray, StarknetCoreType
            >>> felt_array = StarknetArray(StarknetCoreType.Felt)
            >>> felt_array.id_str()
            '[Felt]'

        :return:
        """
        return f"[{self.inner_type.id_str()}]"


@dataclass(slots=True)
class StarknetOption:
    """
    Dataclass Representing a Starknet Option
    """

    inner_type: "StarknetType"

    def id_str(self):
        """
        Returns Inner Type String wrapped with Option[]

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetOption, StarknetCoreType
            >>> uint_option = StarknetOption(StarknetCoreType.U128)
            >>> uint_option.id_str()
            'Option[U128]'

        :return:
        """
        return f"Option[{self.inner_type.id_str()}]"


@dataclass(slots=True)
class StarknetEnum:
    """
    Represents a StarknetEnum with its name and ordered variants
    """

    name: str
    variants: Sequence[tuple[str, "StarknetType"]]  # variant_name  # variant_type

    def id_str(self):
        """
        Returns Enum[<variant-name:variant-type>]

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetEnum, StarknetCoreType
            >>> status_enum = StarknetEnum(
            ...     name="Status",
            ...     variants=[
            ...         ('Success', StarknetCoreType.NoneType),
            ...         ('Failure', StarknetCoreType.NoneType),
            ...     ]
            ... )
            >>> status_enum.id_str()
            "Enum['Success','Failure']"
            >>> type_enum = StarknetEnum(
            ...     name="AddressType",
            ...     variants=[
            ...         ('Class', StarknetCoreType.ClassHash),
            ...         ('Contract', StarknetCoreType.ContractAddress),
            ...     ]
            ... )
            >>> type_enum.id_str()
            'Enum[Class:ClassHash,Contract:ContractAddress]'

        :return:
        """
        variants_str = ",".join(
            [
                (
                    f"{variant_name}:{variant_type.id_str()}"
                    if variant_type != StarknetCoreType.NoneType
                    else f"'{variant_name}'"
                )
                for variant_name, variant_type in self.variants
            ]
        )
        return f"Enum[{variants_str}]"


@dataclass(slots=True)
class StarknetTuple:
    """
    Dataclass Representing a Tuple, and the Types of the Tuple Members
    """

    members: Sequence["StarknetType"]

    def id_str(self):
        """
        Returns the string representation of a tuple of types

        .. doctest::
            >>> from starknet_abi.abi_types import StarknetTuple, StarknetCoreType
            >>> uint_tuple = StarknetTuple([StarknetCoreType.U32, StarknetCoreType.U32])
            >>> uint_tuple.id_str()
            '(U32,U32)'
            >>> nested_tuple = StarknetTuple([
            ...     StarknetCoreType.U256,
            ...     StarknetTuple([StarknetCoreType.U8, StarknetCoreType.U8])
            ... ])
            >>> nested_tuple.id_str()
            '(U256,(U8,U8))'

        :return:
        """
        members_str = ",".join([member.id_str() for member in self.members])
        return f"({members_str})"


@dataclass(slots=True)
class StarknetStruct:
    """
    Dataclass Representing a Starknet Struct Definition
    """

    name: str
    members: Sequence["AbiParameter"]

    def id_str(self):
        """

        .. doctest::
            >>> from starknet_abi.abi_types import StarknetStruct, StarknetCoreType, StarknetArray, AbiParameter
            >>> struct_def = StarknetStruct(
            ...     name="PackageVersion",
            ...     members=[
            ...         AbiParameter("version_hash", StarknetCoreType.Felt),
            ...         AbiParameter("version", StarknetArray(StarknetCoreType.U8))
            ...     ]
            ... )
            >>> struct_def.id_str()
            '{version_hash:Felt,version:[U8]}'

        :return:
        """
        members_str = ",".join(
            [f"{member.name}:{member.type.id_str()}" for member in self.members]
        )
        return "{" + members_str + "}"


StarknetType = Union[
    StarknetCoreType,
    StarknetOption,
    StarknetTuple,
    StarknetArray,
    StarknetStruct,
    StarknetEnum,
]


@dataclass(slots=True)
class AbiParameter:
    """
    Dataclass Representing an ABI Parameter.  Includes a parameter name and the StarknetType of the parameter.
    """

    name: str
    type: StarknetType

    def id_str(self):
        """
        Returns a string representation of the ABI Parameter.  Represents the name, followed by a colon, then a type

        .. doctest::

            >>> from starknet_abi.abi_types import StarknetCoreType, AbiParameter
            >>> from_param = AbiParameter('from', StarknetCoreType.ContractAddress)
            >>> from_param.id_str()
            'from:ContractAddress'

        :return:
        """
        return f"{self.name}:{self.type.id_str()}"


# Constant Types

STARKNET_ACCOUNT_CALL = StarknetStruct(
    name="Call",
    members=[
        AbiParameter("to", StarknetCoreType.ContractAddress),
        AbiParameter("selector", StarknetCoreType.Felt),
        AbiParameter("calldata", StarknetArray(StarknetCoreType.Felt)),
    ],
)

STARKNET_V0_CALL = StarknetStruct(
    name="CallArray",
    members=[
        AbiParameter("to", StarknetCoreType.Felt),
        AbiParameter("selector", StarknetCoreType.Felt),
        AbiParameter("data_offset", StarknetCoreType.U128),
        AbiParameter("data_len", StarknetCoreType.U128),
    ],
)
