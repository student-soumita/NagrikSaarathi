"""
Language schemas for NagrikSaarathi API.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, ConfigDict, Field


class LanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    language_code: str = Field(..., description="ISO 639-1 / 639-3 language identifier")
    english_name: str = Field(..., description="English name (reference/internal only)")
    native_name: str = Field(..., description="Native name in indigenous script")
    writing_system: str = Field(..., description="Script / writing system metadata")
    direction: str = Field(..., description="'ltr' or 'rtl'")
    enabled: bool = Field(..., description="Whether language is enabled")
    supports_text: bool = Field(..., description="Actual capability: text interface support")
    supports_speech_recognition: bool = Field(
        ..., description="Actual capability: speech-to-text availability"
    )
    supports_text_to_speech: bool = Field(
        ..., description="Actual capability: text-to-speech availability"
    )


class LanguageListResponse(BaseModel):
    total: int
    items: List[LanguageResponse]
