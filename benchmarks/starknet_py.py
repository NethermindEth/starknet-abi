import json

from starknet_py.abi.v2.parser import AbiParser as AbiParserV2
from starknet_py.serialization.factory import serializer_for_payload

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
        parsed_abi = AbiParserV2(starknet_eth_abi).parse()

        transfer_func = parsed_abi.interfaces[
            "openzeppelin::token::erc20::interface::IERC20"
        ].items["transfer"]
        transfer_input_serializer = serializer_for_payload(transfer_func.inputs)

        deserialized = transfer_input_serializer.deserialize(transfer_calldata)

    return _run_bench


def bench_simple_decode():
    transfer_calldata = [
        0x7916596FEAB669322F03B6DF4E71F7B158E291FD8D273C0E53759D5B7240B4A,
        0x116933EA5369F0,
        0x0,
    ]

    parsed_abi = AbiParserV2(starknet_eth_abi).parse()

    transfer_func = parsed_abi.interfaces["openzeppelin::token::erc20::interface::IERC20"].items[
        "transfer"
    ]
    transfer_input_serializer = serializer_for_payload(transfer_func.inputs)

    def _run_bench():
        deserialized = transfer_input_serializer.deserialize(transfer_calldata)

    return _run_bench


def bench_complex_decode():

    parsed_abi = AbiParserV2(avnu_abi).parse()

    multi_route_swap_func = parsed_abi.interfaces["avnu::exchange::IExchange"].items[
        "multi_route_swap"
    ]
    multi_route_swap_input_serializer = serializer_for_payload(multi_route_swap_func.inputs)

    def _run_bench():
        deserialized = multi_route_swap_input_serializer.deserialize(multi_route_swap_calldata)

    return _run_bench
