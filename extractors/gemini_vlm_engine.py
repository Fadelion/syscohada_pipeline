import os
import json
import time
import logging
from typing import Dict, Any, Optional
from PIL import Image
from google import genai
from google.genai import types
from syscohada_pipeline.core.prompts import PROMPT_BILAN, PROMPT_CR

logger = logging.getLogger(__name__)

def extract_bilan(image_path: str) -> Optional[Dict[str, Any]]:
    res = _call_gemini(image_path, PROMPT_BILAN, is_json=True)
    return json.loads(res) if res else None

def extract_cr(image_path: str) -> Optional[Dict[str, Any]]:
    res = _call_gemini(image_path, PROMPT_CR, is_json=True)
    return json.loads(res) if res else None

def extract_notes(image_path: str) -> Optional[str]:
    from syscohada_pipeline.core.prompts import PROMPT_NOTES
    return _call_gemini(image_path, PROMPT_NOTES, is_json=False)

def extract_esdgi(image_path: str) -> Optional[str]:
    from syscohada_pipeline.core.prompts import PROMPT_ESDGI
    return _call_gemini(image_path, PROMPT_ESDGI, is_json=False)

def _call_gemini(image_path: str, prompt: str, is_json: bool) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return None
    client = genai.Client(api_key=api_key)
    for attempt in range(5):
        result = _request_gemini(client, image_path, prompt, is_json, attempt)
        if result is not None:
            return result
    return None

def _request_gemini(client: Any, image_path: str, prompt: str, is_json: bool, attempt: int) -> Optional[str]:
    try:
        img = Image.open(image_path)
        mime = "application/json" if is_json else "text/plain"
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_mime_type=mime, temperature=0.0)
        )
        return response.text.strip()
    except Exception as exc:
        _handle_gemini_error(exc, image_path, attempt)
        return None

def _handle_gemini_error(error: Exception, image_path: str, attempt: int) -> None:
    message = str(error)
    if "429" in message or "RESOURCE_EXHAUSTED" in message:
        wait_time = 8 * (attempt + 1)
        logger.warning("Quota Gemini atteint (429). Attente de %ss...", wait_time)
        time.sleep(wait_time)
    elif "503" in message or "UNAVAILABLE" in message:
        logger.warning("Service Gemini indisponible (503). Attente...")
        time.sleep(3)
    else:
        logger.error("Échec Gemini sur %s: %s", image_path, error)
