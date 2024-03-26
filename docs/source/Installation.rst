.. _installation:

Installation
============

.. note::
    As soon as the library is stable, builds will be published to PyPi.  Until then, the development installation
    instructions below can be used.


Development Installation
------------------------

.. code-block:: console

    git clone https://github.com/nethermindETH/starknet-abi.git
    cd starknet-abi
    poetry env use python3.12  # Supports any version of python >= 3.10, but 3.12 is fastest
    poetry install --all-extras


Development Guide
-----------------

**Linting & Pre-commits**

.. code-block:: console

    poetry run pre-commit install
    poetry run pre-commit run --all-files

**Unit Testing**

.. code-block:: console

    poetry run pytest tests/

    # Run only ABI Versioning Tests
    poetry run pytest tests/test_abi_versions/

**Running Doctests**

.. code-block:: console

    poetry run pytest --doctest-modules starknet_abi/

**Building Documentation**

.. code-block:: console

    poetry run sphinx-build -b html docs/source/ _build
