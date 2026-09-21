import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def _get_checkpoint_path(doc_id: str, checkpoint_dir: str) -> Path:
    """Returns the Path object for a given document's checkpoint file."""
    return Path(checkpoint_dir) / f"{doc_id}_checkpoint.json"

def init_checkpoint_dir(checkpoint_dir: str) -> None:
    """Creates the checkpoint directory if it does not exist."""
    try:
        os.makedirs(checkpoint_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create checkpoint directory: {e}")
        raise

def save_checkpoint(doc_id: str, state: Dict[str, Any], checkpoint_dir: str) -> bool:
    """Saves the current processing state to a JSON checkpoint file."""
    try:
        init_checkpoint_dir(checkpoint_dir)
        filepath = _get_checkpoint_path(doc_id, checkpoint_dir)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving checkpoint for {doc_id}: {e}")
        return False

def load_checkpoint(doc_id: str, checkpoint_dir: str) -> Optional[Dict[str, Any]]:
    """Loads a document's processing state from its checkpoint file."""
    filepath = _get_checkpoint_path(doc_id, checkpoint_dir)
    if not filepath.exists():
        return None
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading checkpoint for {doc_id}: {e}")
        return None
