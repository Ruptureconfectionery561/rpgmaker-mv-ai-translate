import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict

from tqdm import tqdm

from .config import TranslationConfig
from .extractor import Extractor
from .reinjector import Reinjector
from .cache import TranslationCache
from .batch_manager import BatchManager
from .translators.factory import get_translator
from .utils.control_codes import ControlCodeManager
from .models import TextEntry

def setup_logging(level: int):
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=level,
        stream=sys.stdout
    )

def main():
    parser = argparse.ArgumentParser(description="RPG Maker MV AI Translator")
    parser.add_argument("--input", type=str, help="Path to RPG Maker MV game directory")
    parser.add_argument("--output", type=str, help="Output directory for translated copy")
    parser.add_argument("--inplace", action="store_true", help="Translate in-place (mutates source)")
    parser.add_argument("--config", type=str, help="Path to gpt-config.json")
    parser.add_argument("--generate-config", action="store_true", help="Write default config to ./gpt-config.json and exit")
    
    # Overrides
    parser.add_argument("--provider", type=str, help="Override LLM provider")
    parser.add_argument("--model", type=str, help="Override Model name")
    parser.add_argument("--batch-size", type=int, help="Override batch size")
    parser.add_argument("--dry-run", action="store_true", help="Extract and report without translating")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    setup_logging(logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger(__name__)

    if args.generate_config:
        config_path = Path("gpt-config.json")
        TranslationConfig().save_defaults(config_path)
        sys.exit(0)

    if not args.input:
        parser.error("--input is required unless --generate-config is used")

    input_dir = Path(args.input)
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not args.inplace and not args.output:
        parser.error("--output is required unless --inplace is used")

    output_dir = input_dir if args.inplace else Path(args.output)
    
    config_path = Path(args.config) if args.config else None
    config = TranslationConfig.load(config_path)

    # Apply overrides
    if args.provider: config.provider = args.provider
    if args.model: config.model = args.model
    if args.batch_size: config.batch_size = args.batch_size

    logger.info(f"Starting extraction for {input_dir}...")
    extractor = Extractor(input_dir)
    entries = extractor.extract_all()
    
    if args.dry_run:
        logger.info(f"Dry run complete. Found {len(entries)} translatable entries.")
        sys.exit(0)

    provider_safe = config.provider.replace('/', '_').replace('\\', '_')
    model_safe = config.model.replace('/', '_').replace('\\', '_')
    cache_name = f"translations_{provider_safe}_{model_safe}"
    
    cache = TranslationCache(Path(".cache"), cache_name=cache_name)
    translator = get_translator(config)
    batch_manager = BatchManager(config)

    # Pre-process: control codes and cache check
    pending_entries: List[TextEntry] = []
    # Using object IDs to map back to original positions to ensure output order matches input order
    final_translations: Dict[int, str] = {}
    control_code_maps: Dict[int, dict] = {}
    masked_texts: Dict[int, str] = {}
    
    cache_hits = 0

    for entry in entries:
        eid = id(entry)
        masked_text, cc_map = ControlCodeManager.extract_and_replace(entry.original_text)
        masked_texts[eid] = masked_text
        control_code_maps[eid] = cc_map
        
        cached_trans = cache.get(masked_text)
        if cached_trans is not None:
            cache_hits += 1
            final_translations[eid] = cached_trans
        else:
            pending_entries.append(entry)

    logger.info(f"Using cache: {cache_hits} hits. {len(pending_entries)} entries to translate.")

    # Process pending in batches
    failures = 0
    batches = list(batch_manager.generate_batches(pending_entries))
    queue = batches.copy()
    
    lines_translated = 0

    pbar = tqdm(total=len(pending_entries), desc="Translating", unit="line")
    
    while queue:
        current_batch = queue.pop(0)
        if not current_batch:
            continue
            
        texts_to_translate = [masked_texts[id(e)] for e in current_batch]
        success = False
        
        logger.debug(f"Translating batch of {len(current_batch)} items...")
        
        for attempt in range(config.max_retries):
            try:
                translated_texts = translator.translate_batch(texts_to_translate)
                # Success
                for e, trans in zip(current_batch, translated_texts):
                    final_translations[id(e)] = trans
                    cache.set(masked_texts[id(e)], trans)
                    lines_translated += 1
                success = True
                pbar.update(len(current_batch))
                break
            except Exception as ex:
                logger.warning(f"Batch failed (Attempt {attempt+1}/{config.max_retries}): {ex}")
                
        if not success:
            if len(current_batch) > 1:
                tqdm.write("Splitting batch due to repeated failures.")
                logger.warning("Splitting batch due to repeated failures.")
                queue = batch_manager.split_batch(current_batch) + queue
            else:
                tqdm.write(f"Failed to translate entry after splits/retries: {texts_to_translate[0]}")
                logger.error(f"Failed to translate entry after splits/retries: {texts_to_translate[0]}")
                # Fallback to original text
                e = current_batch[0]
                final_translations[id(e)] = e.original_text
                failures += 1
                pbar.update(len(current_batch))

    pbar.close()

    # Save cache
    cache.save()

    # Reconstruct final ordered list, restoring control codes
    ordered_translations = []
    for entry in entries:
        eid = id(entry)
        trans_masked = final_translations.get(eid, entry.original_text)
        cc_map = control_code_maps.get(eid, {})
        restored_text = ControlCodeManager.restore(trans_masked, cc_map)
        ordered_translations.append(restored_text)

    # Reinjection
    reinjector = Reinjector(input_dir, output_dir)
    if not args.inplace:
        reinjector.copy_unmodified_assets()
        
    logger.info("Injecting translated text back into JSON files...")
    reinjector.inject_all(entries, ordered_translations)

    # Summary
    logger.info("=== SUMMARY ===")
    logger.info(f"Files processed: {len(set(e.file_path for e in entries))}")
    logger.info(f"Extracted lines: {len(entries)}")
    logger.info(f"Cache hits:      {cache_hits}")
    logger.info(f"Lines translated:{lines_translated}")
    logger.info(f"Failures:        {failures}")
    logger.info(f"Config:          provider={config.provider}, model={config.model}")
    logger.info("Translation complete!")

if __name__ == "__main__":
    main()
