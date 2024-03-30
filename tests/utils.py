import json
from pathlib import Path
from typing import Any

PARENT_DIR = Path(__file__).parent


def load_abi(abi_name: str, abi_version: int = 2) -> Any:
    with open(PARENT_DIR / "abis" / f"v{abi_version}" / f"{abi_name}.json") as f:
        return json.load(f)
