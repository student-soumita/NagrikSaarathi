"""
Health check router for NagrikSaarathi API.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Language

router = APIRouter(tags=["System"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Verify application health, database connectivity, and configuration metadata.
    """
    db_healthy = False
    language_count = 0
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
        language_count = len(db.execute(select(Language.id)).all())
    except Exception:
        db_healthy = False

    return {
        "status": "ok" if db_healthy else "degraded",
        "service": "NagrikSaarathi API",
        "version": "0.1.0",
        "database_connected": db_healthy,
        "languages_configured": language_count,
        "demo_mode": settings.demo_mode,
        "disclaimer": "NagrikSaarathi provides citizen assistance; it does not submit applications to government systems.",
    }
