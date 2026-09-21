import logging
import unicodedata
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def classify_page(ocr_words: List[Dict[str, Any]]) -> str:
    """Classe dynamiquement la page en analysant le texte OCR brut."""
    try:
        text_content = " ".join([str(w.get("text", "")).lower() for w in ocr_words])
        return _apply_classification_rules(text_content)
    except Exception as e:
        logger.error(f"Échec de la classification dynamique de la page: {e}")
        return "unknown"

def _apply_classification_rules(text_content: str) -> str:
    """Applique les règles de mots-clés pour définir la section financière."""
    text_clean = _normalize_text(text_content)
    if "bilan" in text_clean and ("actif" in text_clean or "passif" in text_clean):
        return "bilan"
    if "compte de resultat" in text_clean or "compte resultat" in text_clean or "marge commerciale" in text_clean:
        return "cr"
    if "flux de tresorerie" in text_clean or "tresorerie nette" in text_clean or "tableau des flux" in text_clean:
        return "tft"
    if "etat supplementaire" in text_clean or "etats supplementaires" in text_clean or "esdgi" in text_clean:
        return "esdgi"
    if "notes annexes" in text_clean or "note" in text_clean:
        return "notes"
    return "unknown"

def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))
