import pytest

from starknet_abi.core import StarknetAbi

from .utils import get_abis_for_version

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
