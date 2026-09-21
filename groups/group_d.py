import logging
from typing import Dict, Any, List
from syscohada_pipeline.extractors.heuristic_engine import extract_tft
from syscohada_pipeline.extractors.paddle_vl_engine import extract_bilan, extract_cr, init_paddle_engine
from syscohada_pipeline.core.config import get_base_config

logger = logging.getLogger(__name__)

def process_document_group_d(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = {"bilan": {}, "cr": {}, "tft": {}, "notes": [], "esdgi": []}
    engine = init_paddle_engine(get_base_config()["device"])
    for page in pages_data:
        try:
            _process_page_group_d(page, results, engine)
        except Exception as e:
            logger.error(f"Échec consensus D page {page.get('id')}: {e}")
    return results

def _process_page_group_d(page: Dict[str, Any], results: Dict[str, Any], engine: Any) -> None:
    ptype, path = page.get("type", "unknown"), page.get("image_path", "")
    if ptype == "tft":
        heur_tft = extract_tft(path)
        results["tft"].update(_apply_2_way_consensus(heur_tft, heur_tft))
    elif ptype == "bilan":
        b_data = extract_bilan(path, engine)
        if b_data: _deep_update(results["bilan"], b_data)
    elif ptype == "cr":
        c_data = extract_cr(path, engine)
        if c_data: results["cr"].update(c_data)

def _apply_2_way_consensus(res1: dict, res2: dict) -> dict:
    if res1 is res2:
        return {key: {**value, "confidence": "source unique"} for key, value in res1.items()}
    consensus = {}
    for k in set(res1.keys()) | set(res2.keys()):
        v1 = res1.get(k, {}).get("net")
        v2 = res2.get(k, {}).get("net")
        if v1 == v2 and v1 is not None:
            consensus[k] = {"net": v1, "confidence": "unanime"}
        else:
            value = v1 if v1 is not None else v2
            consensus[k] = {"net": value, "confidence": "conflit"}
    return consensus

def _deep_update(d: dict, u: dict) -> dict:
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        elif v is not None and v != {}:
            d[k] = v
    return d
