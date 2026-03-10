from typing import List, Iterator
import logging
from .models import TextEntry
from .config import TranslationConfig

logger = logging.getLogger(__name__)

CHARS_PER_TOKEN_RATIO = 0.4

class BatchManager:
    """
    Groups TextEntry items into variable-sized batches based on token estimates
    and the target model's context window.
    """
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        self.max_batch_size = config.batch_size
        self.context_limits = config.model_context_limits
        
        # Determine the maximum token budget for the input
        model_name = config.model.lower()
        limit = self.context_limits.get(model_name, self.context_limits.get("default", 4096))
        self.usable_budget = int(limit * config.context_usage_ratio)
        logger.debug(f"BatchManager initialized: budget={self.usable_budget} tokens (model={model_name})")

    def _estimate_tokens(self, text: str) -> int:
        return int(len(text) * CHARS_PER_TOKEN_RATIO)

    def generate_batches(self, entries: List[TextEntry]) -> Iterator[List[TextEntry]]:
        """
        Yields batches of TextEntry objects. Ensures that neither the context limit 
        nor the max batch size is exceeded, unless a single entry spans the context limit.
        """
        current_batch = []
        current_budget = 0
        
        for entry in entries:
            tokens = self._estimate_tokens(entry.original_text)
            
            # If a single entry exceeds the budget, it must be sent alone
            if not current_batch and tokens >= self.usable_budget:
                logger.warning(f"Single entry exceeds usable budget ({tokens}/{self.usable_budget} tokens). Yielding singleton batch.")
                yield [entry]
                continue
                
            # If adding this entry exceeds budget OR hits batch size limit, yield current batch
            if current_batch and (current_budget + tokens > self.usable_budget or len(current_batch) >= self.max_batch_size):
                yield current_batch
                current_batch = [entry]
                current_budget = tokens
            else:
                current_batch.append(entry)
                current_budget += tokens
                
        if current_batch:
            yield current_batch

    @staticmethod
    def split_batch(batch: List[TextEntry]) -> List[List[TextEntry]]:
        """Splits a batch in half. Used for retry fallback."""
        if len(batch) <= 1:
            return [batch]
            
        mid = len(batch) // 2
        return [batch[:mid], batch[mid:]]
