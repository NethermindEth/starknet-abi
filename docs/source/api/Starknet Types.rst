Starknet Types
==============

Python Representations of Starknet Types that are present in ABIs.  Parsing Functions
convert ABI Json into these Python Types.  Multiple versions of Cairo ABIs are parsed into
the same format to make decoding and encoding seamless across versions, requiring only the
ABI Parsing logic to change across versions


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

