"""
Languages router for NagrikSaarathi API.

Exposes the 22 Eighth Schedule Indian languages with actual capability metadata.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Language
from backend.app.schemas.language import LanguageListResponse, LanguageResponse

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get("", response_model=LanguageListResponse)
def list_languages(
    enabled_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    List all configured Indian languages with native scripts and capability flags.
    Never assumes every language has voice capabilities.
    """
    query = select(Language)
    if enabled_only:
        query = query.where(Language.enabled == True)  # noqa: E712
    query = query.order_by(Language.english_name)

    languages = db.execute(query).scalars().all()
    items = [LanguageResponse.model_validate(lang) for lang in languages]
    return LanguageListResponse(total=len(items), items=items)


@router.get("/{language_code}", response_model=LanguageResponse)
def get_language(
    language_code: str,
    db: Session = Depends(get_db),
):
    """
    Fetch language details and capability metadata by language code.
    """
    lang = db.execute(
        select(Language).where(Language.language_code == language_code.lower())
    ).scalar_one_or_none()

    if not lang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language with code '{language_code}' is not configured.",
        )
    return LanguageResponse.model_validate(lang)
