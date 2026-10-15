"""
Assisted Sessions router for NagrikSaarathi API.

Privacy and Consent Guarantees:
- Only persists sessions in analytics database if explicit consent is given.
- If consent is declined, assistance proceeds in frontend memory without DB writes.
- Never records form values, PII, documents, or raw voice recordings.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AssistedSession, GovernmentScheme, SessionEvent
from backend.app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionEventCreateRequest,
    SessionEventResponse,
    SessionStatusUpdateRequest,
)

router = APIRouter(prefix="/sessions", tags=["Assisted Sessions"])


@router.post("", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Initiate a citizen assistance session.
    If analytics_consent is True, stores an anonymous session record for service improvement.
    If analytics_consent is False, returns an ephemeral session ID without database persistence.
    """
    # Verify scheme exists
    scheme = db.execute(
        select(GovernmentScheme).where(GovernmentScheme.id == payload.scheme_id)
    ).scalar_one_or_none()

    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {payload.scheme_id} does not exist.",
        )

    session_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    is_demo = payload.is_demo or scheme.is_demo

    if payload.analytics_consent:
        # Consent granted: persist anonymous record for aggregated barrier insights
        new_session = AssistedSession(
            id=session_id,
            scheme_id=payload.scheme_id,
            selected_language=payload.selected_language,
            channel=payload.channel,
            status="in_progress",
            analytics_consent=True,
            is_demo=is_demo,
            started_at=started_at,
        )
        db.add(new_session)
        db.commit()
        persisted = True
    else:
        # Consent declined: ephemeral assistance only
        persisted = False

    return SessionCreateResponse(
        session_id=session_id,
        scheme_id=payload.scheme_id,
        selected_language=payload.selected_language,
        channel=payload.channel,
        status="in_progress",
        analytics_consent=payload.analytics_consent,
        is_demo=is_demo,
        started_at=started_at,
        persisted=persisted,
        privacy_notice=(
            "Session recorded anonymously for barrier analytics with your consent."
            if persisted
            else "Consent declined: all assistance is strictly in-memory and not stored."
        ),
    )


@router.post("/{session_id}/events", response_model=SessionEventResponse, status_code=status.HTTP_201_CREATED)
def record_session_event(
    session_id: str,
    payload: SessionEventCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Record an anonymous structured lifecycle barrier event.
    Requires that the session exists and analytics consent was explicitly granted.
    Never accepts form values or personal citizen information.
    """
    session = db.execute(
        select(AssistedSession).where(AssistedSession.id == session_id)
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or session was not persisted due to lack of analytics consent.",
        )

    if not session.analytics_consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot record analytics events for a session where consent was declined.",
        )

    event = SessionEvent(
        session_id=session_id,
        field_key=payload.field_key,
        event_type=payload.event_type,
        barrier_category=payload.barrier_category,
        resolution_status=payload.resolution_status,
        language_code=payload.language_code or session.selected_language,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return SessionEventResponse.model_validate(event)


@router.patch("/{session_id}/status")
def update_session_status(
    session_id: str,
    payload: SessionStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Update session status (in_progress, completed, abandoned, needs_human_help).
    """
    session = db.execute(
        select(AssistedSession).where(AssistedSession.id == session_id)
    ).scalar_one_or_none()

    if not session:
        # If ephemeral session (consent declined), acknowledge gracefully
        return {"session_id": session_id, "status": payload.status, "persisted": False}

    session.status = payload.status
    if payload.status in ("completed", "abandoned"):
        session.ended_at = datetime.now(timezone.utc)

    db.commit()
    return {
        "session_id": session.id,
        "status": session.status,
        "ended_at": session.ended_at,
        "persisted": True,
    }
