.. _quickstart:

Quickstart
==========

Setup
-----

1. Install the package:
    :ref:`Install <Installation>` the library

2. Get the `Starknet-ETH`_ ABI JSON from Voyager & Save to File `abi.json`:

3.  Create a StarknetABI Instance from the ABI JSON

.. code-block:: python

    import json
    from starknet_abi import StarknetABI

    with open('abi.json') as f:
        raw_abi = json.load(f)

    starknet_eth_abi = StarknetABI.from_json(raw_abi)

4.  Decode Transaction Calldata for `Starknet-ETH`_

.. code-block:: python

    decoded_transfer = starknet_eth_abi.decode_for_entry_point(
        entry_point='0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e',
        calldata=[
            "0x7916596feab669322f03b6df4e71f7b158e291fd8d273c0e53759d5b7240b4a",
            "0x116933ea5369f0",
            "0x0",
        ]
    )
    print(decoded_transfer)


.. _Starknet-ETH: https://voyager.online/class/0x05ffbcfeb50d200a0677c48a129a11245a3fc519d1d98d76882d1c9a1b19c6ed