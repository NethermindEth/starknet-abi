Starknet Types
==============

Python representations of Starknet Types used in ABIs. Parsing functions convert ABI JSON into these Python types. Multiple versions of Cairo ABIs are parsed into the same format, ensuring seamless decoding and encoding across different versions, requiring only the ABI parsing logic to be updated for each new version.

.. autoclass:: starknet_abi.abi_types.StarknetCoreType
    :members:
    :exclude-members: __init__

.. autoclass:: starknet_abi.abi_types.StarknetArray
    :members:
    :exclude-members: __init__

.. autoclass:: starknet_abi.abi_types.StarknetOption
    :members:
    :exclude-members: __init__

.. autoclass:: starknet_abi.abi_types.StarknetTuple
    :members:
    :exclude-members: __init__

.. autoclass:: starknet_abi.abi_types.StarknetEnum
    :members:
    :exclude-members: __init__

.. autoclass:: starknet_abi.abi_types.StarknetStruct
    :members:
    :exclude-members: __init__
