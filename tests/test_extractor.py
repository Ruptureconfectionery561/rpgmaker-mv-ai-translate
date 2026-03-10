import json
from pathlib import Path

import pytest
from rpgmv_translator.extractor import Extractor

@pytest.fixture
def dummy_game_dir(tmp_path: Path):
    data_dir = tmp_path / "www" / "data"
    data_dir.mkdir(parents=True)
    
    # Dummy System.json
    system_data = {
        "gameTitle": "Test Game",
        "currencyUnit": "Gold",
        "terms": {
            "basic": ["Level", "Lv", "HP"],
            "messages": {
                "actionFailure": "There was no effect!",
                "levelUp": "%1 is now %2 %3!"
            }
        },
        "armorTypes": ["General Armor", "Magic Armor"],
        "variables": ["", "TestVar1", "TestVar2"] # Empty string should be ignored
    }
    with open(data_dir / "System.json", "w", encoding="utf-8") as f:
        json.dump(system_data, f)
        
    # Dummy Map001.json
    map_data = {
        "events": [
            None,
            {
                "id": 1,
                "name": "NPC",
                "note": "A regular NPC",
                "pages": [
                    {
                        "list": [
                            {"code": 401, "parameters": ["Hello..."]},
                            {"code": 401, "parameters": ["Welcome to town!"]},
                            {"code": 102, "parameters": [["Yes", "No"], 1, 0, 0, 0]},
                            {"code": 0, "parameters": []}
                        ]
                    }
                ]
            }
        ]
    }
    with open(data_dir / "Map001.json", "w", encoding="utf-8") as f:
        json.dump(map_data, f)
        
    return tmp_path

def test_extract_all(dummy_game_dir: Path):
    extractor = Extractor(dummy_game_dir)
    entries = extractor.extract_all()
    
    # We should have extracted:
    # System.json: gameTitle, currencyUnit, basic (3), actionFailure, levelUp, armorTypes (2), variables (2)
    # Map001.json: name, note, merged 401s (1), choices (2)
    # Total = 1 + 1 + 3 + 1 + 1 + 2 + 2 + 1 + 1 + 1 + 2 = 16 (Wait, let's verify precisely)
    
    texts = [e.original_text for e in entries]
    
    # DB tests (System.json)
    assert "Test Game" in texts
    assert "Gold" in texts
    assert "Level" in texts
    assert "There was no effect!" in texts
    assert "Magic Armor" in texts
    assert "TestVar1" in texts
    assert "" not in texts # Should ignore empty strings
    
    # Event tests (Map001.json)
    assert "Hello...\nWelcome to town!" in texts  # Merged 401s
    assert "Yes" in texts
    assert "No" in texts
    
    # Let's verify paths specifically for merged 401s
    merged_entry = next(e for e in entries if e.original_text == "Hello...\nWelcome to town!")
    # The start_idx was 0. So path should end with [0, 'parameters', 0, 'MERGED', 2]
    assert merged_entry.json_path[-5:] == [0, "parameters", 0, "MERGED", 2]
    
def test_missing_data_dir(tmp_path: Path):
    extractor = Extractor(tmp_path)
    entries = extractor.extract_all()
    assert len(entries) == 0
