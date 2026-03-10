# 🌍 RPG Maker MV AI Translator

[![Python CI/CD](https://github.com/kemsig/rpgmaker-mv-ai-translate/actions/workflows/python-app.yml/badge.svg)](https://github.com/kemsig/rpgmaker-mv-ai-translate/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A robust, beautifully engineered command-line tool built in Python to automatically translate RPG Maker MV games using LLMs. Out of the box, it seamlessly interfaces with any localized OpenAI-compatible endpoint (such as **LM Studio**, **Ollama**, or explicitly OpenAI/Anthropic/etc). 

RPGMaker MV AI Translator is a Python CLI tool that automatically
translates RPG Maker MV games using large language models (LLMs).
It extracts dialogue from RPGMaker JSON files, batches it for
efficient translation, and reinserts the translated text back into the game.

This tool is designed to save you from hours of manual string-hunting. It natively understands RPG Maker MV's complex object structures and handles extraction and injection fluidly.

---

## ✨ Features

- **Painless Extraction**: Automatically extracts dialogue (`MapXXX.json`), choices, descriptions, character names, and database definitions from RPG Maker MV `.json` data files.
- **Control Code Protection**: Accurately preserves RPG Maker game text variables and visual formatting (e.g., `\C[4]`, `\N[1]`, `\!`) perfectly. It abstracts them during translation and natively restores them upon reinjection, effectively preventing LLM hallucination on internal game codes.
- **Dynamic Batch Processing**: Intelligently buckets and batches strings to maximize translation speed while dynamically respecting your target LLM's context window. (You don't need to manually configure token limits).
- **Resilient Translation Cache**: Built-in hashing and caching means repeated translation requests don't waste API calls. If the LLM throws an error or skips a line, the built-in validator cleanly halves the batch and gracefully retries.
- **Non-Destructive Reinjection**: Constructs a fully playable translated copy of your game. The translated text is merged precisely into the game's data files without damaging structural integrity or external plugin logic.

---

## 🚀 Quick Start Pipeline: My Flow with LM Studio & Qwen

If you want to get up and running entirely locally (and for free) using a highly capable model like Qwen, here is the exact step-by-step workflow I use:

### 1. Set Up LM Studio
1. Download [LM Studio](https://lmstudio.ai/).
2. Search for a recent **Qwen** model (e.g., Qwen 2.5 7B, 14B, or higher depending on your VRAM). Download the appropriate GGUF file.
3. Once downloaded, navigate to the **Local Server** tab (the `<->` icon) in LM Studio.
4. Load the Qwen model at the top.
5. Turn on **CORS** (typically in the right panel) and click **Start Server**. It should now be listening at `http://localhost:1234/v1`.

### 2. Configure the Translator
1. Clone this repository and install dependencies:
   ```bash
   pip install -e .
   ```
2. Generate the default configuration file:
   ```bash
   python -m rpgmv_translator.cli --generate-config
   ```
3. Open `gpt-config.json` and tweak it to point to LM Studio:
   ```json
   "endpoint": "http://localhost:1234/v1",
   "provider": "openai", 
   "model": "qwen2.5-7b" 
   ```
   *(Note: Make sure `provider` is set to something LM Studio can parse, such as `openai` if it mimics the OpenAI format API, or `ollama` if it's set up that way).*

### 3. Translate!
Run the tool against your target RPG Maker MV game:
```bash
python -m rpgmv_translator.cli --input ./path/to/game --output ./path/to/game_translated --config ./gpt-config.json
```
Go grab a coffee while Qwen and the batch manager rip through the game's JSON files!

---

## 🛠 Prerequisites & Installation

- **Python 3.11+**

```bash
git clone https://github.com/kemsig/rpgmaker-mv-ai-translate.git
cd rpgmaker-mv-ai-translate
pip install -e .
```

*(Note: We recommend setting up a virtual environment via `python -m venv venv` and activating it before installing).*

---

## ⚙️ Configuration File Anatomy

The tool behaves exactly how you configure it via `gpt-config.json` (generated via `--generate-config`).

Key fields you can extensively customize:
- `endpoint`: The base URL to your translation endpoint (e.g., `http://localhost:11434` for Ollama, `http://localhost:1234/v1` for LM Studio/OpenAI interfaces).
- `model`: The specific LLM model identifier.
- `batch_size`: The upper limit of lines to bundle into each LLM context prompt. Feel free to raise this (e.g. `50`) to accelerate translation if your model has a large context window.
- `source_language` / `target_language`: Fully adjustable. Change these to `Chinese` -> `Spanish`, `Japanese` -> `English`, etc.
- `system_prompt` / `user_prompt_template`: You have full control over the exact persona and formatting rules the LLM follows.

*(Pro-tip: All configuration options can be overridden dynamically at translation runtime via CLI flags like `--model` or `--batch-size`!)*

---

## 💻 Full Usage & CLI Options

To run the translation safely, generating a full copy:
```bash
python -m rpgmv_translator.cli --input ./path/to/original_game --output ./path/to/translated_game --config ./gpt-config.json
```

### CLI Flag Reference:
- `--input <path>`: Required. Path to the original game directory containing `www/data/` or `data/`.
- `--output <path>`: Required (unless `--inplace`). Path where the translated clone should be saved.
- `--config <path>`: Optional. Path to configuration JSON.
- `--inplace`: Overwrite the input directory files instead of creating a copy. **(Warning: Keep backups if you use this!)**.
- `--dry-run`: Merely extract and analyze strings. Shows exactly what will be translated and tests the extraction pipeline without pinging your LLM.
- `--model <name>`, `--provider <name>`, `--batch-size <num>`, `--temperature <num>`: Easily override `gpt-config.json` values on the fly.

---

## 💡 Best Practices and Easy Use Guides

- **Start with a `--dry-run`**: Always run a dry run first to see how many lines and API calls you can expect. This will map out the translation scale immediately.
- **Iterative Testing with `--inplace`**: If you're localizing a tiny game and frequently tweaking the `--input` translation, `--inplace` is much faster. 
- **Resuming After Stops**: Because of `.cache/translations.json`, if your API crashes or your computer turns off halfway through translation, just restart the exact same basic translation command. The tool will instantly skip everything it's already translated and pick up right where it left off.
- **Handling Untranslated Plugins**: If your game uses custom `.js` plugins that have hardcoded strings in `www/js/plugins/`, the tool currently won't translate them automatically. You'll need to manually open those JS files to localize bespoke UI widgets.

---

## 🧪 Testing and CI/CD Pipeline

This tool is bundled with Pytest coverage mapping and a GitHub Actions workflow.

To execute tests directly:
```bash
# We set PYTHONPATH so pytest discovers the module correctly
PYTHONPATH=. pytest --cov=rpgmv_translator tests/
```

We highly encourage contributions! The repository is configured with a built-in CI/CD Action that automatically validates Pytest flows against Python `3.11` and `3.12` on every Pull Request or Commit to `main`. 

---

## 📝 Architecture & Design
If you want to dive deeper into how we dynamically batch entries, manage LLM token limits natively, and inject JSON paths without destroying plugins, check out [design.md](./design.md).
