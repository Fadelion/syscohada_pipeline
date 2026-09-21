import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def validate_bilan(actif: Dict[str, Any], passif: Dict[str, Any]) -> bool:
    """Règle 1: Total Actif (BZ) doit être égal au Total Passif (DZ)."""
    try:
        total_actif = _get_value(actif, "BZ")
        total_passif = _get_value(passif, "DZ")
        if total_actif is None or total_passif is None:
            logger.warning("Bilan non validable: total Actif ou Passif absent")
            return False
        is_balanced = abs(total_actif - total_passif) < 2.0
        if not is_balanced:
            logger.warning(f"Bilan déséquilibré: Actif={total_actif}, Passif={total_passif}")
        return is_balanced
    except Exception as e:
        logger.error(f"Erreur validation bilan: {e}")
        return False

def compute_net(brut: float, amort: float) -> float:
    """Règle 2: Net = Brut - Amortissements (pour l'Actif)."""
    brut = brut or 0.0
    amort = amort or 0.0
    return round(brut - amort, 2)

def validate_tft(tft_data: Dict[str, Any]) -> bool:
    """Règle 3: Validation de la cohérence du TFT."""
    checks = _tft_checks(tft_data)
    if not checks:
        logger.warning("TFT non validable: aucune identité complète")
        return False
    return all(_is_close(actual, expected) for actual, expected in checks)

def _get_value(data: Dict[str, Any], code: str) -> Optional[float]:
    value = data.get(code)
    if not isinstance(value, dict):
        return None
    number = value.get("net")
    return float(number) if isinstance(number, (int, float)) else None

def _tft_checks(data: Dict[str, Any]) -> List[Tuple[float, float]]:
    checks = []
    checks.extend(_sum_check(data, "ZB", ["FA", "FB", "FC", "FD", "FE"]))
    checks.extend(_sum_check(data, "ZC", ["FF", "FG", "FH", "FI", "FJ"]))
    checks.extend(_sum_check(data, "ZD", ["FK", "FL", "FM", "FN"]))
    checks.extend(_sum_check(data, "ZE", ["FO", "FP", "FQ"]))
    checks.extend(_relation_check(data, "ZH", ["ZG", "ZA"]))
    return checks

def _sum_check(data: Dict[str, Any], total: str, parts: List[str]) -> List[Tuple[float, float]]:
    values = [_get_value(data, code) for code in [total] + parts]
    if any(value is None for value in values):
        return []
    return [(values[0], sum(values[1:]))]

def _relation_check(data: Dict[str, Any], total: str, parts: List[str]) -> List[Tuple[float, float]]:
    values = [_get_value(data, code) for code in [total] + parts]
    if any(value is None for value in values):
        return []
    return [(values[0], sum(values[1:]))]

def _is_close(actual: float, expected: float) -> bool:
    return abs(actual - expected) < 2.0
