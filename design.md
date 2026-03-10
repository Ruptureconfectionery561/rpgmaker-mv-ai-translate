# RPG Maker MV AI Translator – Architecture & Design

This document outlines the architecture, pipeline, and primary design decisions behind the RPG Maker MV AI Translator.

## 1. High-Level Architecture

The CLI tool is designed as a multi-module Python application that processes JSON data files from an RPG Maker MV project. The system functions as a pipeline with the following distinct stages:

1. **Configuration (`config.py`)**: Loads user preferences (language, models, endpoints) from `gpt-config.json` and CLI arguments.
2. **Extraction (`extractor.py`)**: Parses the internal `www/data/` or `data/` structure of the MV game, specifically targeting text-heavy definitions like `MapXXX.json`, `CommonEvents.json`, `Actors.json`, etc.
3. **Control Code Protection**: Abstracts away RPG Maker's rendering control codes (e.g. `\N[1]`, `\C[4]`) into safe text placeholders before it reaches the language model.
4. **Translation Layer (`translators/`)**: Connects to external LLM providers (e.g., Ollama, LM Studio, OpenAI) asynchronously.
5. **Dynamic Batching (`batch_manager.py`)**: Gathers multiple extracted strings into appropriately sized prompts based on context windows, maximizing throughput.
6. **Caching (`cache.py`)**: Caches translations using SHA-256 hashes to prevent redundant API calls on subsequent runs.
7. **Reinjection (`reinjector.py`)**: Takes the translated results, restores the protected control codes, and precisely edits the original UI/dialogue nodes without breaking the structural integrity of the JSON files.

---

## 2. Core Components

### The Extractor
Traverses the game directory looking for translatable assets. For dialogue, it targets Event Command Codes `101` and `401` (dialogue sequences) and `102` (choices). It aggressively merges consecutive `401` text blocks together to present the LLM with full conversational context rather than fragmented, single-line strings. It returns an internal `TextEntry` object containing the file path, the nested JSON path, and the original text.

### The Translator Abstraction
Built around a `BaseTranslator` class, the tool allows multiple translation engines to be swapped in. The default implementation is `OllamaTranslator` (which also serves any OpenAI-compatible endpoint like LM Studio). 

### Context-Aware Dynamic Batching
A crucial design decision was to avoid strictly fixed batch sizes. Depending on the LLM's context window, rigid batch sizes can lead to overflows or wasted context. The `batch_manager` analyzes text lengths and intelligently buckets strings up to an estimated context ceiling. If a batch fails to translate properly or the LLM skips a line, the batch manager recursively splits the batch in half and retries gracefully.

### The Cache
A local `.cache/translations.json` file hashes the original strings. This allows the tool to gracefully resume stopped translations, dramatically reducing time and API costs during iterative testing and translation development.

---

## 3. Key Design Decisions

1. **Non-Destructive Reinjection**: Instead of rebuilding the JSON files from scratch (which risks stripping custom plugin properties or unrecognized data), the reinjector uses the stored JSON navigation path to target exactly the text fields that need replacing. All other original data remains perfectly untouched.
2. **Abstract Pluggability**: We do not hardcode the API calls to one single vendor. Using the factory pattern in `translators/factory.py`, adding future support for new APIs (like Anthropic or Gemini) requires only writing a new class that conforms to `BaseTranslator`.
3. **Regex Control Code Masking**: LLMs notoriously hallucinate or discard unusual syntax like `\c[2]`. By swapping these with simple dummy tokens (like `__CTRL0__`) and forcing the LLM to preserve the token in the prompt template, we guarantee that the visual formatting and game variables operate perfectly in the final translated game.
4. **Resiliency over Speed**: Built-in retry logic and the batch-halving algorithm heavily optimize for completion over blind speed. If a model starts acting up, the tool adapts rather than crashing.
