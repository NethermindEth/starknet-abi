# Starknet ABI

Starknet ABI is a Python library for encoding and decoding Starknet contract calls and events. It is built for efficient and rapid indexing of Starknet transactions, offering simplicity and speed.

## Installation

To install Starknet ABI, run the following command:

```bash
python -m pip install starknet-abi
```

## Documentation

For detailed usage and API documentation, visit the [Starknet-ABI Docs](https://nethermindETH.github.io/starknet-abi).

## Features

- **Encode and Decode**: Easily encode and decode Starknet contract calls and events.
- **Comprehensive Parsing**: Parse all versions of Cairo ABI JSON into a shared data structure.
- **Type Identification**: Identify type strings for each function, enabling the detection of ABIs with identical types.
- **ABI Decoding Dispatcher**:
  - Efficiently load thousands of indexed ABIs into memory.
  - Pickle and reuse the decoding dispatcher data structure in data pipelines.
