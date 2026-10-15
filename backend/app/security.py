"""
NagrikSaarathi — Security & Access Control

Handles 3-tier role-based access control (Citizen, Official, Admin),
department & state geographic scoping, demo-mode authorization gates,
and administrative audit logging. Administrative secrets are never exposed.
"""

from __future__ import annotations

import hmac
from typing import Optional
from fastapi import Cookie, Depends, Header, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import AdminAuditLog, User

api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def verify_admin_token(token: Optional[str], settings: Settings) -> bool:
    """Safely verify incoming admin token using constant-time comparison or official/admin session token."""
    if not token:
        return False
    # 1. Direct API Key check
    if settings.admin_api_key and hmac.compare_digest(token.strip(), settings.admin_api_key.strip()):
        return True
    # 2. Signed session token check
    try:
        from backend.app.services.auth_service import decode_access_token
        payload = decode_access_token(token.strip(), settings.admin_api_key)
        if payload and payload.get("role") in ("admin", "official"):
            return True
    except Exception:
        pass
    return False


def require_admin_auth(
    api_key: Optional[str] = Security(api_key_header),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth),
) -> bool:
    """Enforce admin or official authorization via X-Admin-API-Key or Authorization Bearer header."""
    settings = get_settings()
    candidate = api_key or (bearer_creds.credentials if bearer_creds else None)

    if not verify_admin_token(candidate, settings):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin or Department Official authorization required to access protected analytics resources.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


def check_dashboard_access(
    include_demo: bool = True,
    api_key: Optional[str] = Security(api_key_header),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth),
) -> bool:
    """
    Allow public access ONLY if DEMO_MODE is true AND the request is for demo data.
    In production mode (DEMO_MODE=False) or when querying real data (include_demo=False),
    strictly enforce admin or department official authentication.
    """
    settings = get_settings()
    candidate = api_key or (bearer_creds.credentials if bearer_creds else None)

    # Check citizen role explicitly trying to access non-demo data
    if candidate:
        try:
            from backend.app.services.auth_service import decode_access_token
            payload = decode_access_token(candidate.strip(), settings.admin_api_key)
            if payload:
                if payload.get("role") in ("admin", "official"):
                    return True
                elif payload.get("role") == "citizen" and not include_demo:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied. Citizen accounts cannot access departmental analytics.",
                    )
        except HTTPException:
            raise
        except Exception:
            pass

    is_authenticated = verify_admin_token(candidate, settings)
    if is_authenticated:
        return True

    # If in demo mode and requesting demo/simulated analytics, permit public access
    if settings.demo_mode and include_demo:
        return False  # unauthenticated, but permitted for synthetic demo view

    # Otherwise (production or querying real observations unauthenticated) -> reject
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Real analytics or production environments require valid departmental credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ── Strict User Session Authentication ──────────────────────────────────────

def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    nagrik_session: Optional[str] = Cookie(None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and verify bearer token or HttpOnly session cookie.
    Enforces active account status; revoked/inactive users are immediately rejected (403).
    """
    token = None
    auth_header = authorization if isinstance(authorization, str) else (request.headers.get("authorization") if request else None)
    cookie_header = nagrik_session if isinstance(nagrik_session, str) else (request.cookies.get("nagrik_session") if request else None)

    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    elif cookie_header:
        token = cookie_header.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from backend.app.services.auth_service import decode_access_token
    payload = decode_access_token(token, settings.admin_api_key)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload.get("sub", 0))
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated or revoked. Please contact administrator.",
        )

    return user


def require_role(required_role: str):
    """Factory dependency to enforce specific server-verified user roles."""
    def _role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires '{required_role}' privileges.",
            )
        return user
    return _role_checker


def require_citizen_user(user: User = Depends(get_current_user)) -> User:
    """Require authenticated citizen user."""
    if user.role != "citizen":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires Citizen account.",
        )
    return user


def require_official_user(user: User = Depends(get_current_user)) -> User:
    """Require authenticated Department Official with an assigned department."""
    if user.role != "official":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires Department Official credentials.",
        )
    if not user.department or not user.department.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Official account is not assigned to any government department.",
        )
    return user


def require_admin_user(
    request: Request,
    api_key: Optional[str] = Security(api_key_header),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> User:
    """
    Require Principal Administrator privileges via session token or master X-Admin-API-Key.
    """
    # 1. Check if admin API key header provided
    if api_key and settings.admin_api_key and hmac.compare_digest(api_key.strip(), settings.admin_api_key.strip()):
        from sqlalchemy import select
        admin_user = db.execute(select(User).where(User.role == "admin")).scalars().first()
        if admin_user:
            return admin_user
        # Return fallback pseudo admin if none seeded yet
        return User(
            id=1,
            identifier="admin@nagrik.gov.in",
            email="admin@nagrik.gov.in",
            role="admin",
            full_name="Principal Administrator",
            department="National Informatics Centre",
            is_active=True,
        )

    # 2. Check session token
    user = get_current_user(request=request, settings=settings, db=db)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Requires Principal Administrator privileges.",
        )
    return user


def verify_official_scope(
    user: User,
    department_name: str,
    state_code: Optional[str] = None,
) -> None:
    """
    Strict department and state jurisdiction scope enforcement.
    Department Officials can ONLY view and propose changes for schemes
    matching their assigned department and optional state jurisdiction.
    """
    def _norm(s: Optional[str]) -> str:
        if not s:
            return ""
        val = s.lower().replace("&", " and ")
        for suffix in [", government of india", "government of india", "govt of india", "ministry of ", "department of "]:
            val = val.replace(suffix, "")
        return " ".join(val.split())

    norm_user = _norm(user.department)
    norm_target = _norm(department_name)

    matched = (norm_user == norm_target) or (norm_user in norm_target) or (norm_target in norm_user)
    if not matched:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Department Scope Violation: You are assigned to '{user.department}' and "
                f"cannot access or modify resources belonging to '{department_name}'."
            ),
        )

    if user.state_scope:
        user_state = user.state_scope.strip().upper()
        if state_code and state_code.strip().upper() != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Jurisdiction Scope Violation: Your jurisdiction is scoped to state '{user_state}', "
                    f"cannot perform actions for state '{state_code}'."
                ),
            )


def audit_log_action(
    db: Session,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AdminAuditLog:
    """
    Record an immutable audit log entry for administrative & official accountability.
    """
    log_entry = AdminAuditLog(
        user_id=user.id,
        user_identifier=user.identifier,
        user_role=user.role,
        department=user.department,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
