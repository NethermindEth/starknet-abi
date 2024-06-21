Installation
============

.. note::
    Once the library is stable, builds will be published to PyPi. In the meantime, you can follow the development installation instructions.

Development installation
------------------------

.. code-block:: console

    git clone https://github.com/nethermindEth/starknet-abi
    cd starknet-abi
    poetry env use python3.12  # Supports any version of python >= 3.10, but 3.12 is the fastest
    poetry install --all-extras

Development guide
-----------------

**Linting & pre-commits**

.. code-block:: console

    poetry run pre-commit install
    poetry run pre-commit run --all-files

**Unit testing**

.. code-block:: console

    poetry run pytest tests/

    # Run only ABI versioning tests
    poetry run pytest tests/test_abi_versions/

**Running doctests**

.. code-block:: console

    poetry run pytest --doctest-modules starknet_abi/

**Building documentation**

.. code-block:: console

    poetry run sphinx-build -b html docs/source/ _build
