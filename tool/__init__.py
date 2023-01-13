from __future__ import annotations

import os.path
from pathlib import Path

from config import settings


def validate(path: Path):
    if not os.path.exists(path) and settings.debug:
        raise FileNotFoundError(path)
    elif os.path.exists(path):
        return path
    else:
        return ""


base_dir = Path(__file__).resolve().parent

foundry_anvil = validate(base_dir / "foundry" / "anvil.exe")
foundry_anvil_json = base_dir / "foundry" / "anvil.json"

foundry_cast = validate(base_dir / "foundry" / "cast.exe")
foundry_forge = validate(base_dir / "foundry" / "forge.exe")
foundry_chisel = validate(base_dir / "foundry" / "chisel.exe")
