import pytest

from starknet_abi.core import StarknetAbi
from starknet_abi.dispatch import DecodingDispatcher
from tests.utils import load_abi


@pytest.fixture()
def decoding_dispatcher() -> DecodingDispatcher:
    dispatcher = DecodingDispatcher()

    for abi_name, abi_version, class_hash in [
        # fmt: off
        ('contract_abi', 1, bytes.fromhex('010455c752b86932ce552f2b0fe81a880746649b9aee7e0d842bf3f52378f9f8')),
        ('starknet_eth', 2, bytes.fromhex('05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed')),
        # fmt: on
    ]:
        abi_json = load_abi(abi_name, abi_version)
        parsed_abi = StarknetAbi.from_json(abi_json, abi_name, class_hash)

        dispatcher.add_abi(parsed_abi)

    return dispatcher
