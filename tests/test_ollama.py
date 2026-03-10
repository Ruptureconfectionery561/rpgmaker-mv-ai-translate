import pytest
from rpgmv_translator.translators.ollama import OllamaTranslator, TranslationError
from rpgmv_translator.config import TranslationConfig

@pytest.fixture
def config():
    conf = TranslationConfig()
    conf.provider = "ollama"
    conf.model = "test-model"
    return conf

@pytest.fixture
def translator(config):
    return OllamaTranslator(config)

def test_build_text_block(translator):
    texts = ["Hello", "World", "This is a test."]
    block = translator._build_text_block(texts)
    
    expected = "[0]\nHello\n\n[1]\nWorld\n\n[2]\nThis is a test."
    assert block == expected

def test_parse_response_success(translator):
    response_text = """
Here are the translations:
[0]
Bonjour
[1]
Monde
[2]
Ceci est un test.
"""
    result = translator._parse_response(response_text, expected_count=3)
    assert result == ["Bonjour", "Monde", "Ceci est un test."]

def test_parse_response_mismatch(translator):
    response_text = """
[0]
Bonjour
[1]
Monde
"""
    # Expected 3, got 2 blocks
    with pytest.raises(TranslationError) as excinfo:
        translator._parse_response(response_text, expected_count=3)
    assert "got 2, expected 3" in str(excinfo.value)

def test_parse_response_fallback(translator):
    response_text = "Bonjour le monde"
    # When expecting 1, it should just return the whole string if it misses the brackets
    result = translator._parse_response(response_text, expected_count=1)
    assert result == ["Bonjour le monde"]
