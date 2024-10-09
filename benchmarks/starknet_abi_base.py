import json

from nethermind.starknet_abi.core import StarknetAbi
from nethermind.starknet_abi.decode import decode_from_params

from .abi import AVNU_ABI_JSON, STARKNET_ETH_ABI_JSON
from .calldata import multi_route_swap_calldata

starknet_eth_abi = json.loads(STARKNET_ETH_ABI_JSON)
avnu_abi = json.loads(AVNU_ABI_JSON)


def bench_setup():
    transfer_calldata = [
        0x7916596FEAB669322F03B6DF4E71F7B158E291FD8D273C0E53759D5B7240B4A,
        0x116933EA5369F0,
        0x0,
    ]

    def _run_bench():
        parsed_abi = StarknetAbi.from_json(starknet_eth_abi)

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

    parsed_abi = StarknetAbi.from_json(starknet_eth_abi)

    transfer_func = parsed_abi.functions["transfer"].inputs

    def _run_bench():
        calldata_copy = transfer_calldata.copy()
        decoded = decode_from_params(transfer_func, calldata_copy)

    return _run_bench


# https://voyager.online/tx/0x4335f58410d8e66309e67d25c12bc61b5bc4b4d1ada61ff1eb2f3a0cabbb3d2
def bench_complex_decode():
    parsed_abi = StarknetAbi.from_json(avnu_abi)

    multi_route_swap = parsed_abi.functions["multi_route_swap"].inputs

    def _run_bench():
        calldata_copy = multi_route_swap_calldata.copy()
        decoded = decode_from_params(multi_route_swap, calldata_copy)

    return _run_bench
