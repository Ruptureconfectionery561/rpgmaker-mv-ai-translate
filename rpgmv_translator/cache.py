import json
import hashlib
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TranslationCache:
    """
    A persistent JSON cache for translated text.
    Key: SHA256 mapping of the original text.
    Value: Translated string.
    """
    
    def __init__(self, cache_dir: Path, cache_name: str = "translations"):
        self.cache_dir = cache_dir
        self.cache_file = self.cache_dir / f"{cache_name}.json"
        self._cache = {}
        self._load()

    def _load(self) -> None:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.debug(f"Loaded {len(self._cache)} translation entries from cache.")
            except Exception as e:
                logger.error(f"Failed to load cache from {self.cache_file}: {e}")
                self._cache = {}
        else:
            self._cache = {}

    def save(self) -> None:
        """Persists the cache to disk."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
            logger.debug("Cache saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save cache to {self.cache_file}: {e}")

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def get(self, original_text: str) -> Optional[str]:
        """Returns the cached translation for the original text if it exists."""
        key = self._hash(original_text)
        return self._cache.get(key)

    def set(self, original_text: str, translated_text: str) -> None:
        """Sets the translated text in the cache."""
        key = self._hash(original_text)
        self._cache[key] = translated_text
