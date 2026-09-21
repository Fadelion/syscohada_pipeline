import logging
from typing import Dict, Any, List
from syscohada_pipeline.extractors.heuristic_engine import extract_tft
from syscohada_pipeline.extractors.paddle_vl_engine import extract_bilan, extract_cr, init_paddle_engine
from syscohada_pipeline.core.config import get_base_config

logger = logging.getLogger(__name__)

def process_document_group_a(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = {"bilan": {}, "cr": {}, "tft": {}, "notes": [], "esdgi": []}
    engine = init_paddle_engine(get_base_config()["device"])
    
    for page in pages_data:
        try:
            _process_page_group_a(page, results, engine)
        except Exception as e:
            logger.error(f"Erreur d'extraction sur la page {page.get('id')}: {e}")
            
    return results

def _process_page_group_a(page: Dict[str, Any], results: Dict[str, Any], engine: Any) -> None:
    ptype, path = page.get("type", "unknown"), page.get("image_path", "")
    if ptype == "tft":
        tft_data = extract_tft(path)
        if tft_data: results["tft"].update(tft_data)
    elif ptype == "bilan":
        b_data = extract_bilan(path, engine)
        if b_data: _deep_update(results["bilan"], b_data)
    elif ptype == "cr":
        c_data = extract_cr(path, engine)
        if c_data: results["cr"].update(c_data)

def _deep_update(d: dict, u: dict) -> dict:
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        elif v is not None and v != {}:
            d[k] = v
    return d
