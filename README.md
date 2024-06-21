# Starknet ABI

Starknet ABI is a Python library for encoding and decoding Starknet contract calls and events. It is built for efficient and rapid indexing of Starknet transactions, offering simplicity and speed.

## Installation

Once the library is stable, builds will be published to PyPi. In the meantime, you can follow the development installation instructions:

```bash
git clone https://github.com/nethermindEth/starknet-abi
cd starknet-abi
poetry env use python3.12  # Supports any version of python >= 3.10, but 3.12 is the fastest
poetry install --all-extras
```

## Quickstart

### Parse Starknet ABI JSON

1. Get the [Starknet-ETH ABI JSON](https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed) from Voyager and save it to a file named `abi.json`.
2. Create a `StarknetABI` instance from the ABI JSON file:

```python
import json
from starknet_abi.core import StarknetAbi

with open("abi.json") as f:
    raw_abi = json.load(f)

# Create a StarknetABI instance
starknet_eth_abi = StarknetAbi.from_json(raw_abi, "starknet_eth", b"")

# View the ABI functions
print(starknet_eth_abi.functions)

# View the ABI implemented interfaces
print(starknet_eth_abi.implemented_interfaces)
```

For detailed usage and API documentation, visit the [Starknet-ABI Docs](https://nethermindEth.github.io/starknet-abi).

## Features

- **Encode and Decode**: Easily encode and decode Starknet contract calls and events.
- **Comprehensive Parsing**: Parse all versions of Cairo ABI JSON into a shared data structure.
- **Type Identification**: Identify type strings for each function, enabling the detection of ABIs with identical types.
- **ABI Decoding Dispatcher**:
  - Efficiently load thousands of indexed ABIs into memory.
  - Pickle and reuse the decoding dispatcher data structure in data pipelines.

## Contributing

We value community contributions and are eager to support your involvement. If you encounter any bugs or have suggestions for new features, please [open an issue](https://github.com/NethermindEth/starknet-abi/issues/new) or submit a [pull request](https://github.com/NethermindEth/starknet-abi/pulls).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
