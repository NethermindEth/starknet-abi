Releases
========

.. note::
    This library is currently a beta release.  If you experience
    a bug or want to suggest a new feature, raise an issue on Github!


0.0.1 - Starknet ABI Beta Release
---------------------------------

* Parsing Cairo V1 and V2 Abis to Dataclasses for decoding & encoding
* Benchmarks with starknet-py
* Type encoding & decoding

Development TODO
----------------

* Add High-Level Tests for Function & Event Decoding
* Complete Testing for DecodingDispatcher Class
* Optimize the decode & encode if tree
  * The decoding & encoding currently performs if isinstance(decode_type, "StarknetType")
  * The order of these if statements has not been optimized, should be reordered based on ABI Type frequency statistics
* Improve quality of documentation
  * Add Usage Guides covering common use-cases like decoding a specific event for a specific contract
* Improve quality of benchmarks, and add more complex encoding & decoding benchmarks


Possible Future Features
------------------------
* Even faster ABI Decoding through compiled-extensions
  * Rust or Cython decoder implementation


.. admonition:: Contact

    For Direct Questions, reach out to Eli Barbieri on telegram: `@elicbarbieri <https://t.me/elicbarbieri>`_

