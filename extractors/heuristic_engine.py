import re
import logging
from typing import Dict, Any, List, Optional
try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)

# Cache global (Singleton) pour ne charger le modèle qu'une seule fois
_OCR_INSTANCE = None

def init_heuristic_engine(device: str = "cpu") -> Any:
    global _OCR_INSTANCE
    if _OCR_INSTANCE is None and PaddleOCR is not None:
        paddle_dev = "gpu" if device == "cuda" else "cpu"
        _OCR_INSTANCE = PaddleOCR(lang="fr", device=paddle_dev)
    return _OCR_INSTANCE

def extract_tft(image_path: str) -> Dict[str, Any]:
    """Applique l'heuristique géométrique pour le TFT."""
    engine = init_heuristic_engine()
    if not engine: return {}
    
    try:
        try:
            raw_result = engine.ocr(image_path)
        except TypeError:
            raw_result = engine.ocr(image_path, cls=True)
        if not raw_result or not raw_result[0]: return {}
        
        lines = _group_by_y(raw_result[0])
        return _extract_values_from_lines(lines)
    except Exception as e:
        logger.error(f"Erreur d'extraction heuristique TFT: {e}")
        return {}

def _group_by_y(items: List[Any], threshold: int = 15) -> List[List[Any]]:
    """Regroupe les blocs PaddleOCR par proximité verticale (lignes)."""
    items = sorted(items, key=lambda x: x[0][0][1]) # Tri par Y_min
    lines, current_line = [], []
    
    for item in items:
        y = item[0][0][1]
        if not current_line:
            current_line.append(item)
        else:
            avg_y = sum(i[0][0][1] for i in current_line) / len(current_line)
            if abs(y - avg_y) <= threshold:
                current_line.append(item)
            else:
                lines.append(sorted(current_line, key=lambda x: x[0][0][0]))
                current_line = [item]
                
    if current_line:
        lines.append(sorted(current_line, key=lambda x: x[0][0][0]))
    return lines

def _extract_values_from_lines(lines: List[List[Any]]) -> Dict[str, Any]:
    """Extrait le code référence (gauche) et la valeur nette (droite)."""
    tft_data = {}
    valid_refs = {"ZA", "FA", "FB", "FC", "FD", "FE", "BFR", "ZB", "FF", "FG", "FH", 
                  "FI", "FJ", "ZC", "FK", "FL", "FM", "FN", "ZD", "FO", "FP", "FQ", 
                  "ZE", "ZF", "ZG", "ZH"}
    
    for line in lines:
        full_text = " ".join([i[1][0] for i in line]).upper()
        # Trouver la réf à gauche
        refs = re.findall(r'\b([A-Z]{2}|BFR)\b', full_text)
        found_ref = next((r for r in refs if r in valid_refs), None)
        
        # S'il y a un mot spécial qui override
        if "VARIATION DU BFR" in full_text or "VARIATION GLOBALE DU BFR" in full_text:
            found_ref = "BFR"
            
        if found_ref:
            val = _parse_rightmost_number(line)
            if val is not None:
                tft_data[found_ref] = {"net": val}
                
    return tft_data

def _parse_rightmost_number(line: List[Any]) -> Optional[float]:
    """Parse le premier nombre valide en partant de la droite."""
    for item in reversed(line):
        text = item[1][0].replace(" ", "").replace("\u202f", "").replace(",", ".")
        # Gestion des parenthèses = négatif
        is_negative = bool(re.search(r'^\(.*\)$', text) or text.startswith("-"))
        text = re.sub(r'[^\d.]', '', text)
        if text.replace(".", "").isdigit():
            val = float(text)
            return -val if is_negative else val
    return None
