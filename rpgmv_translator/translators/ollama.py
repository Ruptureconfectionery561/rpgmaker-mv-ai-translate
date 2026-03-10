import re
import logging
import requests
from typing import List
from .base import BaseTranslator
from ..config import TranslationConfig

logger = logging.getLogger(__name__)

class TranslationError(Exception):
    """Raised when translation output fails validation or API call fails."""
    pass

class OllamaTranslator(BaseTranslator):
    """
    Communicates with a local Ollama server to translate blocks of text.
    Expects input and outputs to be formatted in numbered blocks.
    """
    
    def __init__(self, config: TranslationConfig):
        super().__init__(config)
        self.api_url = f"{self.config.endpoint.rstrip('/')}/api/generate"
        
        # Pre-build the system prompt
        self.system_prompt = self.config.system_prompt.format(
            source_language=self.config.source_language,
            target_language=self.config.target_language
        )
        if self.config.context_hint:
            self.system_prompt += f"\n\nContext: {self.config.context_hint}"

    def _build_text_block(self, texts: List[str]) -> str:
        """Formats the texts into numbered blocks."""
        blocks = []
        for i, text in enumerate(texts):
            blocks.append(f"[{i}]\n{text}")
        return "\n\n".join(blocks)

    def _parse_response(self, response_text: str, expected_count: int) -> List[str]:
        """
        Extracts translated blocks based on the [N] format.
        """
        # Finds [N] followed by the content until the next [N] or end of string.
        pattern = re.compile(r'\[\d+\]\s*(.*?)(?=(?:\[\d+\])|\Z)', re.DOTALL)
        matches = pattern.findall(response_text)
        
        translations = [m.strip() for m in matches]
        
        if len(translations) != expected_count:
            # Fallback if the parser missed. Sometimes LLM omits the bracket numbers or outputs raw text for 1 item.
            if expected_count == 1 and len(response_text.strip()) > 0 and len(translations) == 0:
                return [response_text.strip()]
            
            # If not recoverable, clean up and raise error so the batch splitter can retry.
            logger.error(f"Ollama returned {len(translations)} blocks, expected {expected_count}.")
            logger.debug(f"Raw response: {response_text}")
            raise TranslationError(f"Output count mismatch: got {len(translations)}, expected {expected_count}")
            
        return translations

    def translate_batch(self, texts: List[str]) -> List[str]:
        if not texts:
            return []
            
        text_block = self._build_text_block(texts)
        
        user_prompt = self.config.user_prompt_template.format(
            source_language=self.config.source_language,
            target_language=self.config.target_language,
            text_block=text_block
        )
        
        payload = {
            "model": self.config.model,
            "system": self.system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature
            }
        }
        
        try:
            logger.debug(f"Sending request to {self.api_url} for batch of {len(texts)}")
            response = requests.post(self.api_url, json=payload, timeout=(10, 300))
            response.raise_for_status()
            response_json = response.json()
            response_text = response_json.get("response", "")
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama API request timed out (is the server running at {self.api_url}?): {e}")
            raise TranslationError(f"API Request timed out: {e}") from e
        except requests.RequestException as e:
            logger.error(f"Ollama API request failed (check endpoint URL): {e}")
            raise TranslationError(f"API Request failed: {e}") from e
            
        return self._parse_response(response_text, len(texts))
