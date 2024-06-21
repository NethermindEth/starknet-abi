.. _quickstart:

Quickstart
==========

This guide will help you create a StarknetABI instance and encode and decode transaction calldata. Look at the :ref:`Installation guide <installation>` for instructions on installing the Starknet ABI library.

Parse Starknet ABI JSON
-----------------------

Get the `Starknet-ETH ABI JSON <https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed>`_ from Voyager and save it to a file named `abi.json`. Then, create a `StarknetABI` instance from the ABI JSON file:

.. code-block:: python

    import json
    from starknet_abi.core import StarknetAbi

    with open("abi.json") as f:
        raw_abi = json.load(f)

    # Create StarknetABI instance
    starknet_eth_abi = StarknetAbi.from_json(raw_abi, "starknet_eth", b"")

    # View the ABI functions
    print(starknet_eth_abi.functions)

    # View the ABI implemented interfaces
    print(starknet_eth_abi.implemented_interfaces)

Encode transaction calldata
---------------------------

Decode transaction calldata
---------------------------

.. _Starknet-ETH: https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed
