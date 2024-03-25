# Starknet ABI

Starknet ABI is a Python library for encoding and decoding StarkNet contract calls and events.

Built for efficient and rapid indexing of StarkNet transactions, Starknet ABI is simple and fast.

## Installation

```bash
pip install starknet-abi
```

## Documentation
[Starkent-ABI Docs](https://nethermindETH.github.io/starknet-abi)


## Features
* Encode and decode StarkNet contract calls and events
* Parse all versions of Cairo ABI JSON into shared datastructure
* Identifying Type strings for each Functions allow you to detect which ABIs have identical types
* Abi Decoding dispatcher
  * Efficiently load thousands of indexed ABIs into memory
  * Decoding Dispatcher Datastructure can be pickled and reused in data pipelines
