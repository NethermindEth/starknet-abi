from starknet_abi.abi_types import AbiParameter, StarknetCoreType
from starknet_abi.core import StarknetAbi
from starknet_abi.decoding_types import AbiEvent, AbiFunction
from tests.utils import load_abi


def test_function_signatures():
    transfer = AbiFunction(
        name="transfer",
        inputs=[
            AbiParameter("recipient", StarknetCoreType.ContractAddress),
            AbiParameter("amount", StarknetCoreType.U256),
        ],
        outputs=[StarknetCoreType.Bool],
    )

    assert (
        transfer.id_str() == "Function(recipient:ContractAddress,amount:U256) -> (Bool)"
    )
    assert (
        transfer.signature.hex()
        == "0083afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e"
    )


def test_event_signatures():
    transfer = AbiEvent(
        name="Transfer",
        data=[
            AbiParameter("from", StarknetCoreType.ContractAddress),
            AbiParameter("to", StarknetCoreType.ContractAddress),
            AbiParameter("amount", StarknetCoreType.U256),
        ],
    )

    assert (
        transfer.id_str()
        == "Event(from:ContractAddress,to:ContractAddress,amount:U256)"
    )
    assert (
        transfer.signature.hex()
        == "0099cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )


def test_load_eth_abi():
    eth_abi = load_abi("starknet_eth.json", 2)
    eth_decoder = StarknetAbi.from_json(
        eth_abi,
        "starknet_eth",
        bytes.fromhex(
            "05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed"
        ),
    )
