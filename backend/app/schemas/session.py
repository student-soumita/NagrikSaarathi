"""
AssistedSession and SessionEvent schemas for NagrikSaarathi API.

Privacy guarantee:
Zero PII or form answers in request or response schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

SessionChannel = Literal["web", "assisted_desk"]
SessionStatus = Literal["in_progress", "completed", "abandoned", "needs_human_help"]
EventType = Literal[
    "help_requested",
    "voice_used",
    "validation_failed",
    "field_completed",
    "issue_resolved",
    "issue_unresolved",
    "application_completed",
    "abandoned",
    "human_help_requested",
]
BarrierCategory = Literal[
    "confusing_question",
    "missing_document",
    "language_difficulty",
    "validation_error",
    "technical_failure",
    "other",
]
ResolutionStatus = Literal["resolved", "unresolved", "escalated"]


class SessionCreateRequest(BaseModel):
    scheme_id: int = Field(..., description="Target government scheme ID")
    selected_language: str = Field(..., max_length=10, description="Preferred language code (e.g. 'hi')")
    channel: SessionChannel = Field(default="web", description="Service delivery channel")
    analytics_consent: bool = Field(
        ...,
        description="Explicit citizen consent for aggregated anonymous barrier analytics",
    )
    is_demo: bool = Field(
        default=False,
        description="Whether this is a synthetic demonstration session",
    )


class SessionCreateResponse(BaseModel):
    session_id: str
    scheme_id: int
    selected_language: str
    channel: str
    status: str
    analytics_consent: bool
    is_demo: bool
    started_at: datetime
    persisted: bool = Field(
        ...,
        description="True if stored in database; False if in-memory/ephemeral (consent declined)",
    )
    privacy_notice: str


class SessionStatusUpdateRequest(BaseModel):
    status: SessionStatus = Field(..., description="New session status")


class SessionEventCreateRequest(BaseModel):
    field_key: Optional[str] = Field(None, max_length=120, description="Field identifier (no user value)")
    event_type: EventType = Field(..., description="Structured lifecycle event type")
    barrier_category: Optional[BarrierCategory] = Field(None, description="Optional barrier category")
    resolution_status: Optional[ResolutionStatus] = Field(None, description="Optional resolution status")
    language_code: Optional[str] = Field(None, max_length=10, description="Language code during event")


class SessionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    field_key: Optional[str]
    event_type: str
    barrier_category: Optional[str]
    resolution_status: Optional[str]
    language_code: Optional[str]
    created_at: datetime
