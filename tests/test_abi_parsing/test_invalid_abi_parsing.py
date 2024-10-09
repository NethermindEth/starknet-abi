import re

import pytest

from nethermind.starknet_abi.core import StarknetAbi
from nethermind.starknet_abi.exceptions import InvalidAbiError
from tests.utils import load_invalid_abi


def test_abi_cycle_error():
    abi_json = load_invalid_abi("dojo_game")

    with pytest.raises(
        InvalidAbiError,
        match=re.escape(
            "Cyclic Struct Dependencies in ABI: ['dojo::model::layout::FieldLayout', "
            "'dojo::model::layout::Layout', 'dojo::model::layout::FieldLayout']"
        ),
    ):
        StarknetAbi.from_json(
            abi_json,
            "Dojo Game",
            bytes.fromhex("00a349b743d361ce4567361475a89b84a386bb383448c6926954e5fe0b525597"),
        )
