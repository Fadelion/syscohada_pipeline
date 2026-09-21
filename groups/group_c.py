import logging
from typing import Any, Dict, Iterable, List
from syscohada_pipeline.extractors.gemini_vlm_engine import extract_bilan, extract_cr
from syscohada_pipeline.extractors.heuristic_engine import extract_tft
from syscohada_pipeline.extractors.paddle_vl_engine import extract_bilan as extract_paddle_bilan
from syscohada_pipeline.extractors.paddle_vl_engine import extract_cr as extract_paddle_cr
from syscohada_pipeline.extractors.paddle_vl_engine import init_paddle_engine

logger = logging.getLogger(__name__)

def process_document_group_c(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Consensus sur les moteurs réellement disponibles."""
    results = {"bilan": {}, "cr": {}, "tft": {}, "notes": [], "esdgi": []}
    paddle_engine = init_paddle_engine()
    for page in pages_data:
        try:
            _process_page_group_c(page, results, paddle_engine)
        except Exception as e:
            logger.error(f"Échec consensus sur page {page.get('id')}: {e}")
    return results

def _process_page_group_c(page: Dict[str, Any], results: Dict[str, Any], paddle_engine: Any) -> None:
    page_type = page.get("type", "unknown")
    img_path = page.get("image_path", "")
    if page_type == "tft":
        results["tft"].update(_single_source(extract_tft(img_path)))
    elif page_type == "bilan":
        gemini_res = extract_bilan(img_path) or {}
        paddle_res = extract_paddle_bilan(img_path, paddle_engine) or {}
        results["bilan"].update(_apply_bilan_consensus(gemini_res, paddle_res))
    elif page_type == "cr":
        gemini_res = extract_cr(img_path) or {}
        paddle_res = extract_paddle_cr(img_path, paddle_engine) or {}
        results["cr"].update(_apply_consensus(gemini_res, paddle_res))

def _apply_bilan_consensus(first: Dict, second: Dict) -> Dict[str, Any]:
    result = {}
    for section in {"actif", "passif"}:
        result[section] = _apply_consensus(first.get(section, {}), second.get(section, {}))
    return result

def _apply_consensus(first: Dict, second: Dict) -> Dict[str, Any]:
    consensus = {}
    for key in set(first) | set(second):
        values = [first.get(key, {}).get("net"), second.get(key, {}).get("net")]
        result = vote_majority(values)
        if result["value"] is not None:
            consensus[key] = {"net": result["value"], "confidence": result["confidence"]}
    return consensus

def _single_source(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: {**value, "confidence": "source unique"} for key, value in data.items()}

def vote_majority(values: Iterable[Any]) -> Dict[str, Any]:
    vals = [value for value in values if value is not None]
    if not vals:
        return {"value": None, "confidence": "aucune donnée"}
    from collections import Counter
    counts = Counter(vals)
    most_common, count = counts.most_common(1)[0]
    confidence = "unanime" if count == len(vals) else "majorité" if count > 1 else "conflit"
    return {"value": most_common, "confidence": confidence}
