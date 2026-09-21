import gc
import logging

logger = logging.getLogger(__name__)

def free_memory() -> None:
    """Libère la mémoire RAM et GPU pour éviter les fuites (OOM)."""
    try:
        gc.collect()
        _free_gpu_memory()
    except Exception as e:
        logger.warning(f"Erreur lors de la libération mémoire: {e}")

def _free_gpu_memory() -> None:
    """Libère le cache CUDA si PyTorch ou Paddle sont disponibles."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

    try:
        import paddle
        if paddle.device.is_compiled_with_cuda():
            paddle.device.cuda.empty_cache()
    except ImportError:
        pass
