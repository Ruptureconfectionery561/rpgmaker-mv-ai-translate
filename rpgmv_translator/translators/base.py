"""
Translation modules
"""
from typing import List
from abc import ABC, abstractmethod
from ..config import TranslationConfig

class BaseTranslator(ABC):
    """
    Abstract base class for all translation backends.
    """
    
    def __init__(self, config: TranslationConfig):
        self.config = config

    @abstractmethod
    def translate_batch(self, texts: List[str]) -> List[str]:
        """
        Translates a batch of strings. 
        Must return a list of strings of the exact same length as the input list.
        """
        pass
