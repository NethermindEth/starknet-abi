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

### Decode transaction calldata

1. Decode core types:

```python
>>> from starknet_abi.decode import decode_core_type, StarknetCoreType
>>> decode_core_type(StarknetCoreType.Bool, [0])
False
>>> decode_core_type(StarknetCoreType.U256, [12345, 0])
12345
>>> decode_core_type(StarknetCoreType.Felt, [256])
'0x0000000000000000000000000000000000000000000000000000000000000100'
```

2. Decode from parameters:

```python
>>> from starknet_abi.decode import decode_from_params, StarknetCoreType, AbiParameter
>>> decode_from_params(
        [AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
        [123456, 654321]
    )
{'a': 123456, 'b': 654321}
```

3. Decode from types:

```python
>>> from starknet_abi.decode import decode_from_types, StarknetCoreType, StarknetArray
>>> decode_from_types([StarknetArray(StarknetCoreType.U8), StarknetCoreType.Bool], [3, 123, 244, 210, 0])
[[123, 244, 210], False]
>>> decode_from_types(
        [StarknetCoreType.ContractAddress, StarknetCoreType.U256, StarknetCoreType.Bool],
        [0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 250_000, 0, 1]
    )
['0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', 250000, True]
```

### Encode transaction calldata

1. Encode core types:

```python
>>> from starknet_abi.encode import encode_core_type, StarknetCoreType
>>> encode_core_type(StarknetCoreType.Bool, False)
[0]
>>> encode_core_type(StarknetCoreType.U256, 12345)
[12345, 0]
>>> encode_core_type(StarknetCoreType.Felt, "0x0000000000000000000000000000000000000000000000000000000000000100")
[256]
```

2. Encode from parameters:

```python
>>> from starknet_abi.encode import encode_from_params, StarknetCoreType, AbiParameter
>>> encode_from_params(
        [AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
        {"a": 123456, "b": 654321}
    )
[123456, 654321]
```

3. Encode from types:

```python
>>> from starknet_abi.encode import encode_from_types, StarknetCoreType, StarknetArray
>>> encode_from_types([StarknetArray(StarknetCoreType.U8), StarknetCoreType.Bool], [[123, 244, 210], False])
[3, 123, 244, 210, 0]
>>> encode_from_types(
        [StarknetCoreType.ContractAddress, StarknetCoreType.U256, StarknetCoreType.Bool],
        ["0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 250000, True]
    )
[2087021424722619777119509474943472645767659996348769578120564519014510906823, 250000, 0, 1]
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
