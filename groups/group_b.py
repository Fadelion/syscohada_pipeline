import logging
from typing import Dict, Any, List
from syscohada_pipeline.extractors.gemini_vlm_engine import extract_bilan, extract_cr, extract_notes, extract_esdgi
from syscohada_pipeline.extractors.heuristic_engine import extract_tft

logger = logging.getLogger(__name__)

def process_document_group_b(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Approche Hybride: Gemini (Bilan/CR/Notes/ESDGI), Heuristique (TFT)."""
    results = {"bilan": {}, "cr": {}, "tft": {}, "notes": [], "esdgi": []}
    for page in pages_data:
        try:
            _process_page_group_b(page, results)
        except Exception as e:
            logger.error(f"Erreur d'extraction sur la page {page.get('id')}: {e}")
    return results

def _deep_update(d: dict, u: dict) -> dict:
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        elif v is not None and v != {}:
            d[k] = v
    return d

def _process_page_group_b(page: Dict[str, Any], results: Dict[str, Any]) -> None:
    ptype, path = page.get("type", "unknown"), page.get("image_path", "")
    if ptype == "bilan":
        data = extract_bilan(path)
        if data: 
            from syscohada_pipeline.core.accounting_rules import compute_net
            for code, vals in data.get("actif", {}).items():
                if isinstance(vals, dict) and vals.get("net") is None:
                    if vals.get("brut") is not None and vals.get("amort") is not None:
                        vals["net"] = compute_net(vals["brut"], vals["amort"])
            _deep_update(results["bilan"], data)
    elif ptype == "cr":
        data = extract_cr(path)
        if data: _deep_update(results["cr"], data)
    elif ptype == "tft":
        data = extract_tft(path)
        if data: _deep_update(results["tft"], data)
    elif ptype == "notes":
        data = extract_notes(path)
        if data: results["notes"].append({"page_id": page.get("id"), "content": data})
    elif ptype == "esdgi":
        data = extract_esdgi(path)
        if data: results["esdgi"].append({"page_id": page.get("id"), "content": data})
