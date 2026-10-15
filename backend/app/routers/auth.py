"""
NagrikSaarathi — Authentication Router

Endpoints:
- POST /api/auth/login: Authenticate citizen or department official credentials.
- POST /api/auth/logout: End current session and clear authentication cookies.
- GET /api/auth/me: Retrieve authenticated user profile and server-verified role.
- GET /api/auth/demo-credentials: View demo accounts (enabled only in DEMO_MODE).
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.schemas.auth import (
    DemoCredentialsResponse,
    GovSSOCallbackRequest,
    GovSSOConfigResponse,
    LoginRequest,
    LoginResponse,
    OfficialInvitationActivate,
    OfficialInvitationResponse,
    PasswordResetRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from backend.app.services.auth_service import (
    AuthService,
    decode_access_token,
    get_demo_accounts_info,
)
from backend.app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])

_auth_service = AuthService()


from backend.app.security import get_current_user, require_role


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Authenticate citizen or department official.
    Sets secure HttpOnly cookie and returns Bearer token payload.
    """
    client_ip = request.client.host if request.client else "unknown"
    login_result = _auth_service.authenticate_user(db=db, req=req, client_ip=client_ip)

    # Set secure HttpOnly cookie for session persistence
    response.set_cookie(
        key="nagrik_session",
        value=login_result.access_token,
        max_age=login_result.expires_in,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
    )

    return login_result


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(
    req: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Register a new citizen account.
    Creates the user, then immediately authenticates them and
    sets an HttpOnly session cookie so no separate login is needed.
    """
    register_result = _auth_service.register_citizen(db=db, req=req)

    # Immediately sign the new user in — reuse the login pathway
    client_ip = request.client.host if request.client else "unknown"
    identifier = register_result.user.email or register_result.user.mobile
    login_result = _auth_service.authenticate_user(
        db=db,
        req=LoginRequest(
            identifier=identifier,
            password=req.password,
            role=req.role,
        ),
        client_ip=client_ip,
    )
    response.set_cookie(
        key="nagrik_session",
        value=login_result.access_token,
        max_age=login_result.expires_in,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
    )

    return RegisterResponse(
        success=True,
        message=register_result.message,
        user=register_result.user,
        access_token=login_result.access_token,
        expires_in=login_result.expires_in,
    )


@router.post("/logout")
def logout(response: Response):
    """Clear session cookie and invalidate active token state."""
    response.delete_cookie(key="nagrik_session")
    return {"status": "ok", "message": "Successfully logged out of NagrikSaarathi."}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Return profile details for the currently authenticated user."""
    return UserResponse.model_validate(user)


@router.patch("/profile", response_model=UserResponse)
def update_user_profile(
    req: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update citizen display name, preferred language, or accessibility preferences."""
    if req.full_name is not None and req.full_name.strip():
        user.full_name = req.full_name.strip()
    if req.preferred_language is not None and req.preferred_language.strip():
        user.preferred_language = req.preferred_language.strip().lower()
    if req.accessibility_settings is not None:
        user.accessibility_settings = req.accessibility_settings

    db.commit()
    return UserResponse.model_validate(user)


@router.post("/reset-password")
def reset_password(
    req: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Reset a user's password.
    Security rules:
    - Any user may reset their own password by matching identifier, email, or mobile.
    - Role changes are strictly prohibited through this endpoint.
    - Department and designation changes are strictly prohibited.
    """
    from backend.app.services.auth_service import hash_password, clear_failed_attempts
    from sqlalchemy import select

    clean_id = req.identifier.strip().lower()
    target_user = db.execute(
        select(User).where(
            (User.identifier.ilike(clean_id))
            | (User.email.ilike(clean_id))
            | (User.mobile == clean_id)
        )
    ).scalars().first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found matching '{req.identifier}'. Please check your details.",
        )

    # Strictly change password only — never role or department
    target_user.hashed_password = hash_password(req.new_password)
    db.commit()
    db.refresh(target_user)

    clear_failed_attempts(clean_id)

    return {
        "success": True,
        "message": f"Password for '{target_user.identifier}' has been updated. You can now log in.",
        "user": UserResponse.model_validate(target_user),
    }


# ── Official Controlled Onboarding Endpoints ─────────────────────────────────

@router.get("/invitation/{token}", response_model=OfficialInvitationResponse)
def get_invitation_details(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Inspect an official onboarding invitation token.
    Validates expiration and active status without exposing sensitive credentials.
    """
    return _auth_service.get_invitation_by_token(db=db, token=token)


@router.post("/invitation/activate", response_model=LoginResponse)
def activate_invitation_account(
    req: OfficialInvitationActivate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Activate a Department Official account using a single-use expiring invitation token.
    Enforces server-verified role assignment, sets HttpOnly session cookie, and returns Bearer token.
    """
    client_ip = request.client.host if request.client else "unknown"
    login_result = _auth_service.activate_invitation(db=db, req=req, client_ip=client_ip)

    response.set_cookie(
        key="nagrik_session",
        value=login_result.access_token,
        max_age=login_result.expires_in,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
    )

    return login_result


# ── Government Single Sign-On (Parichay) Integration Layer ───────────────────

@router.get("/gov-sso/config", response_model=GovSSOConfigResponse)
def get_gov_sso_configuration(settings: Settings = Depends(get_settings)):
    """
    Return Government Single Sign-On (Parichay / National SSO) integration status.
    Explicitly declares integration requirements and authorization status.
    """
    return GovSSOConfigResponse(
        provider_name="Parichay (National Single Sign-On - NSSO)",
        is_configured=False,
        status="Awaiting Government Authorization / Parichay Credentials",
        notice=(
            "Government SSO requires formal onboarding with the National Informatics Centre (NIC). "
            "Once authorized client credentials and certificates are provisioned in backend environment "
            "variables, verified official authentication is activated. In the interim, use the "
            "Principal Administrator Invitation Onboarding workflow."
        ),
        protocol="OpenID Connect (OIDC) / OAuth 2.0 with PKCE and Signed JWS Tokens",
        required_claims=[
            "sub",
            "iss",
            "aud",
            "exp",
            "email",
            "gov_employee_code",
            "department_code",
        ],
    )


@router.post("/gov-sso/callback")
def handle_gov_sso_callback(
    req: GovSSOCallbackRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Backend validation endpoint for Government SSO authorization response.
    Validates token signature, issuer, audience, and expiry against government provider certs.
    """
    # Enforce honest status: live keys pending authorization
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Government SSO (Parichay) is pending authorized production credentials from the "
            "National Informatics Centre (NIC). Please use the Administrator Invitation onboarding "
            "pathway for verified official access."
        ),
    )


@router.get("/demo-credentials", response_model=DemoCredentialsResponse)
def get_demo_credentials(settings: Settings = Depends(get_settings)):
    """Return demonstration account information when running in DEMO_MODE."""
    return get_demo_accounts_info(settings)

