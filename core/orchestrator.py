import logging
import os
import glob
import re
from typing import Any, Callable, Dict, List, Optional
from syscohada_pipeline.core.config import get_base_config
from syscohada_pipeline.core.pdf_processor import convert_pdf_to_images
from syscohada_pipeline.core.page_classifier import classify_page
from syscohada_pipeline.core.db_builder import build_syscohada_db, build_notes_db, build_esdgi_db
from syscohada_pipeline.core.checkpoint_manager import load_checkpoint, save_checkpoint

logger = logging.getLogger(__name__)

def _setup_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    except ImportError:
        logger.warning("python-dotenv absent.")

def _apply_accounting_rules(results: dict):
    from syscohada_pipeline.core.accounting_rules import validate_bilan, validate_tft
    actif = results.get("bilan", {}).get("actif", {})
    passif = results.get("bilan", {}).get("passif", {})
    results["bilan"]["is_valid"] = validate_bilan(actif, passif)
    results["tft"]["is_valid"] = validate_tft(results.get("tft", {}))

def run_pipeline(input_path: str, output_dir: str, process_func: Callable, group_name: str):
    _setup_env()
    config = get_base_config()
    os.makedirs(output_dir, exist_ok=True)
    pdfs = _find_pdfs(input_path)
    all_results = []
    for pdf in sorted(pdfs):
        logger.info(f"Traitement de {pdf}")
        try:
            run_config = {**config, "group_name": group_name}
            res = _process_single_pdf(pdf, output_dir, process_func, run_config)
        except Exception as exc:
            logger.exception("Échec du document %s: %s", pdf, exc)
            res = {}
        if res:
            all_results.append(res)
    _build_all_dbs(all_results, output_dir, group_name)

def _process_single_pdf(pdf_path: str, out_dir: str, process_func: Callable, cfg: dict) -> dict:
    doc_id = _document_id(pdf_path, cfg.get("group_name", "default"))
    cached = load_checkpoint(doc_id, cfg["checkpoint_dir"])
    if cached and cached.get("status") == "completed":
        return cached.get("results", {})
    page_dir = os.path.join(out_dir, "pages", doc_id)
    img_paths = convert_pdf_to_images(pdf_path, page_dir, max_pages=None)
    if not img_paths:
        save_checkpoint(doc_id, {"status": "failed", "source_file": pdf_path}, cfg["checkpoint_dir"])
        return {}
    from syscohada_pipeline.core.memory import free_memory
    try:
        return _run_document(img_paths, pdf_path, process_func, cfg)
    except Exception as exc:
        save_checkpoint(doc_id, {"status": "failed", "source_file": pdf_path, "error": str(exc)}, cfg["checkpoint_dir"])
        raise
    finally:
        free_memory()

def _run_document(img_paths: List[str], pdf_path: str, process_func: Callable, cfg: dict) -> dict:
    from syscohada_pipeline.extractors.heuristic_engine import init_heuristic_engine
    ocr = init_heuristic_engine(device=cfg["device"])
    pages = _prepare_pages_data(img_paths, ocr)
    results = process_func(pages)
    _apply_accounting_rules(results)
    results["source_file"] = os.path.basename(pdf_path)
    doc_id = _document_id(pdf_path, cfg.get("group_name", "default"))
    save_checkpoint(doc_id, {"status": "completed", "source_file": pdf_path, "results": results}, cfg["checkpoint_dir"])
    return results

def _find_pdfs(input_path: str) -> List[str]:
    if os.path.isdir(input_path):
        return glob.glob(os.path.join(input_path, "*.pdf"))
    return [input_path]

def _document_id(pdf_path: str, group_name: str) -> str:
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    return f"{group_name}_{safe_stem}"

def _prepare_pages_data(img_paths: List[str], ocr_engine: Any) -> List[Dict[str, Any]]:
    return [_prepare_page(path, ocr_engine) for path in img_paths]

def _prepare_page(path: str, ocr_engine: Any) -> Dict[str, Any]:
    raw = _run_ocr(path, ocr_engine)
    ocr_words = _extract_ocr_words(raw)
    page_type = classify_page(ocr_words)
    logger.info("Page classifiée: %s (%s)", page_type.upper(), os.path.basename(path))
    return {"id": path, "image_path": path, "type": page_type, "ocr_words": ocr_words}

def _run_ocr(path: str, engine: Any) -> Any:
    if engine is None:
        return None
    try:
        return engine.predict(path)
    except (AttributeError, TypeError):
        try:
            return engine.ocr(path)
        except TypeError:
            return engine.ocr(path, cls=True)

def _extract_ocr_words(raw: Any) -> List[Dict[str, str]]:
    first = raw[0] if isinstance(raw, list) and raw else raw
    if isinstance(first, dict) and "rec_texts" in first:
        return [{"text": str(text)} for text in first["rec_texts"]]
    if isinstance(first, list):
        return [{"text": str(line[1][0])} for line in first if len(line) > 1]
    return []

def _build_all_dbs(all_results: list, output_dir: str, group_name: str):
    if not all_results: return
    build_syscohada_db(all_results, os.path.join(output_dir, f"bd_syscohada_{group_name}.xlsx"))
    build_notes_db(all_results, os.path.join(output_dir, f"bd_notes_{group_name}.xlsx"))
    build_esdgi_db(all_results, os.path.join(output_dir, f"bd_esdgi_{group_name}.xlsx"))
