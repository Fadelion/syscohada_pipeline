import logging
import os
from typing import List, Optional, Any
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

logger = logging.getLogger(__name__)

def convert_pdf_to_images(pdf_path: str, output_dir: str, max_pages: int = None) -> List[str]:
    """Convertit les pages d'un PDF en images JPEG."""
    if not convert_from_path:
        logger.error("pdf2image non installé.")
        return []
    try:
        os.makedirs(output_dir, exist_ok=True)
        images = convert_from_path(pdf_path, dpi=200, last_page=max_pages)
        return _save_images(images, output_dir, os.path.basename(pdf_path))
    except Exception as e:
        logger.error(f"Échec conversion PDF {pdf_path}: {e}")
        return []

def _save_images(images: List[Any], output_dir: str, prefix: str) -> List[str]:
    """Sauvegarde les objets PIL Image sur le disque."""
    saved_paths = []
    for i, img in enumerate(images):
        path = os.path.join(output_dir, f"{prefix}_page_{i+1}.jpg")
        img.save(path, "JPEG")
        saved_paths.append(path)
    return saved_paths
