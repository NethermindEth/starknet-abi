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
        "erc20_key_events",
        bytes.fromhex(
            "0261ad90e1901833f794ee3d69816846f68ddb4fb7bb9ffec2d8f0c8608e298d"
        ),
    )

    abi_event = parsed_abi.events["Approval"]
    decoded_event = abi_event.decode(event_data, event_keys)

    assert decoded_event.data == {
        "owner": "0x060cafc0b0e66067b3a4978e93552de54e0caeeb82a352a202e0dc79a41459b6",
        "spender": "0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f",
        "value": 950934089763838757956944,
    }
