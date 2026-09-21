import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def _flatten_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Aplatit une entrée de dictionnaire imbriquée."""
    row = {"fichier_source": entry.get("source_file", "Inconnu")}
    for category, values in entry.items():
        if not isinstance(values, dict): continue
        for k, v in values.items():
            if isinstance(v, dict):
                if "net" in v: row[f"{category}_{k}_net"] = v.get("net")
                if "brut" in v: row[f"{category}_{k}_brut"] = v.get("brut")
                if "amort" in v: row[f"{category}_{k}_amort"] = v.get("amort")
            else:
                row[f"{category}_{k}"] = v
    return row

def build_syscohada_db(data: List[Dict[str, Any]], output_path: str) -> bool:
    """Construit `bd_syscohada.xlsx` (1 ligne = 1 année/entreprise)."""
    try:
        import pandas as pd
        flat_data = [_flatten_entry(entry) for entry in data]
        pd.DataFrame(flat_data).to_excel(output_path, index=False)
        logger.info(f"Création DB SYSCOHADA ({len(data)} entrées) : {output_path}")
        return True
    except ImportError:
        logger.error("Pandas non installé. Échec création db_syscohada.")
        return False
    except Exception as e:
        logger.error(f"Échec création db_syscohada: {e}")
        return False

def _build_text_db(data: List[Dict[str, Any]], output_path: str, key: str) -> bool:
    """Helper générique pour construire les BD textuelles (Notes, ESDGI)."""
    try:
        import pandas as pd
        rows = []
        for entry in data:
            source = entry.get("source_file", "Inconnu")
            for item in entry.get(key, []):
                rows.append({"fichier_source": source, "page_id": item.get("page_id"), "contenu": item.get("content")})
        pd.DataFrame(rows).to_excel(output_path, index=False)
        logger.info(f"Création DB {key.upper()} ({len(rows)} entrées) : {output_path}")
        return True
    except Exception as e:
        logger.error(f"Échec création DB {key.upper()}: {e}")
        return False

def build_notes_db(data: List[Dict[str, Any]], output_path: str) -> bool:
    """Construit `bd_notes.xlsx` (tableaux Markdown purs)."""
    return _build_text_db(data, output_path, "notes")

def build_esdgi_db(data: List[Dict[str, Any]], output_path: str) -> bool:
    """Construit `bd_esdgi.xlsx` (tableaux Markdown purs)."""
    return _build_text_db(data, output_path, "esdgi")
