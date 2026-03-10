import pytest
from rpgmv_translator.config import TranslationConfig
from rpgmv_translator.batch_manager import BatchManager
from rpgmv_translator.models import TextEntry

def create_entries(count: int, text_length: int = 10) -> list[TextEntry]:
    return [TextEntry(file_path="dummy.json", json_path=[], original_text="A" * text_length) for _ in range(count)]

def test_generate_batches_respects_size():
    config = TranslationConfig(batch_size=3)
    manager = BatchManager(config)
    
    entries = create_entries(8)
    batches = list(manager.generate_batches(entries))
    
    assert len(batches) == 3
    assert len(batches[0]) == 3
    assert len(batches[1]) == 3
    assert len(batches[2]) == 2

def test_generate_batches_respects_context_limit():
    config = TranslationConfig()
    manager = BatchManager(config)
    
    # Force a very small token budget
    manager.usable_budget = 100
    # Each entry will use length * 0.4 tokens
    # e.g., 200 length -> 80 tokens
    entries = create_entries(3, text_length=200)
    
    # 3 entries, each 80 tokens. Budget is 100.
    # So each batch can only hold 1 entry.
    batches = list(manager.generate_batches(entries))
    
    assert len(batches) == 3
    assert len(batches[0]) == 1
    assert len(batches[1]) == 1
    assert len(batches[2]) == 1

def test_generate_batches_singleton_exceeds_budget():
    config = TranslationConfig()
    manager = BatchManager(config)
    
    manager.usable_budget = 50
    # Entry is 200 length -> 80 tokens, exceeds budget of 50
    entries = create_entries(1, text_length=200)
    
    batches = list(manager.generate_batches(entries))
    assert len(batches) == 1
    assert len(batches[0]) == 1

def test_split_batch():
    entries = create_entries(4)
    splits = BatchManager.split_batch(entries)
    
    assert len(splits) == 2
    assert len(splits[0]) == 2
    assert len(splits[1]) == 2
    
def test_split_batch_single():
    entries = create_entries(1)
    splits = BatchManager.split_batch(entries)
    
    assert len(splits) == 1
    assert len(splits[0]) == 1
