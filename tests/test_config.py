import json
from pathlib import Path

import pytest
from rpgmv_translator.config import TranslationConfig

def test_config_defaults():
    config = TranslationConfig()
    assert config.provider == "ollama"
    assert config.model == "llama3"
    assert config.batch_size == 10
    assert config.max_retries == 3

def test_config_load_success(tmp_path: Path):
    config_file = tmp_path / "config.json"
    data = {
        "provider": "openai",
        "model": "gpt-4o",
        "batch_size": 20
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    config = TranslationConfig.load(config_file)
    assert config.provider == "openai"
    assert config.model == "gpt-4o"
    assert config.batch_size == 20
    # ensure defaults are kept for missing keys
    assert config.max_retries == 3

def test_config_load_unknown_keys(tmp_path: Path):
    config_file = tmp_path / "config.json"
    data = {
        "provider": "mock",
        "unknown_key_123": "value"
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    config = TranslationConfig.load(config_file)
    assert config.provider == "mock"
    assert not hasattr(config, "unknown_key_123")

def test_config_load_missing_file():
    config = TranslationConfig.load(Path("non_existent_file_999.json"))
    assert config.provider == "ollama"  # Should fall back to default

def test_config_save_defaults(tmp_path: Path):
    config_file = tmp_path / "out_config.json"
    config = TranslationConfig()
    config.provider = "custom_provider"
    
    config.save_defaults(config_file)
    assert config_file.exists()
    
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["provider"] == "custom_provider"
    assert data["model"] == "llama3"
