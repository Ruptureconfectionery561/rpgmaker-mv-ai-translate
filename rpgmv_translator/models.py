from dataclasses import dataclass
from typing import List, Union

@dataclass
class TextEntry:
    """Represents a discrete string of translatable text located within a file."""
    file_path: str
    json_path: List[Union[str, int]]
    original_text: str
