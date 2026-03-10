import json
from pathlib import Path
from typing import Any, Dict

def load_json(path: Path) -> Any:
    """
    Loads JSON from a file, ensuring UTF-8 encoding.
    Strips BOM if present (utf-8-sig handles this automatically).
    """
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(path: Path, data: Any) -> None:
    """
    Saves data to a JSON file ensuring UTF-8 without BOM.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

def ensure_dir(path: Path) -> None:
    """
    Ensures that a directory exists.
    """
    path.mkdir(parents=True, exist_ok=True)
