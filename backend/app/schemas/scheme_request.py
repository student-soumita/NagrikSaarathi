"""
NagrikSaarathi — Scheme Request Schemas
Pydantic schemas for citizen missing-scheme submissions and tracking.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SchemeRequestCreate(BaseModel):
    scheme_name: str = Field(..., min_length=2, max_length=250, description="Official or colloquial scheme name")
    government_level: str = Field("central", description="central, state, or ut")
    state_code: Optional[str] = Field(None, max_length=10, description="ISO state/UT code if applicable")
    department_name: Optional[str] = Field(None, max_length=250, description="Ministry or department name")
    description: Optional[str] = Field(None, description="What the scheme provides or citizen remarks")
    official_portal_url: Optional[str] = Field(None, max_length=500, description="Official portal or gazette URL if known")
    citizen_contact: Optional[str] = Field(None, max_length=120, description="Email or mobile for tracking without login")


class SchemeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_id: str
    user_id: Optional[int] = None
    citizen_contact: Optional[str] = None
    scheme_name: str
    government_level: str
    state_code: Optional[str] = None
    department_name: Optional[str] = None
    description: Optional[str] = None
    official_portal_url: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    linked_scheme_id: Optional[int] = None
    linked_scheme_slug: Optional[str] = None
    linked_scheme_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: Optional[datetime] = None


class SchemeRequestAdminUpdate(BaseModel):
    status: str = Field(..., description="Target status from SCHEME_REQUEST_STATUSES")
    admin_notes: Optional[str] = Field(None, description="Internal notes or citizen-facing feedback")
    rejection_reason: Optional[str] = Field(None, description="Reason if status is Rejected or Unable to Verify")
    linked_scheme_id: Optional[int] = Field(None, description="ID of existing scheme in government_schemes")


class SchemeRequestPublish(BaseModel):
    """Payload to create official catalogue scheme record and mark request as Added to Catalogue."""
    display_name: str = Field(..., min_length=2, max_length=200)
    category: str = Field("other", max_length=40)
    official_source_url: str = Field(..., min_length=5, max_length=500)
    official_application_url: Optional[str] = Field(None, max_length=500)
    department_name: Optional[str] = Field(None, max_length=200)
    beneficiary_groups: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(None)
    admin_notes: Optional[str] = Field(None)
