"""
NagrikSaarathi — Authentication Schemas
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=120, description="Mobile number, email, or official ID")
    password: str = Field(..., min_length=6, max_length=120, description="User password")
    role: str = Field("citizen", pattern="^(citizen|official|admin)$", description="Login role: citizen, official, or admin")
    remember_me: bool = Field(False, description="Whether to remember session")


class RegisterRequest(BaseModel):
    """
    Request body for citizen self-registration.
    Public registration is strictly restricted to Citizens.
    Administrative roles (Official, Admin) cannot be obtained through self-registration.
    """
    full_name: str = Field(..., min_length=2, max_length=120, description="Full name of citizen")
    email: Optional[str] = Field(None, max_length=120, description="Email address (optional if mobile provided)")
    mobile: Optional[str] = Field(None, max_length=15, description="10-digit mobile number (optional if email provided)")
    password: str = Field(..., min_length=8, max_length=120, description="Password — min 8 chars")
    role: str = Field("citizen", pattern="^citizen$", description="Public registration is strictly for citizen role only")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        digits = re.sub(r"\D", "", v)
        if len(digits) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return digits

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        v = v.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("Invalid email address")
        return v


class RegisterResponse(BaseModel):
    """Response returned after successful citizen registration."""
    success: bool = True
    message: str
    user: "UserResponse"
    access_token: Optional[str] = None
    expires_in: Optional[int] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identifier: str
    role: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    state_scope: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    is_active: bool = True
    preferred_language: Optional[str] = "en"
    accessibility_settings: Optional[dict] = Field(default_factory=lambda: {"fontScale": 1, "highContrast": False})
    is_demo: bool = False


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    accessibility_settings: Optional[dict] = None


class OfficialCreateRequest(BaseModel):
    """Request by Principal Administrator to create a Department Official account."""
    identifier: str = Field(..., min_length=3, max_length=120, description="Email or official government username")
    email: Optional[str] = Field(None, max_length=120)
    full_name: str = Field(..., min_length=2, max_length=120)
    department: str = Field(..., min_length=2, max_length=150, description="Assigned government department name")
    state_scope: Optional[str] = Field(None, max_length=10, description="State/UT code or NULL for central")
    designation: Optional[str] = Field(None, max_length=120, description="Officer designation / title")
    password: str = Field(..., min_length=8, max_length=120)


class OfficialUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    state_scope: Optional[str] = None
    designation: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class OfficialInvitationCreate(BaseModel):
    """Request by Principal Administrator to issue an official onboarding invitation."""
    email: str = Field(..., min_length=5, max_length=120)
    full_name: str = Field(..., min_length=2, max_length=120)
    department: str = Field(..., min_length=2, max_length=200)
    state_scope: Optional[str] = Field(None, max_length=10)
    designation: Optional[str] = Field(None, max_length=120)
    allowed_permissions: List[str] = Field(default_factory=lambda: ["proposals", "evidence_review", "diff_radar", "translations"])
    expires_in_days: int = Field(7, ge=1, le=30)
    verification_method: str = Field("MANUAL_ADMIN_REVIEW", description="MANUAL_ADMIN_REVIEW | OFFICIAL_ID_REVIEW | PARICHAY_SSO")
    verification_notes: Optional[str] = None


class OfficialInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invitation_token: str
    email: str
    full_name: str
    department: str
    state_scope: Optional[str] = None
    designation: Optional[str] = None
    allowed_permissions: List[str] = Field(default_factory=list)
    status: str
    verification_method: str
    verification_notes: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: Optional[str] = None
    approved_at: Optional[str] = None
    activated_at: Optional[str] = None
    invited_by_id: int
    user_id: Optional[int] = None


class OfficialInvitationActivate(BaseModel):
    """Submission by prospective official to activate their account using an invitation token."""
    token: str = Field(..., min_length=10, max_length=120)
    password: str = Field(..., min_length=8, max_length=120)
    mobile: Optional[str] = Field(None, max_length=15)
    full_name: Optional[str] = None


class OfficialInvitationReview(BaseModel):
    """Decision by Principal Administrator to approve, modify, or reject an invitation activation."""
    approved: bool
    admin_notes: Optional[str] = None
    assigned_department: Optional[str] = None
    assigned_scope: Optional[str] = None
    allowed_permissions: Optional[List[str]] = None


class GovSSOConfigResponse(BaseModel):
    provider_name: str = "Parichay (National Single Sign-On - NSSO)"
    is_configured: bool = False
    status: str
    notice: str
    protocol: str
    required_claims: List[str]


class GovSSOCallbackRequest(BaseModel):
    auth_code: str
    state: str
    redirect_uri: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Payload to reset password. Security rule: never accepts role or department overrides."""
    identifier: str = Field(..., min_length=3, max_length=120)
    new_password: str = Field(..., min_length=8, max_length=120)



class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int


class DemoAccountInfo(BaseModel):
    role: str
    identifier: str
    password_hint: str
    description: str
    is_demo: bool = True


class DemoCredentialsResponse(BaseModel):
    demo_mode: bool
    notice: str
    accounts: List[DemoAccountInfo]
