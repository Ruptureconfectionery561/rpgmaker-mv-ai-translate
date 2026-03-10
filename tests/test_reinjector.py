import json
from pathlib import Path

import pytest
from rpgmv_translator.reinjector import Reinjector
from rpgmv_translator.models import TextEntry

@pytest.fixture
def dummy_reinjector_env(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    
    data_dir = input_dir / "www" / "data"
    data_dir.mkdir(parents=True)
    
    # Simple JSON for standard injection
    system_data = {"gameTitle": "Test Game", "currencyUnit": "G"}
    with open(data_dir / "System.json", "w", encoding="utf-8") as f:
        json.dump(system_data, f)
        
    # Complex JSON for MERGED event injection
    map_data = {
        "events": [
            None,
            {
                "pages": [
                    {
                        "list": [
                            {"code": 401, "parameters": ["Line 1"]},
                            {"code": 401, "parameters": ["Line 2"]},
                            {"code": 0, "parameters": []}
                        ]
                    }
                ]
            }
        ]
    }
    with open(data_dir / "Map001.json", "w", encoding="utf-8") as f:
        json.dump(map_data, f)
        
    output_dir = tmp_path / "output"
    return input_dir, output_dir

def test_inject_simple(dummy_reinjector_env):
    input_dir, output_dir = dummy_reinjector_env
    reinjector = Reinjector(input_dir, output_dir)
    
    entries = [
        TextEntry(file_path=str(input_dir / "www/data/System.json"), json_path=["gameTitle"], original_text="Test Game"),
        TextEntry(file_path=str(input_dir / "www/data/System.json"), json_path=["currencyUnit"], original_text="G")
    ]
    translations = ["Translated Game", "Gold"]
    
    reinjector.inject_all(entries, translations)
    
    with open(output_dir / "www/data/System.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["gameTitle"] == "Translated Game"
    assert data["currencyUnit"] == "Gold"

def test_inject_merged_events_same_lines(dummy_reinjector_env):
    input_dir, output_dir = dummy_reinjector_env
    reinjector = Reinjector(input_dir, output_dir)
    
    # Original is 2 lines (idx 0 to 2)
    entries = [
        TextEntry(file_path=str(input_dir / "www/data/Map001.json"), 
                  json_path=["events", 1, "pages", 0, "list", 0, "parameters", 0, "MERGED", 2], 
                  original_text="Line 1\nLine 2")
    ]
    translations = ["Translated 1\nTranslated 2"]
    
    reinjector.inject_all(entries, translations)
    
    with open(output_dir / "www/data/Map001.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    event_list = data["events"][1]["pages"][0]["list"]
    assert event_list[0]["parameters"][0] == "Translated 1"
    assert event_list[1]["parameters"][0] == "Translated 2"
    assert event_list[2]["code"] == 0

def test_inject_merged_events_more_lines(dummy_reinjector_env):
    input_dir, output_dir = dummy_reinjector_env
    reinjector = Reinjector(input_dir, output_dir)
    
    # Original is 2 lines
    entries = [
        TextEntry(file_path=str(input_dir / "www/data/Map001.json"), 
                  json_path=["events", 1, "pages", 0, "list", 0, "parameters", 0, "MERGED", 2], 
                  original_text="Line 1\nLine 2")
    ]
    translations = ["Translated 1\nTranslated 2\nTranslated 3"]
    
    reinjector.inject_all(entries, translations)
    
    with open(output_dir / "www/data/Map001.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    event_list = data["events"][1]["pages"][0]["list"]
    assert event_list[0]["parameters"][0] == "Translated 1"
    assert event_list[1]["parameters"][0] == "Translated 2"
    assert event_list[2]["parameters"][0] == "Translated 3"
    assert event_list[2]["code"] == 401
    assert event_list[3]["code"] == 0

def test_inject_merged_events_fewer_lines(dummy_reinjector_env):
    input_dir, output_dir = dummy_reinjector_env
    reinjector = Reinjector(input_dir, output_dir)
    
    # Original is 2 lines
    entries = [
        TextEntry(file_path=str(input_dir / "www/data/Map001.json"), 
                  json_path=["events", 1, "pages", 0, "list", 0, "parameters", 0, "MERGED", 2], 
                  original_text="Line 1\nLine 2")
    ]
    # Single line translation
    translations = ["Translated Only 1"]
    
    reinjector.inject_all(entries, translations)
    
    with open(output_dir / "www/data/Map001.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    event_list = data["events"][1]["pages"][0]["list"]
    assert event_list[0]["parameters"][0] == "Translated Only 1"
    assert event_list[1]["code"] == 108  # Overwritten as comment
    assert event_list[2]["code"] == 0

def test_copy_unmodified_assets(dummy_reinjector_env):
    input_dir, output_dir = dummy_reinjector_env
    
    # Create an extra file that isn't touched by translation
    (input_dir / "www/img").mkdir(parents=True)
    with open(input_dir / "www/img/test.png", "w") as f:
        f.write("fake image data")
        
    reinjector = Reinjector(input_dir, output_dir)
    reinjector.copy_unmodified_assets()
    
    assert (output_dir / "www/img/test.png").exists()
    assert (output_dir / "www/data/System.json").exists()
