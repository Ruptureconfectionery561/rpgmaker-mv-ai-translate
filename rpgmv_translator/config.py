import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class TranslationConfig:
    provider: str = "ollama"
    model: str = "llama3"
    endpoint: str = "http://localhost:11434"
    source_language: str = "Japanese"
    target_language: str = "English"
    batch_size: int = 10
    max_retries: int = 3
    temperature: float = 0.3
    system_prompt: str = (
        "You are a professional translator specializing in video game localization. "
        "Translate {source_language} text to natural, fluent {target_language}. "
        "Preserve all placeholders exactly as they appear. Maintain the tone and context of RPG dialogue."
    )
    user_prompt_template: str = (
        "Translate the following {source_language} text to {target_language}.\n"
        "Preserve placeholders like __CTRL0__ exactly.\n"
        "Return results in the same numbered format.\n\n"
        "{text_block}"
    )
    context_hint: str = "This is dialogue from a Japanese RPG. Keep translations natural for a gaming audience."
    
    model_context_limits: Dict[str, int] = field(default_factory=lambda: {
        "llama3": 8192, 
        "mistral": 32768, 
        "gemma2": 8192, 
        "default": 4096
    })
    context_usage_ratio: float = 0.7

    @classmethod
    def load(cls, path: Optional[Path]) -> "TranslationConfig":
        """Loads configuration from a JSON file, falling back to defaults for missing keys."""
        if path and path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Filter out unknown keys to prevent dataclass instantiation errors
                valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                
                return cls(**filtered_data)
            except Exception as e:
                logger.error(f"Failed to load config from {path}: {e}")
                logger.info("Using default configuration.")
        
        return cls()

    def save_defaults(self, path: Path) -> None:
        """Writes the current configuration to a JSON file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=4, ensure_ascii=False)
            logger.info(f"Generated default config at {path}")
        except Exception as e:
            logger.error(f"Failed to write config to {path}: {e}")

