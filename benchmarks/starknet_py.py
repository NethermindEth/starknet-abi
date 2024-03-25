import json

from starknet_py.abi.v2.parser import AbiParser as AbiParserV2
from starknet_py.serialization.factory import serializer_for_payload

from .abi import STARKNET_ETH_ABI_JSON

starknet_eth_abi = json.loads(STARKNET_ETH_ABI_JSON)


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

    transfer_func = parsed_abi.interfaces[
        "openzeppelin::token::erc20::interface::IERC20"
    ].items["transfer"]
    transfer_input_serializer = serializer_for_payload(transfer_func.inputs)

    def _run_bench():
        deserialized = transfer_input_serializer.deserialize(transfer_calldata)

    return _run_bench
