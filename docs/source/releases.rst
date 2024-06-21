Releases
========

.. note::
    This library is currently in beta and is under development. If you find a bug or have suggestions for new features, please `open an issue <https://github.com/NethermindEth/starknet-abi/issues/new>`_ or submit a `pull request <https://github.com/NethermindEth/starknet-abi/pulls>`_.

0.0.1 - Starknet ABI Beta Release
---------------------------------

- Parsing Cairo V1 and V2 Abis to dataclasses for decoding and encoding
- Benchmarks with `starknet-py`
- Type encoding and decoding

Development TODO
----------------

- Add high-level tests for function and event decoding
- Complete testing for `DecodingDispatcher` class
- Optimize the decode and encode if tree
  - The decoding and encoding currently performs if `isinstance(decode_type, "StarknetType")`
  - The order of these if statements have not been optimized and should be reordered based on ABI Type frequency statistics
- Improve quality of documentation
  - Add usage guides covering common use cases like decoding a specific event for a specific contract
- Improve the quality of benchmarks and add more complex encoding and decoding benchmarks

Possible future features
------------------------

- Even faster ABI decoding through compiled-extensions
  - Rust or Cython decoder implementation

.. admonition:: Contact

    For direct questions, reach out to Eli Barbieri on Telegram: `@elicbarbieri <https://t.me/elicbarbieri>`_
