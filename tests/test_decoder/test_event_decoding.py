from nethermind.starknet_abi import StarknetAbi
from tests.utils import load_abi


def test_decode_event():
    event_keys = [
        0x0134692B230B9E1FFA39098904722134159652B09C5BC41D88D6698779D228FF,
        0x060CAFC0B0E66067B3A4978E93552DE54E0CAEEB82A352A202E0DC79A41459B6,
        0x04270219D365D6B017231B52E92B3FB5D7C8378B05E9ABC97724537A80E93B0F,
    ]

    event_data = [
        0xC95E3D845779376FED50,
        0x00,
    ]

    abi_json = load_abi("erc20_key_events", 2)

    parsed_abi = StarknetAbi.from_json(
        abi_json,
        bytes.fromhex("0261ad90e1901833f794ee3d69816846f68ddb4fb7bb9ffec2d8f0c8608e298d"),
    )

    abi_event = parsed_abi.events["Approval"]
    decoded_event = abi_event.decode(event_data, event_keys)

    assert decoded_event.data == {
        "owner": "0x060cafc0b0e66067b3a4978e93552de54e0caeeb82a352a202e0dc79a41459b6",
        "spender": "0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f",
        "value": 950934089763838757956944,
    }


def test_decode_wildcard_len_event():
    event_keys = [
        0x025D4F50FFA759476DCB003B1C94B6B1976321CCCEAE5F223696598ED626E9D3,
    ]

    event_data = [
        0x01DEC3416DC353A5B9FA9030016837DF7226F2A8767B786FECD3566E8B57D3C8,
        0x02,
        0x0197948A9994,
        0x0CE31CFE97,
    ]

    abi_json = load_abi("starknet_id_naming", 1)

    parsed_abi = StarknetAbi.from_json(
        abi_json,
        bytes.fromhex("0280601107dd4067877f74b646c903a51852202bf6f5a3c4dda54e367ca16910"),
    )

    abi_event = parsed_abi.events["addr_to_domain_update"]
    decoded_event = abi_event.decode(event_data, event_keys)

    assert decoded_event.data == {
        "address": "0x01dec3416dc353a5b9fa9030016837df7226f2a8767b786fecd3566e8b57d3c8",
        "domain": [
            "0x0197948a9994",
            "0x0ce31cfe97",
        ],
    }
