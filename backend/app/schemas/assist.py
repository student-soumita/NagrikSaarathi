"""
Multilingual assistance schemas (explain & validate) for NagrikSaarathi API.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    scheme_id: int = Field(..., description="ID of the government scheme")
    field_key: str = Field(..., max_length=120, description="Field identifier")
    target_language: str = Field(..., max_length=10, description="Target language code (e.g. 'hi')")


class ExplainResponse(BaseModel):
    scheme_id: int
    field_key: str
    target_language: str
    original_label: str
    localized_label: str
    localized_explanation: str
    localized_instruction: str
    validation_guidance: Dict[str, Any] = Field(default_factory=dict)
    source_reference: Optional[str] = None
    translation_status: str = Field(
        ...,
        description="'approved', 'reviewed', 'draft', or 'missing'",
    )
    is_reviewed: bool = Field(..., description="True if human-reviewed or approved")
    is_fallback: bool = Field(..., description="True if localized content was missing or fallback used")
    provider_used: Optional[str] = Field(
        None, description="Translation engine/source: 'database_store', 'bhashini', or 'safe_fallback'"
    )
    disclaimer: str = Field(
        default="NagrikSaarathi provides guidance based on verified scheme guidelines; it does not submit applications to official government systems."
    )
    human_assistance_path: Optional[str] = Field(
        None, description="Guidance to request human desk assistance if localized text is missing or unclear"
    )


class ValidateRequest(BaseModel):
    scheme_id: int = Field(..., description="ID of the government scheme")
    field_key: str = Field(..., max_length=120, description="Field identifier to validate")
    value: Any = Field(..., description="Field value to validate deterministically against rules")
    target_language: str = Field(default="hi", max_length=10, description="Language for error feedback")


class ValidateResponse(BaseModel):
    is_valid: bool
    field_key: str
    target_language: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    applied_rule: Optional[Dict[str, Any]] = None
    official_source_url: Optional[str] = None
    disclaimer: str = Field(
        default="Deterministic validation is based solely on published form rules. Please check official documents for legal eligibility."
    )
