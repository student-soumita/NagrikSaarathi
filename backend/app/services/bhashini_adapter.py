"""
BHASHINI / External Language Service Adapter (Layer B).

Handles communication with external language service APIs.
Strictly subject to provider access, valid credentials, timeouts, and error handling.
Does not assume every provider supports every language or capability.
Never exposes credentials or API keys.
"""

from __future__ import annotations

import logging
from typing import Optional
import httpx

from backend.app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class BhashiniAdapter:
    """Adapter for BHASHINI / external language translation and voice services."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        """Return True only if external endpoint and credentials are present."""
        return bool(
            self.settings.bhashini_endpoint
            and self.settings.bhashini_api_key
        )

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> Optional[str]:
        """
        Request dynamic translation from external provider with strict timeout.
        Returns translated string or None on failure/unconfigured.
        """
        if not self.is_configured:
            return None

        if source_lang == target_lang:
            return text

        url = f"{self.settings.bhashini_endpoint.rstrip('/')}/v1/translate"
        headers = {
            "Authorization": f"Bearer {self.settings.bhashini_api_key}",
            "Content-Type": "application/json",
        }
        if self.settings.bhashini_user_id:
            headers["x-user-id"] = self.settings.bhashini_user_id

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang,
                        }
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Parse standard response format safely
                    output = (
                        data.get("pipelineResponse", [{}])[0]
                        .get("output", [{}])[0]
                        .get("target")
                    )
                    return output
                else:
                    logger.warning(
                        "External translation provider returned status %d", response.status_code
                    )
                    return None
        except httpx.TimeoutException:
            logger.warning("External language provider timed out after %.1fs", self.settings.provider_timeout_seconds)
            return None
        except Exception as exc:
            logger.warning("Error calling external language provider: %s", type(exc).__name__)
            return None

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        language_code: str,
        mime_type: str = "audio/wav",
    ) -> Optional[str]:
        """
        Transcribe audio using external speech-to-text API.
        Never persists raw audio bytes to disk.
        """
        if not self.is_configured:
            return None

        url = f"{self.settings.bhashini_endpoint.rstrip('/')}/v1/asr"
        headers = {
            "Authorization": f"Bearer {self.settings.bhashini_api_key}",
        }
        files = {"file": ("audio.wav", audio_bytes, mime_type)}
        data = {"language": language_code}

        try:
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds) as client:
                response = await client.post(url, files=files, data=data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("transcript")
                return None
        except Exception as exc:
            logger.warning("External ASR failed or timed out: %s", type(exc).__name__)
            return None

    async def synthesize_speech(
        self,
        text: str,
        language_code: str,
    ) -> Optional[str]:
        """
        Synthesize speech into base64 audio.
        """
        if not self.is_configured:
            return None

        url = f"{self.settings.bhashini_endpoint.rstrip('/')}/v1/tts"
        headers = {
            "Authorization": f"Bearer {self.settings.bhashini_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"text": text, "language": language_code}

        try:
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("audio_base64")
                return None
        except Exception as exc:
            logger.warning("External TTS failed or timed out: %s", type(exc).__name__)
            return None
