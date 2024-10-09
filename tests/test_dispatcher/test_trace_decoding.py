from nethermind.starknet_abi.dispatch import DecodingDispatcher, StarknetAbi
from tests.utils import load_abi


def test_legacy_trace_result():
    # Transaction: 0x01eaebf1a9ff736c78d07b4948ad446ea179351d39b4ddcd9cc68a027fc23683
    # Class Hash:  0x033434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
    # Funnction: __execute__() -> ([felt])
    dispatcher = DecodingDispatcher()

    abi_class = bytes.fromhex("033434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2")
    abi_json = load_abi("argent_v0", 1)

    argent_abi = StarknetAbi.from_json(abi_json, abi_class, "argent_v0")

    dispatcher.add_abi(argent_abi)

    calldata = [
        0x03,
        0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7,
        0x83AFD3F4CAEDC6EEBF44246FE54E38C95E3179A5EC9EA81740ECA5B482D12E,
        0x00,
        0x03,
        0x02E0AF29598B407C8716B17F6D2795ECA1B471413FA03FB145A5E33722184067,
        0x038C3244E92DA3BEC5E017783C62779E3FD5D13827570DC093AB2A55F16D41B9,
        0x03,
        0x0A,
        0x02E0AF29598B407C8716B17F6D2795ECA1B471413FA03FB145A5E33722184067,
        0x0292F3F4DF7749C2AE1FDC3379303C2E6CAA9BBC3033EE67709FDE5B77F65836,
        0x0D,
        0x01,
        0x0E,
        0x02E0AF29598B407C8716B17F6D2795ECA1B471413FA03FB145A5E33722184067,
        0x067D14111A060000,
        0x00,
        0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7,
        0x053C91253BC9682C04929CA02ED00B3E423F6710D2EE7E0D5EBB06F3ECF368A8,
        0x00,
        0x01,
        0x00,
        0x0126C6E8,
        0x01,
        0x012541F6,
        0x01,
        0x00,
        0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7,
    ]
    result = [0x01, 0x046CB2, 0x022EE84C7A1290, 0x5B, 0x00]

    selector = bytes.fromhex("015d40a3d6ca2ac30f4031e42be28da9b056fef9bb7357ac5e85627ee876e5ad")

    decoding_res = dispatcher.decode_function(calldata, result, selector, abi_class)

    assert decoding_res is not None

    assert decoding_res.outputs == [
        "0x01",
        "0x046cb2",
        "0x022ee84c7a1290",
        "0x5b",
        "0x00",
    ]

    assert decoding_res.inputs == {
        "call_array": [
            {
                "to": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
                "selector": "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",
                "data_offset": "0x00",
                "data_len": "0x03",
            },
            {
                "to": "0x02e0af29598b407c8716b17f6d2795eca1b471413fa03fb145a5e33722184067",
                "selector": "0x038c3244e92da3bec5e017783c62779e3fd5d13827570dc093ab2a55f16d41b9",
                "data_offset": "0x03",
                "data_len": "0x0a",
            },
            {
                "to": "0x02e0af29598b407c8716b17f6d2795eca1b471413fa03fb145a5e33722184067",
                "selector": "0x0292f3f4df7749c2ae1fdc3379303c2e6caa9bbc3033ee67709fde5b77f65836",
                "data_offset": "0x0d",
                "data_len": "0x01",
            },
        ],
        "calldata": [
            "0x02e0af29598b407c8716b17f6d2795eca1b471413fa03fb145a5e33722184067",
            "0x067d14111a060000",
            "0x00",
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
            "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
            "0x00",
            "0x01",
            "0x00",
            "0x0126c6e8",
            "0x01",
            "0x012541f6",
            "0x01",
            "0x00",
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
        ],
    }
