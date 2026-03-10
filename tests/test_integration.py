import json
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from rpgmv_translator.cli import main
from rpgmv_translator.translators.mock import MockTranslator

@pytest.fixture
def dummy_e2e_env(tmp_path: Path):
    input_dir = tmp_path / "game_in"
    input_dir.mkdir()
    data_dir = input_dir / "www" / "data"
    data_dir.mkdir(parents=True)
    
    # Simple JSON
    system_data = {"gameTitle": "Test Title", "currencyUnit": "Gold"}
    with open(data_dir / "System.json", "w", encoding="utf-8") as f:
        json.dump(system_data, f)
        
    output_dir = tmp_path / "game_out"
    # Ensure cache folder is empty or uses a specific one
    cache_dir = tmp_path / ".cache"
    
    return input_dir, output_dir, cache_dir

def test_full_run_mock_provider(dummy_e2e_env):
    input_dir, output_dir, cache_dir = dummy_e2e_env
    
    # Run the equivalent of: rpgmv_translator --input <input_dir> --output <output_dir> --provider mock
    argv = ["rpgmv_translator", "--input", str(input_dir), "--output", str(output_dir), "--provider", "mock"]
    
    with patch.object(sys, "argv", argv):
        # Also patch cache dir to fall within tmp_path to prevent dirtying real repo
        with patch("rpgmv_translator.cli.TranslationCache") as mock_cache_cls:
            # We want the real cache logic, just bound to our tmp dir
            from rpgmv_translator.cache import TranslationCache
            real_cache = TranslationCache(cache_dir, "test_cache")
            mock_cache_cls.return_value = real_cache
            
            main()
            
    # Verification
    assert (output_dir / "www/data/System.json").exists()
    
    with open(output_dir / "www/data/System.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["gameTitle"] == "Test Title [MOCK EN]"
    assert data["currencyUnit"] == "Gold [MOCK EN]"

def test_cache_hit_verification(dummy_e2e_env):
    input_dir, output_dir, cache_dir = dummy_e2e_env
    
    argv = ["rpgmv_translator", "--input", str(input_dir), "--output", str(output_dir), "--provider", "mock"]
    
    from rpgmv_translator.cache import TranslationCache
    
    with patch("rpgmv_translator.cli.TranslationCache") as mock_cache_cls:
        # Run 1
        real_cache_1 = TranslationCache(cache_dir, "test_cache")
        mock_cache_cls.return_value = real_cache_1
        with patch.object(sys, "argv", argv):
            main()
            
    with patch("rpgmv_translator.cli.TranslationCache") as mock_cache_cls:
        # Run 2
        real_cache_2 = TranslationCache(cache_dir, "test_cache")
        mock_cache_cls.return_value = real_cache_2
        
        # Spy on the translate_batch method of the mock provider. 
        # In a real cache hit scenario, it should not be called.
        with patch.object(sys, "argv", argv), \
             patch("rpgmv_translator.translators.mock.MockTranslator.translate_batch") as mock_translate:
             
            main()
            # Since everything was translated in Run 1 and cached, translate_batch should not be invoked in Run 2.
            mock_translate.assert_not_called()

def test_inplace_translation(dummy_e2e_env):
    input_dir, _, cache_dir = dummy_e2e_env
    
    argv = ["rpgmv_translator", "--input", str(input_dir), "--inplace", "--provider", "mock"]
    
    with patch.object(sys, "argv", argv):
        with patch("rpgmv_translator.cli.TranslationCache") as mock_cache_cls:
            from rpgmv_translator.cache import TranslationCache
            real_cache = TranslationCache(cache_dir, "test_cache")
            mock_cache_cls.return_value = real_cache
            
            main()
            
    with open(input_dir / "www/data/System.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["gameTitle"] == "Test Title [MOCK EN]"

def test_failure_recovery(dummy_e2e_env):
    input_dir, output_dir, cache_dir = dummy_e2e_env
    
    argv = ["rpgmv_translator", "--input", str(input_dir), "--output", str(output_dir), "--provider", "mock"]
    
    # We will simulate a failure in the translation to see if it gracefully falls back
    # By mocking get_translator to return our saboteur translator
    class FailingTranslator(MockTranslator):
        def translate_batch(self, texts):
            raise Exception("Simulated API Error")
            
    with patch.object(sys, "argv", argv):
         with patch("rpgmv_translator.cli.get_translator", return_value=FailingTranslator(config=MagicMock())):
             # We should avoid polluting the cache with fake failures, so we use a dummy dir again
             with patch("rpgmv_translator.cli.TranslationCache") as mock_cache_cls:
                 from rpgmv_translator.cache import TranslationCache
                 real_cache = TranslationCache(cache_dir, "test_cache")
                 mock_cache_cls.return_value = real_cache
                 
                 main()
                 
    # Because of our failures, the translator should fall back to the original text.
    with open(output_dir / "www/data/System.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["gameTitle"] == "Test Title"  # Not mock-translated due to repeated failure
