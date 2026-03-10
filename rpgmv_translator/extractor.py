import os
from pathlib import Path
from typing import List, Any
import logging
from .models import TextEntry
from .utils.file_utils import load_json

logger = logging.getLogger(__name__)

class Extractor:
    """
    Scans an RPG Maker MV project to extract translatable text.
    Target files: www/data/MapXXX.json, CommonEvents.json, and Database files.
    """
    
    TARGET_KEYS = {"name", "description", "note", "nickname", "profile", "message1", "message2", "message3", "message4", "gameTitle", "currencyUnit"}

    def __init__(self, game_dir: Path):
        self.game_dir = game_dir
        if (game_dir / "www" / "data").exists():
            self.data_dir = game_dir / "www" / "data"
        else:
            self.data_dir = game_dir / "data"

    def extract_all(self) -> List[TextEntry]:
        if not self.data_dir.exists():
            logger.error(f"Data directory not found at {self.data_dir}")
            return []
            
        entries: List[TextEntry] = []
        for file_path in self.data_dir.glob("*.json"):
            filename = file_path.name
            
            if filename.startswith("Map") or filename == "CommonEvents.json" or filename == "Troops.json":
                entries.extend(self._extract_events_from_file(file_path))
            else:
                entries.extend(self._extract_db_from_file(file_path))
                
        logger.info(f"Extracted a total of {len(entries)} text entries.")
        return entries

    def _extract_db_from_file(self, file_path: Path) -> List[TextEntry]:
        entries = []
        try:
            data = load_json(file_path)
        except Exception as e:
            logger.warning(f"Failed to load {file_path.name}: {e}")
            return entries

        file_str = str(file_path)

        def walk(obj: Any, path: List[Any]):
            if isinstance(obj, dict):
                # Specific check for System.json terms.messages
                if file_path.name == "System.json" and len(path) == 2 and path[0] == "terms" and path[1] == "messages":
                    for k, v in obj.items():
                        if isinstance(v, str) and v.strip():
                            entries.append(TextEntry(file_path=file_str, json_path=path + [k], original_text=v))
                    return

                for k, v in obj.items():
                    if k in self.TARGET_KEYS and isinstance(v, str) and v.strip():
                        entries.append(TextEntry(file_path=file_str, json_path=path + [k], original_text=v))
                    elif isinstance(v, (dict, list)):
                        walk(v, path + [k])
            elif isinstance(obj, list):
                # Terms in System.json are often lists of strings
                is_system_list = (
                    file_path.name == "System.json" and len(path) > 0 and 
                    path[-1] in {"elements", "skillTypes", "weaponTypes", "armorTypes", "equipTypes", "switches", "variables"}
                )
                is_terms_list = (
                    file_path.name == "System.json" and len(path) == 2 and 
                    path[0] == "terms" and path[1] in {"basic", "commands", "params"}
                )
                
                if is_system_list or is_terms_list:
                    for i, item in enumerate(obj):
                        if isinstance(item, str) and item.strip():
                            entries.append(TextEntry(file_path=file_str, json_path=path + [i], original_text=item))
                else:
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            walk(item, path + [i])

        walk(data, [])
        return entries

    def _extract_events_from_file(self, file_path: Path) -> List[TextEntry]:
        entries = []
        try:
            data = load_json(file_path)
        except Exception as e:
            logger.warning(f"Failed to load {file_path.name}: {e}")
            return entries

        file_str = str(file_path)

        def process_event_list(cmd_list: List[dict], base_path: List[Any]):
            i = 0
            while i < len(cmd_list):
                cmd = cmd_list[i]
                if not isinstance(cmd, dict):
                    i += 1
                    continue
                    
                code = cmd.get("code")
                params = cmd.get("parameters", [])
                
                # 401: Dialogue line
                if code == 401 and params and isinstance(params[0], str) and params[0].strip():
                    merged_text = params[0]
                    start_idx = i
                    j = i + 1
                    
                    # Merge consecutive 401 commands into one block
                    while j < len(cmd_list):
                        next_cmd = cmd_list[j]
                        if not isinstance(next_cmd, dict) or next_cmd.get("code") != 401:
                            break
                        next_params = next_cmd.get("parameters", [])
                        if next_params and isinstance(next_params[0], str):
                            merged_text += "\n" + next_params[0]
                        j += 1
                    
                    if merged_text.strip():
                        # We store the path to the FIRST 401 command. 
                        # The reinjector must know to replace this block and delete subsequent merged 401s if necessary.
                        entries.append(TextEntry(
                            file_path=file_str, 
                            json_path=base_path + [start_idx, "parameters", 0, "MERGED", j - start_idx], 
                            original_text=merged_text
                        ))
                    i = j - 1
                    
                # 102: Choices
                elif code == 102 and params and isinstance(params[0], list):
                    choices = params[0]
                    for c_idx, choice in enumerate(choices):
                        if isinstance(choice, str) and choice.strip():
                            entries.append(TextEntry(
                                file_path=file_str,
                                json_path=base_path + [i, "parameters", 0, c_idx],
                                original_text=choice
                            ))
                            
                # Note: code 101 is Face/Name. The name is often at params[4] in modern MV plugins, 
                # but standard MV doesn't translate names in 101. We'll stick to strictly necessary strings.
                            
                i += 1

        def search_for_lists(obj: Any, path: List[Any]):
            if isinstance(obj, dict):
                # An event page has a "list" of commands
                if "list" in obj and isinstance(obj["list"], list) and len(obj["list"]) > 0 and isinstance(obj["list"][0], dict) and "code" in obj["list"][0]:
                    process_event_list(obj["list"], path + ["list"])
                else:
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            search_for_lists(v, path + [k])
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        search_for_lists(item, path + [i])

        search_for_lists(data, [])
        return entries
