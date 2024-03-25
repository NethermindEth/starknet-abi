import json

from starknet_abi.core import StarknetAbi
from starknet_abi.decode import decode_from_params

from .abi import STARKNET_ETH_ABI_JSON

starknet_eth_abi = json.loads(STARKNET_ETH_ABI_JSON)


def bench_setup():
    transfer_calldata = [
        0x7916596FEAB669322F03B6DF4E71F7B158E291FD8D273C0E53759D5B7240B4A,
        0x116933EA5369F0,
        0x0,
    ]

    def _run_bench():
        parsed_abi = StarknetAbi.from_json(starknet_eth_abi, "starknet_eth")

        transfer_func = parsed_abi.functions["transfer"].inputs
        calldata_copy = transfer_calldata.copy()
        decoded = decode_from_params(transfer_func, calldata_copy)

    return _run_bench


def bench_simple_decode():
    transfer_calldata = [
        0x7916596FEAB669322F03B6DF4E71F7B158E291FD8D273C0E53759D5B7240B4A,
        0x116933EA5369F0,
        0x0,
    ]

    parsed_abi = StarknetAbi.from_json(starknet_eth_abi, "starknet_eth")

    transfer_func = parsed_abi.functions["transfer"].inputs

    def _run_bench():
        calldata_copy = transfer_calldata.copy()
        decoded = decode_from_params(transfer_func, calldata_copy)

    return _run_bench
