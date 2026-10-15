"""
NagrikSaarathi — Help & Support Ticket Schemas
Pydantic schemas for citizen support requests, tracking, and resolution feedback.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HelpTicketCreate(BaseModel):
    citizen_name: Optional[str] = Field(None, max_length=120, description="Full name of citizen")
    citizen_contact: str = Field(..., min_length=3, max_length=120, description="Email or 10-digit mobile number")
    category: str = Field(..., description="translation | guided_form_difficulty | eligibility_confusion | missing_scheme | incorrect_official_link | technical_error | other")
    subject: str = Field(..., min_length=3, max_length=250, description="Short summary of the issue")
    description: str = Field(..., min_length=10, description="Detailed explanation of the difficulty or question")
    page_or_scheme_ref: Optional[str] = Field(None, max_length=250, description="Page URL, form step, or scheme name")


class HelpTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    user_id: Optional[int] = None
    citizen_name: Optional[str] = None
    citizen_contact: str
    category: str
    subject: str
    description: str
    page_or_scheme_ref: Optional[str] = None
    status: str
    priority: str
    admin_notes: Optional[str] = None
    resolution_message: Optional[str] = None
    satisfaction_solved: Optional[bool] = None
    feedback_notes: Optional[str] = None
    reopen_count: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class HelpTicketAdminUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Received | Open | In Progress | Waiting for Citizen | Resolved | Closed")
    priority: Optional[str] = Field(None, description="low | medium | high | urgent")
    admin_notes: Optional[str] = Field(None, description="Internal notes")
    resolution_message: Optional[str] = Field(None, description="Citizen-facing resolution details")


class HelpTicketFeedback(BaseModel):
    satisfaction_solved: bool = Field(..., description="True if solved, False if citizen needs further help")
    feedback_notes: Optional[str] = Field(None, description="Citizen feedback or additional question")
    reopen: bool = Field(False, description="True to reopen the ticket if unsatisfied")
