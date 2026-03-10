from .base import BaseTranslator
from .mock import MockTranslator
from .ollama import OllamaTranslator
from .openai import OpenAITranslator
from ..config import TranslationConfig
import logging

logger = logging.getLogger(__name__)

def get_translator(config: TranslationConfig) -> BaseTranslator:
    """
    Factory function to instantiate the requested translation backend.
    """
    provider = config.provider.lower().strip()
    
    if provider == "mock":
        logger.info("Using MockTranslator back-end.")
        return MockTranslator(config)
    elif provider == "ollama":
        logger.info(f"Using OllamaTranslator back-end (model: {config.model}).")
        return OllamaTranslator(config)
    elif provider in ["openai", "lmstudio"]:
        logger.info(f"Using OpenAITranslator back-end (model: {config.model}).")
        return OpenAITranslator(config)
    else:
        logger.warning(f"Unknown provider '{provider}', falling back to OllamaTranslator")
        return OllamaTranslator(config)
