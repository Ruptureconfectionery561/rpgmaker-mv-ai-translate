import json
from pathlib import Path

import pytest
from rpgmv_translator.cache import TranslationCache

def test_cache_set_and_get(tmp_path: Path):
    cache = TranslationCache(tmp_path, "test_cache")
    
    cache.set("Hello", "Bonjour")
    cache.set("World", "Monde")
    
    assert cache.get("Hello") == "Bonjour"
    assert cache.get("World") == "Monde"
    assert cache.get("Unknown") is None

def test_cache_save_and_load(tmp_path: Path):
    cache = TranslationCache(tmp_path, "test_cache")
    cache.set("Hello", "Bonjour")
    cache.save()
    
    assert (tmp_path / "test_cache.json").exists()
    
    cache2 = TranslationCache(tmp_path, "test_cache")
    assert cache2.get("Hello") == "Bonjour"

def test_cache_load_missing(tmp_path: Path):
    cache = TranslationCache(tmp_path, "missing_cache")
    assert cache.get("Hello") is None
    
def test_cache_bad_file(tmp_path: Path):
    bad_file = tmp_path / "bad_cache.json"
    with open(bad_file, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")
        
    cache = TranslationCache(tmp_path, "bad_cache")
    # Should handle gracefully and start empty
    assert cache.get("Hello") is None
