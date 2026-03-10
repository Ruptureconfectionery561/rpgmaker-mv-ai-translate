import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any
from .models import TextEntry
from .utils.file_utils import load_json, save_json, ensure_dir
from .utils.text_utils import wrap_text

logger = logging.getLogger(__name__)

class Reinjector:
    """
    Reinjets translated text back into the original JSON files.
    Safely navigates the JSON schema without altering the structural layout.
    """
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def inject_all(self, entries: List[TextEntry], translations: List[str]) -> None:
        """
        Takes translated entries and saves the modified files to the output directory.
        """
        # Group entries by file to minimize I/O
        file_map: Dict[str, list[tuple[TextEntry, str]]] = {}
        for entry, trans in zip(entries, translations):
            if entry.file_path not in file_map:
                file_map[entry.file_path] = []
            file_map[entry.file_path].append((entry, trans))
            
        logger.info(f"Injecting into {len(file_map)} files...")
            
        for file_path_str, items in file_map.items():
            input_file = Path(file_path_str)
            
            # Determine relative path from input game_dir to this file
            try:
                rel_path = input_file.relative_to(self.input_dir)
            except ValueError:
                rel_path = Path(input_file.name)
                
            output_file = self.output_dir / rel_path
            ensure_dir(output_file.parent)
            
            data = load_json(input_file)
            
            # Sort items by JSON path downwards, or specifically handle MERGED deletions from bottom-up
            # to avoid index shifting in arrays if we delete nodes. 
            # We don't actually delete nodes to keep it safe; we overwrite 401s and turn extras into Code 0 (No Op)
            # we can safely resize the event list. Modifying lists in place requires care.
            
            def sort_key(item):
                return [(0, k) if isinstance(k, int) else (1, k) for k in item[0].json_path]
            
            items.sort(key=sort_key, reverse=True)
            
            for entry, trans in items:
                try:
                    self._inject_single(data, entry.json_path, trans)
                except TypeError as e:
                    logger.error(f"Failed to inject entry in file {file_path_str} at path {entry.json_path}")
                    raise
            save_json(output_file, data)
            logger.debug(f"Saved {output_file}")

    def _inject_single(self, root: Any, path: List[Any], translated_text: str) -> None:
        target = root
        
        # Check if this is a MERGED event path
        if len(path) >= 5 and path[-2] == "MERGED":
            translated_text = wrap_text(translated_text)
            
            merge_count = path[-1]
            start_idx = path[-5]
            
            # Navigate to the containing list
            for key in path[:-5]:
                target = target[key]
                
            event_list = target # This is the "list" array
            
            lines = translated_text.split('\n')
            
            # Replace the first 401 command's parameter
            event_list[start_idx]["parameters"][0] = lines[0] if len(lines) > 0 else ""
            
            # Create additional 401 commands if translation has more lines than original
            # OR modify the existing consecutive 401 commands
            
            current_idx = start_idx + 1
            line_idx = 1
            
            # Replace existing consecutive 401s
            while line_idx < len(lines) and line_idx < merge_count:
                event_list[current_idx]["parameters"][0] = lines[line_idx]
                current_idx += 1
                line_idx += 1
                
            # If translation is longer than original, insert new 401 commands
            while line_idx < len(lines):
                new_cmd = {
                    "code": 401,
                    "indent": event_list[start_idx].get("indent", 0),
                    "parameters": [lines[line_idx]]
                }
                event_list.insert(current_idx, new_cmd)
                current_idx += 1
                line_idx += 1
                
            # If translation is shorter than original, turn the unused 401s into comments (code 108) or blank 401s
            while line_idx < merge_count:
                event_list[current_idx]["code"] = 108  # Comment
                event_list[current_idx]["parameters"] = [""]
                current_idx += 1
                line_idx += 1
                
            return

        # Standard injection
        for key in path[:-1]:
            if isinstance(target, str):
                logger.error(f"Target evaluated to a string prematurely at key {key} in path {path}")
            target = target[key]
            
        try:
            target[path[-1]] = translated_text
        except TypeError as e:
            logger.error(f"TypeError during injection! Path: {path}. Target type: {type(target)}. Target data: {target}")
            raise

    def copy_unmodified_assets(self) -> None:
        """
        Copies any files from the input directory to the output directory that were not modified.
        This ensures the output directory is a fully playable copy of the game.
        """
        logger.info("Copying unmodified game assets to output directory...")
        
        def copy_if_needed(src: Path, dst: Path):
            if src.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
                for item in src.iterdir():
                    copy_if_needed(item, dst / item.name)
            else:
                if not dst.exists():
                    shutil.copy2(src, dst)

        copy_if_needed(self.input_dir, self.output_dir)
