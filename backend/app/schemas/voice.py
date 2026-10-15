"""
Voice service schemas for NagrikSaarathi API.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    language_code: str
    transcript: str
    provider: str
    audio_processed_bytes: int
    disclaimer: str = Field(
        default="Audio is processed ephemerally in-memory and raw recordings are never retained on the server."
    )


class SpeakRequest(BaseModel):
    text: str = Field(..., max_length=1000, description="Text to synthesize")
    language_code: str = Field(..., max_length=10, description="Target language code")


class SpeakResponse(BaseModel):
    language_code: str
    audio_base64: Optional[str] = None
    audio_format: str = "audio/wav"
    provider: str
    disclaimer: str = Field(
        default="Synthesized audio is generated on-demand without logging personal text inputs."
    )
