import pytest
from rpgmv_translator.config import TranslationConfig
from rpgmv_translator.translators.factory import get_translator
from rpgmv_translator.translators.ollama import OllamaTranslator
from rpgmv_translator.translators.openai import OpenAITranslator
from rpgmv_translator.translators.mock import MockTranslator

def test_get_translator_ollama():
    config = TranslationConfig(provider="ollama")
    translator = get_translator(config)
    assert isinstance(translator, OllamaTranslator)

def test_get_translator_openai():
    config = TranslationConfig(provider="openai")
    translator = get_translator(config)
    assert isinstance(translator, OpenAITranslator)

def test_get_translator_mock():
    config = TranslationConfig(provider="mock")
    translator = get_translator(config)
    assert isinstance(translator, MockTranslator)

def test_get_translator_unknown():
    config = TranslationConfig(provider="unknown_provider")
    translator = get_translator(config)
    assert isinstance(translator, OllamaTranslator)
