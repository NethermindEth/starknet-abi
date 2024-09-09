import json

import pytest

from nethermind.starknet_abi.abi_types import (
    AbiParameter,
    StarknetCoreType,
    StarknetNonZero,
    StarknetStruct,
    StarknetTuple,
)
from nethermind.starknet_abi.core import StarknetAbi
from tests.test_abi_parsing.utils import get_abis_for_version
from tests.utils import PARENT_DIR

v1_abi_names_and_json = get_abis_for_version("v1")
v2_abi_names_and_json = get_abis_for_version("v2")


@pytest.mark.parametrize(("abi_name", "abi_json"), v1_abi_names_and_json)
def test_parse_v1_abis_to_starknet_abi(abi_name, abi_json):
    decoder = StarknetAbi.from_json(abi_json, abi_name, b"")


@pytest.mark.parametrize(("abi_name", "abi_json"), v2_abi_names_and_json)
def test_parse_v2_abis_to_starknet_abi(abi_name, abi_json):
    decoder = StarknetAbi.from_json(abi_json, abi_name, b"")

    if abi_name == "starknet_eth":
        assert "transfer" in decoder.functions

    if abi_name == "argent_account_v3":
        func = decoder.functions["change_guardian_backup"]
        assert func.inputs[0].type.inner_type.variants[0] == (
            "Starknet",
            StarknetStruct(
                "argent::signer::signer_signature::StarknetSigner",
                [AbiParameter("pubkey", StarknetNonZero(StarknetCoreType.Felt))],
            ),
        )


def test_named_tuple_parsing():
    abi_json = json.load(open(PARENT_DIR / "abis" / "v1" / "legacy_named_tuple.json"))

    parsed_abi = StarknetAbi.from_json(
        abi_json,
        "legacy_named_tuple",
        bytes.fromhex(
            "0484c163658bcce5f9916f486171ac60143a92897533aa7ff7ac800b16c63311"
        ),
    )

    xor_inputs = parsed_abi.functions["xor_counters"].inputs
    input_name, input_type = xor_inputs[0].name, xor_inputs[0].type
    assert isinstance(input_type, StarknetStruct)
    assert input_name == "index_and_x"
    assert input_type.name == "IndexAndValues"
    assert input_type.members == [
        AbiParameter("index", StarknetCoreType.Felt),
        AbiParameter(
            "values", StarknetTuple([StarknetCoreType.Felt, StarknetCoreType.Felt])
        ),
    ]


def test_storage_address_parsing():
    abi_json = json.load(open(PARENT_DIR / "abis" / "v2" / "storage_address.json"))

    parsed_abi = StarknetAbi.from_json(
        abi_json,
        "storage_address",
        bytes.fromhex(
            "0484c163658bcce5f9916f486171ac60143a92897533aa7ff7ac800b16c63311"
        ),
    )

    storage_function = parsed_abi.functions["storage_read"]

    assert storage_function.inputs == [
        AbiParameter("address_domain", StarknetCoreType.U32),
        AbiParameter("address", StarknetCoreType.StorageAddress),
    ]
