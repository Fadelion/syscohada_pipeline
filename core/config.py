import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detect_hardware() -> str:
    """Detects available hardware and returns 'cuda' or 'cpu'."""
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("CUDA detected. GPU will be used.")
            return "cuda"
        logger.info("CUDA not available. CPU fallback activated.")
        return "cpu"
    except ImportError:
        logger.warning("PyTorch not found. Defaulting to CPU.")
        return "cpu"
    except Exception as e:
        logger.warning(f"Hardware detection failed: {e}. Defaulting to CPU.")
        return "cpu"

def get_base_config() -> Dict[str, Any]:
    """Returns the base configuration dictionary for the pipeline."""
    return {
        "device": detect_hardware(),
        "checkpoint_dir": os.getenv("SYSCOHADA_CHECKPOINT_DIR", "./checkpoints"),
        "log_level": os.getenv("SYSCOHADA_LOG_LEVEL", "INFO"),
    }
