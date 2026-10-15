"""
NagrikSaarathi — Help & Support Ticket Router
Citizen-facing and self-service support workflows.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import HelpTicket, User
from backend.app.schemas.help_ticket import (
    HelpTicketCreate,
    HelpTicketFeedback,
    HelpTicketResponse,
)
from backend.app.services.auth_service import decode_access_token

router = APIRouter(prefix="/help", tags=["Help & Support"])


def _try_get_user(
    authorization: Optional[str] = Header(None),
    nagrik_session: Optional[str] = Cookie(None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optionally extract authenticated user if credentials exist, without raising 401."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif nagrik_session:
        token = nagrik_session.strip()

    if not token:
        return None

    payload = decode_access_token(token, settings.admin_api_key)
    if not payload:
        return None

    try:
        user_id = int(payload.get("sub", 0))
        return db.get(User, user_id)
    except Exception:
        return None


def _generate_ticket_number() -> str:
    year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    return f"TKT-{year}-{suffix}"


@router.post("/tickets", response_model=HelpTicketResponse, status_code=status.HTTP_201_CREATED)
def create_help_ticket(
    payload: HelpTicketCreate,
    user: Optional[User] = Depends(_try_get_user),
    db: Session = Depends(get_db),
):
    """
    Submit a citizen help & support ticket.
    Generates a unique tracking ticket number and saves to the database.
    """
    ticket_num = _generate_ticket_number()

    # Initial history log entry
    initial_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": "citizen",
        "action": "ticket_created",
        "details": f"Ticket submitted under category '{payload.category}'",
    }

    ticket = HelpTicket(
        ticket_number=ticket_num,
        user_id=user.id if user else None,
        citizen_name=payload.citizen_name or (user.full_name if user else None),
        citizen_contact=payload.citizen_contact.strip(),
        category=payload.category,
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        page_or_scheme_ref=payload.page_or_scheme_ref,
        status="Received",
        priority="medium",
        history=[initial_event],
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return HelpTicketResponse.model_validate(ticket)


@router.get("/tickets/track/{ticket_number}", response_model=HelpTicketResponse)
def track_help_ticket(
    ticket_number: str,
    contact: Optional[str] = Query(None, description="Optional email or phone for verification"),
    db: Session = Depends(get_db),
):
    """
    Public tracking endpoint for citizens to verify ticket status, resolution message, and history.
    """
    ticket = db.execute(
        select(HelpTicket).where(HelpTicket.ticket_number == ticket_number.strip().upper())
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Help ticket '{ticket_number}' not found.",
        )

    # Optional contact matching if supplied
    if contact and contact.strip().lower() not in ticket.citizen_contact.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contact details do not match the record on this ticket.",
        )

    return HelpTicketResponse.model_validate(ticket)


@router.get("/tickets/my", response_model=List[HelpTicketResponse])
def get_my_tickets(
    contact: Optional[str] = Query(None, description="Email or mobile number for guest lookup"),
    user: Optional[User] = Depends(_try_get_user),
    db: Session = Depends(get_db),
):
    """
    Fetch tickets submitted by the authenticated citizen, or by contact for visitors.
    """
    if user:
        tickets = db.execute(
            select(HelpTicket)
            .where((HelpTicket.user_id == user.id) | (HelpTicket.citizen_contact == user.identifier))
            .order_by(desc(HelpTicket.created_at))
        ).scalars().all()
    elif contact:
        tickets = db.execute(
            select(HelpTicket)
            .where(HelpTicket.citizen_contact == contact.strip())
            .order_by(desc(HelpTicket.created_at))
        ).scalars().all()
    else:
        return []

    return [HelpTicketResponse.model_validate(t) for t in tickets]


@router.post("/tickets/{ticket_number}/feedback", response_model=HelpTicketResponse)
def record_ticket_feedback(
    ticket_number: str,
    feedback: HelpTicketFeedback,
    db: Session = Depends(get_db),
):
    """
    Record citizen satisfaction for a resolved ticket.
    If satisfaction is False and citizen chooses to reopen, the ticket status returns to 'In Progress'.
    """
    ticket = db.execute(
        select(HelpTicket).where(HelpTicket.ticket_number == ticket_number.strip().upper())
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Help ticket '{ticket_number}' not found.",
        )

    ticket.satisfaction_solved = feedback.satisfaction_solved
    if feedback.feedback_notes:
        ticket.feedback_notes = feedback.feedback_notes.strip()

    history_list = list(ticket.history or [])
    now_str = datetime.now(timezone.utc).isoformat()

    if not feedback.satisfaction_solved and feedback.reopen:
        ticket.status = "In Progress"
        ticket.reopen_count = (ticket.reopen_count or 0) + 1
        history_list.append({
            "timestamp": now_str,
            "actor": "citizen",
            "action": "ticket_reopened",
            "details": f"Citizen indicated problem not resolved (reopen #{ticket.reopen_count}): {feedback.feedback_notes or 'No notes provided'}",
        })
    else:
        action_name = "feedback_solved" if feedback.satisfaction_solved else "feedback_unsolved"
        history_list.append({
            "timestamp": now_str,
            "actor": "citizen",
            "action": action_name,
            "details": f"Satisfaction: {'Solved' if feedback.satisfaction_solved else 'Unsolved'} - {feedback.feedback_notes or ''}",
        })

    ticket.history = history_list
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return HelpTicketResponse.model_validate(ticket)
