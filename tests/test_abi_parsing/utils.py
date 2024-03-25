import json
from typing import Any, Literal

from tests.utils import PARENT_DIR


def get_abis_for_version(
    abi_version: Literal["v1", "v2"]
) -> list[tuple[str, list[dict[str, Any]]]]:
    """
    Load ABIs for a given version.

    :param abi_version: version of ABIs to load

    :return: [abi_names], [abi_json_data]
    """
    return_data = []

    abi_dir = PARENT_DIR / "abis" / abi_version

    for abi_json_path in abi_dir.iterdir():
        if abi_json_path.suffix == ".json":
            with open(abi_json_path) as f:
                return_data.append((abi_json_path.stem, json.load(f)))

    return return_data
