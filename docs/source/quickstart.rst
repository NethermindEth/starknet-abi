.. _quickstart:

Quickstart
==========

This guide will help you get started with parsing Starknet ABI JSON and encode and decode transaction calldata. Refer to the :ref:`Installation guide <installation>` for instructions on installing the Starknet ABI library.

Parse Starknet ABI JSON
-----------------------

1. Get the `Starknet-ETH ABI JSON <https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed>`_ from Voyager and save it to a file named `abi.json`.
2. Create a `StarknetABI` instance from the ABI JSON file:

.. code-block:: python

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

Decode transaction calldata
---------------------------

1. Decode core types:

.. code-block:: python

    >>> from starknet_abi.decode import decode_core_type, StarknetCoreType
    >>> decode_core_type(StarknetCoreType.Bool, [0])
    False
    >>> decode_core_type(StarknetCoreType.U256, [12345, 0])
    12345
    >>> decode_core_type(StarknetCoreType.Felt, [256])
    '0x0000000000000000000000000000000000000000000000000000000000000100'

2. Decode from parameters:

.. code-block:: python

    >>> from starknet_abi.decode import AbiParameter, decode_from_params, StarknetCoreType
    >>> decode_from_params(
    ...     [AbiParameter("a", StarknetCoreType.U32), AbiParameter("b", StarknetCoreType.U32)],
    ...     [123456, 654321]
    ... )
    {'a': 123456, 'b': 654321}

3. Decode from types:

.. code-block:: python

    >>> from starknet_abi.decode import decode_from_types, StarknetCoreType, StarknetArray
    >>> decode_from_types([StarknetArray(StarknetCoreType.U8), StarknetCoreType.Bool], [3, 123, 244, 210, 0])
    [[123, 244, 210], False]
    >>> decode_from_types(
    ...     [StarknetCoreType.ContractAddress, StarknetCoreType.U256, StarknetCoreType.Bool],
    ...     [0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 250_000, 0, 1]
    ... )
    ['0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', 250000, True]

Encode transaction calldata
---------------------------

.. _Starknet-ETH: https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed
