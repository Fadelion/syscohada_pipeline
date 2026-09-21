import logging
import re
from typing import Dict, Any, List, Optional
try:
    from paddleocr import PaddleOCRVL
except ImportError:
    PaddleOCRVL = None

logger = logging.getLogger(__name__)

def init_paddle_engine(device: str = "cpu") -> Optional[Any]:
    if not PaddleOCRVL: return None
    return PaddleOCRVL(pipeline_version="v1.6", device="gpu" if device == "cuda" else "cpu")

def extract_bilan(image_path: str, engine: Any) -> Dict[str, Any]:
    """Extraie le Bilan avec PaddleOCR-VL."""
    if not engine: return {}
    try:
        results = engine.predict(image_path)
        blocks = getattr(results, "parsing_res_list", [])
        return _parse_vl_bilan(blocks)
    except Exception as e:
        logger.error(f"Erreur PaddleVL Bilan: {e}")
        return {}

def extract_cr(image_path: str, engine: Any) -> Dict[str, Any]:
    """Extraie le CR avec PaddleOCR-VL."""
    if not engine: return {}
    try:
        results = engine.predict(image_path)
        blocks = getattr(results, "parsing_res_list", [])
        return _parse_vl_cr(blocks)
    except Exception as e:
        logger.error(f"Erreur PaddleVL CR: {e}")
        return {}

def _parse_vl_bilan(blocks: List[Any]) -> Dict[str, Any]:
    """Parse le Markdown VL pour trouver les codes Actif/Passif."""
    data = {"actif": {}, "passif": {}}
    for b in blocks:
        if getattr(b, "label", "") != "table": continue
        text = str(getattr(b, "content", "")).upper()
        # Logique simplifiée d'extraction (à enrichir avec regex exactes)
        for row in text.split('\n'):
            refs = re.findall(r'\b([A-D][A-Z])\b', row)
            nums = [float(re.sub(r'[^\d]', '', x)) for x in row.split('|') if re.sub(r'[^\d]', '', x)]
            if refs and nums:
                r = refs[0]
                if r.startswith(('A', 'B')):
                    data["actif"][r] = {"brut": nums[0]}
                elif r.startswith(('C', 'D')):
                    data["passif"][r] = {"net": nums[0]}
    return data

def _parse_vl_cr(blocks: List[Any]) -> Dict[str, Any]:
    """Parse le Markdown VL pour trouver les codes CR."""
    data = {}
    for b in blocks:
        if getattr(b, "label", "") != "table": continue
        text = str(getattr(b, "content", "")).upper()
        for row in text.split('\n'):
            refs = re.findall(r'\b([TXR][A-Z])\b', row)
            nums = [float(re.sub(r'[^\d]', '', x)) for x in row.split('|') if re.sub(r'[^\d]', '', x)]
            if refs and nums:
                data[refs[0]] = {"net": nums[0]}
    return data

def extract_raw_text_boxes(image_path: str, engine: Any) -> List[Dict[str, Any]]:
    if not engine: return []
    try:
        res = list(engine.predict(image_path))
        return [{"text": str(getattr(i, 'content', i))} for i in res]
    except Exception:
        return []
