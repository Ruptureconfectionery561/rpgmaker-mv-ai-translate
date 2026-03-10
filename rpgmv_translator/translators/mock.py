from typing import List
import logging
from .base import BaseTranslator

logger = logging.getLogger(__name__)

class MockTranslator(BaseTranslator):
    """
    A mock translator that appends '[MOCK EN]' to all strings to simulate
    translation without requiring an actual LLM server.
    """
    
    def translate_batch(self, texts: List[str]) -> List[str]:
        logger.debug(f"MockTranslator: translating batch of {len(texts)} items")
        return [f"{t} [MOCK EN]" for t in texts]
