"""
Multilingual Assistance router for NagrikSaarathi API.

Provides:
- POST /api/assist/explain: localized field guidance with review status and fallback.
- POST /api/assist/validate: safe, deterministic rule validation without inventing government policies.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.assist import (
    ExplainRequest,
    ExplainResponse,
    ValidateRequest,
    ValidateResponse,
)
from backend.app.services.language_service import LanguageService
from backend.app.services.validation_service import ValidationService

router = APIRouter(prefix="/assist", tags=["Multilingual Guidance"])

_language_service = LanguageService()


@router.post("/explain", response_model=ExplainResponse)
async def explain_field(
    payload: ExplainRequest,
    db: Session = Depends(get_db),
):
    """
    Provide localized explanations, instructions, validation guidance, and review status.
    Uses Layer A (stored DB guidance), Layer B (optional dynamic provider), and Layer C (safe fallback).
    """
    response = await _language_service.get_field_explanation(
        db=db,
        scheme_id=payload.scheme_id,
        field_key=payload.field_key,
        target_language=payload.target_language.lower(),
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field '{payload.field_key}' not found in scheme {payload.scheme_id}.",
        )

    return response


@router.post("/validate", response_model=ValidateResponse)
def validate_field(
    payload: ValidateRequest,
    db: Session = Depends(get_db),
):
    """
    Deterministically validate a field value against published schema rules.
    Never invents legal requirements or eligibility rules.
    """
    result = ValidationService.validate_field_value(
        db=db,
        scheme_id=payload.scheme_id,
        field_key=payload.field_key,
        value=payload.value,
        target_language=payload.target_language.lower(),
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field '{payload.field_key}' not found in scheme {payload.scheme_id}.",
        )

    return result
