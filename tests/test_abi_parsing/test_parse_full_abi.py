import json

from nethermind.starknet_abi.abi_types import (
    AbiParameter,
    StarknetArray,
    StarknetCoreType,
    StarknetStruct,
)
from nethermind.starknet_abi.core import StarknetAbi
from nethermind.starknet_abi.decoding_types import AbiEvent, AbiFunction
from nethermind.starknet_abi.parse import parse_abi_function
from tests.abi import (
    NO_STRUCT_ABI_DEFINITION,
    NO_STRUCT_CLASS_HASH,
    VERSION_0_ABI_DEFINITION,
    VERSION_0_CLASS_HASH,
)
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

    assert transfer.id_str() == "Function(recipient:ContractAddress,amount:U256) -> (Bool)"
    assert (
        transfer.signature.hex()
        == "0083afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e"
    )


def test_event_signatures():
    transfer = AbiEvent(
        name="Transfer",
        parameters=["from", "to", "amount"],
        data={
            "from": StarknetCoreType.ContractAddress,
            "to": StarknetCoreType.ContractAddress,
            "amount": StarknetCoreType.U256,
        },
    )

    assert transfer.id_str() == "Event(from:ContractAddress,to:ContractAddress,amount:U256)"
    assert (
        transfer.signature.hex()
        == "0099cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )


def test_key_event_signature():
    transfer = AbiEvent(
        name="Transfer",
        parameters=["from", "to", "amount"],
        keys={
            "from": StarknetCoreType.ContractAddress,
            "to": StarknetCoreType.ContractAddress,
        },
        data={
            "amount": StarknetCoreType.U256,
        },
    )

    assert transfer.id_str() == "Event(<from>:ContractAddress,<to>:ContractAddress,amount:U256)"
    assert (
        transfer.signature.hex()
        == "0099cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )


def test_load_eth_abi():
    eth_abi = load_abi("starknet_eth", 2)
    eth_decoder = StarknetAbi.from_json(
        eth_abi,
        "starknet_eth",
        bytes.fromhex("05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed"),
    )


def test_load_wildcard_array_syntax():
    wildcard_abi = load_abi("complex_array", 1)
    decoder = StarknetAbi.from_json(
        wildcard_abi,
        "complex_array",
        bytes.fromhex("0031da92cf5f54bcb81b447e219e2b791b23f3052d12b6c9abd04ff2e5626576"),
    )

    # "data": [
    #     {
    #         "name": "storage_cells_len",
    #         "type": "felt"
    #     },
    #     {
    #         "name": "storage_cells",
    #         "type": "StorageCell*"
    #     }
    # ],

    parsed_event = decoder.events["log_storage_cells"]

    assert len(parsed_event.data) == 1
    assert parsed_event.data["storage_cells"] == StarknetArray(
        StarknetStruct(
            name="StorageCell",
            members=[
                AbiParameter("key", StarknetCoreType.Felt),
                AbiParameter("value", StarknetCoreType.Felt),
            ],
        )
    )
    assert parsed_event.name == "log_storage_cells"


def test_wildcard_size_syntax():
    # felt* syntax length parameter can be calldata_len or calldata_size
    abi_function = {
        "inputs": [
            {"name": "selector", "type": "felt"},
            {"name": "calldata_size", "type": "felt"},
            {"name": "calldata", "type": "felt*"},
        ],
        "name": "__default__",
        "outputs": [
            {"name": "retdata_size", "type": "felt"},
            {"name": "retdata", "type": "felt*"},
        ],
        "type": "function",
    }

    parsed_abi_func = parse_abi_function(abi_function, {})
    assert len(parsed_abi_func.inputs) == 2
    assert parsed_abi_func.inputs[0].name == "selector"
    assert parsed_abi_func.inputs[0].type == StarknetCoreType.Felt
    assert parsed_abi_func.inputs[1].name == "calldata"
    assert parsed_abi_func.inputs[1].type == StarknetArray(StarknetCoreType.Felt)


def test_wildcard_constructor():
    argent_v0_abi = load_abi("argent_v0_proxy", 1)

    abi_decoder = StarknetAbi.from_json(
        argent_v0_abi,
        bytes.fromhex("025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918"),
    )

    assert abi_decoder.constructor.inputs == [
        AbiParameter("implementation", StarknetCoreType.Felt),
        AbiParameter("selector", StarknetCoreType.Felt),
        AbiParameter("calldata", StarknetArray(StarknetCoreType.Felt)),
    ]


def test_no_struct_definition():
    abi_json = json.loads(NO_STRUCT_ABI_DEFINITION)

    decoder = StarknetAbi.from_json(
        abi_json,
        "no_struct",
        bytes.fromhex(NO_STRUCT_CLASS_HASH[2:]),
    )


def test_felt_types():
    abi_json = json.loads(VERSION_0_ABI_DEFINITION)

    decoder = StarknetAbi.from_json(
        abi_json,
        "felt_types",
        bytes.fromhex(VERSION_0_CLASS_HASH[2:]),
    )


def test_parse_event_keys():
    abi_json = load_abi("erc20_key_events", 2)

    parsed_abi = StarknetAbi.from_json(
        abi_json,
        "erc20_key_events",
        bytes.fromhex("0261ad90e1901833f794ee3d69816846f68ddb4fb7bb9ffec2d8f0c8608e298d"),
    )

    approve_event = parsed_abi.events["Approval"]

    assert approve_event.parameters == ["owner", "spender", "value"]
    assert approve_event.keys == {
        "owner": StarknetCoreType.ContractAddress,
        "spender": StarknetCoreType.ContractAddress,
    }

    assert approve_event.data == {"value": StarknetCoreType.U256}
    assert approve_event.name == "Approval"
