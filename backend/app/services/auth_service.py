"""
NagrikSaarathi — Authentication Service

Provides:
- Secure PBKDF2-HMAC-SHA256 password hashing.
- Cryptographically signed HMAC-SHA256 session tokens with department & state scoping.
- Server-side credential validation with 3-tier role-based access control.
- In-memory rate-limiting defense against credential stuffing.
- Demo account handling strictly isolated to DEMO_MODE.
- Principal Administrator management for Department Official accounts.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.models import AdminAuditLog, Department, OfficialInvitation, User
from backend.app.schemas.auth import (
    DemoAccountInfo,
    DemoCredentialsResponse,
    LoginRequest,
    LoginResponse,
    OfficialCreateRequest,
    OfficialInvitationActivate,
    OfficialInvitationCreate,
    OfficialInvitationResponse,
    OfficialInvitationReview,
    OfficialUpdateRequest,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

# In-memory attempt tracking for rate-limiting: identifier_or_ip -> [(timestamp), ...]
_attempt_tracker: Dict[str, List[float]] = {}
MAX_ATTEMPTS = 10
ATTEMPT_WINDOW_SECONDS = 600  # 10 minutes


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a random 16-byte salt."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2_sha256$100000${salt.hex()}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password in constant time."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iters = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_dk = bytes.fromhex(parts[3])
        dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, expected_dk)
    except Exception:
        return False


# ── Session / Access Token ───────────────────────────────────────────────────

def create_access_token(
    user_id: int,
    identifier: str,
    role: str,
    secret_key: str,
    department: Optional[str] = None,
    state_scope: Optional[str] = None,
    expires_in_seconds: int = 86400,
) -> str:
    """Generate an HMAC-SHA256 signed session token including role and department scopes."""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "identifier": identifier,
        "role": role,
        "department": department,
        "state_scope": state_scope,
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    sig = hmac.new(
        secret_key.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def decode_access_token(token: str, secret_key: str) -> Optional[dict]:
    """Decode and verify an HMAC-SHA256 signed session token."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig_b64 = parts

        # Verify signature in constant time
        expected_sig = hmac.new(
            secret_key.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        # Decode JSON payload
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8")
        payload = json.loads(payload_json)

        # Check expiration
        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None


# ── Rate Limiting ─────────────────────────────────────────────────────────────

def check_rate_limit(key: str) -> None:
    """Enforce maximum failed login attempts per key within window."""
    now = time.time()
    attempts = _attempt_tracker.get(key, [])
    valid_attempts = [t for t in attempts if now - t < ATTEMPT_WINDOW_SECONDS]
    _attempt_tracker[key] = valid_attempts

    if len(valid_attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please wait 5 minutes before trying again.",
        )


def record_failed_attempt(key: str) -> None:
    now = time.time()
    attempts = _attempt_tracker.get(key, [])
    attempts.append(now)
    _attempt_tracker[key] = attempts


def clear_failed_attempts(key: str) -> None:
    _attempt_tracker.pop(key, None)


# ── Demo Accounts (Strictly in DEMO_MODE) ──────────────────────────────────────

DEMO_CITIZEN_PASSWORD = "Citizen@2026"
DEMO_OFFICIAL_PASSWORD = "Officer@2026"
DEMO_ADMIN_PASSWORD = "Admin@2026"


def get_demo_accounts_info(settings: Settings) -> DemoCredentialsResponse:
    """Return demonstration credentials metadata for all 3 access tiers."""
    if not settings.demo_mode:
        return DemoCredentialsResponse(
            demo_mode=False,
            notice="Demonstration accounts are disabled in production mode.",
            accounts=[],
        )

    return DemoCredentialsResponse(
        demo_mode=True,
        notice="Demonstration credentials for hackathon preview and testing only.",
        accounts=[
            DemoAccountInfo(
                role="citizen",
                identifier="9876543210",
                password_hint=DEMO_CITIZEN_PASSWORD,
                description="Citizen demo login with pre-configured profile, requests, and tickets.",
                is_demo=True,
            ),
            DemoAccountInfo(
                role="official",
                identifier="officer@dept.gov.in",
                password_hint=DEMO_OFFICIAL_PASSWORD,
                description="Agriculture Department Official (Ministry of Agriculture and Farmers Welfare).",
                is_demo=True,
            ),
            DemoAccountInfo(
                role="official",
                identifier="officer.edu@dept.gov.in",
                password_hint=DEMO_OFFICIAL_PASSWORD,
                description="Higher Education Official (Department of Higher Education) for cross-department tests.",
                is_demo=True,
            ),
            DemoAccountInfo(
                role="admin",
                identifier="admin@nagrik.gov.in",
                password_hint=DEMO_ADMIN_PASSWORD,
                description="Principal Administrator with full governance, review, approval, and audit authority.",
                is_demo=True,
            ),
        ],
    )


def _is_expired(expires_at: Optional[datetime], now: Optional[datetime] = None) -> bool:
    if not expires_at:
        return False
    if now is None:
        now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return expires_at < now


# ── Authentication Service Class ──────────────────────────────────────────────

class AuthService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def authenticate_user(
        self,
        db: Session,
        req: LoginRequest,
        client_ip: str = "unknown",
    ) -> LoginResponse:
        """
        Authenticate user credentials against DB or demo accounts (if in demo mode).
        Applies role check, rate limiting, and safe generic error reporting.
        """
        rate_key = f"{client_ip}:{req.identifier.strip().lower()}"
        check_rate_limit(rate_key)

        settings = get_settings()
        clean_id = req.identifier.strip().lower()
        role = req.role.strip().lower()

        # 1. Check Demo Accounts if in DEMO_MODE
        if settings.demo_mode:
            # Citizen Demo
            if role == "citizen" and clean_id in ("9876543210", "citizen@nagrik.gov.in"):
                if req.password == DEMO_CITIZEN_PASSWORD:
                    clear_failed_attempts(rate_key)
                    user = self._get_or_create_demo_user(
                        db=db,
                        identifier="9876543210",
                        email="citizen@nagrik.gov.in",
                        mobile="9876543210",
                        role="citizen",
                        full_name="नागरिक उपयोगकर्ता (Demo Citizen)",
                    )
                    expires = 7 * 86400 if req.remember_me else 86400
                    token = create_access_token(
                        user_id=user.id,
                        identifier=user.identifier,
                        role=user.role,
                        secret_key=settings.admin_api_key,
                        expires_in_seconds=expires,
                    )
                    return LoginResponse(
                        access_token=token,
                        token_type="bearer",
                        user=UserResponse.model_validate(user),
                        expires_in=expires,
                    )

            # Official Demo (Agriculture)
            elif role == "official" and clean_id in ("officer@dept.gov.in", "officer_2026"):
                if req.password == DEMO_OFFICIAL_PASSWORD:
                    clear_failed_attempts(rate_key)
                    user = self._get_or_create_demo_user(
                        db=db,
                        identifier="officer@dept.gov.in",
                        email="officer@dept.gov.in",
                        mobile=None,
                        role="official",
                        full_name="विभागीय नोडल अधिकारी (Department Officer)",
                        department="Ministry of Agriculture and Farmers Welfare",
                        designation="Nodal Scheme Officer (Agriculture)",
                    )
                    expires = 7 * 86400 if req.remember_me else 86400
                    token = create_access_token(
                        user_id=user.id,
                        identifier=user.identifier,
                        role=user.role,
                        secret_key=settings.admin_api_key,
                        department=user.department,
                        state_scope=user.state_scope,
                        expires_in_seconds=expires,
                    )
                    return LoginResponse(
                        access_token=token,
                        token_type="bearer",
                        user=UserResponse.model_validate(user),
                        expires_in=expires,
                    )

            # Official Demo (Education)
            elif role == "official" and clean_id in ("officer.edu@dept.gov.in",):
                if req.password == DEMO_OFFICIAL_PASSWORD:
                    clear_failed_attempts(rate_key)
                    user = self._get_or_create_demo_user(
                        db=db,
                        identifier="officer.edu@dept.gov.in",
                        email="officer.edu@dept.gov.in",
                        mobile=None,
                        role="official",
                        full_name="शिक्षा विभाग अधिकारी (Higher Education Officer)",
                        department="Department of Higher Education",
                        designation="Joint Director (Scholarships)",
                    )
                    expires = 7 * 86400 if req.remember_me else 86400
                    token = create_access_token(
                        user_id=user.id,
                        identifier=user.identifier,
                        role=user.role,
                        secret_key=settings.admin_api_key,
                        department=user.department,
                        state_scope=user.state_scope,
                        expires_in_seconds=expires,
                    )
                    return LoginResponse(
                        access_token=token,
                        token_type="bearer",
                        user=UserResponse.model_validate(user),
                        expires_in=expires,
                    )

            # Admin Demo
            elif role == "admin" and clean_id in ("admin@nagrik.gov.in", "admin"):
                if req.password == DEMO_ADMIN_PASSWORD:
                    clear_failed_attempts(rate_key)
                    user = self._get_or_create_demo_user(
                        db=db,
                        identifier="admin@nagrik.gov.in",
                        email="admin@nagrik.gov.in",
                        mobile=None,
                        role="admin",
                        full_name="मुख्य प्रशासनिक अधिकारी (Principal Administrator)",
                        department="National Informatics Centre & MoE",
                        designation="Principal System Administrator",
                    )
                    expires = 7 * 86400 if req.remember_me else 86400
                    token = create_access_token(
                        user_id=user.id,
                        identifier=user.identifier,
                        role=user.role,
                        secret_key=settings.admin_api_key,
                        department=user.department,
                        state_scope=user.state_scope,
                        expires_in_seconds=expires,
                    )
                    return LoginResponse(
                        access_token=token,
                        token_type="bearer",
                        user=UserResponse.model_validate(user),
                        expires_in=expires,
                    )

        # 2. Check Database Users
        user = db.execute(
            select(User).where(
                (User.identifier.ilike(clean_id))
                | (User.email.ilike(clean_id))
                | (User.mobile == clean_id)
            )
        ).scalar_one_or_none()

        if not user or user.role != role:
            record_failed_attempt(rate_key)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or incorrect login role. Please verify your details.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is currently inactive or revoked. Please contact administrator.",
            )

        if not verify_password(req.password, user.hashed_password):
            record_failed_attempt(rate_key)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or incorrect login role. Please verify your details.",
            )

        # Successful DB login
        clear_failed_attempts(rate_key)
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()

        expires = 7 * 86400 if req.remember_me else 86400
        token = create_access_token(
            user_id=user.id,
            identifier=user.identifier,
            role=user.role,
            secret_key=settings.admin_api_key,
            department=user.department,
            state_scope=user.state_scope,
            expires_in_seconds=expires,
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
            expires_in=expires,
        )

    def _get_or_create_demo_user(
        self,
        db: Session,
        identifier: str,
        role: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        full_name: Optional[str] = None,
        department: Optional[str] = None,
        designation: Optional[str] = None,
        state_scope: Optional[str] = None,
    ) -> User:
        """Find or create demonstration user record in database."""
        user = db.execute(
            select(User).where(User.identifier == identifier)
        ).scalar_one_or_none()

        if user is None:
            raw_pwd = (
                DEMO_CITIZEN_PASSWORD if role == "citizen"
                else DEMO_ADMIN_PASSWORD if role == "admin"
                else DEMO_OFFICIAL_PASSWORD
            )
            user = User(
                identifier=identifier,
                email=email,
                mobile=mobile,
                hashed_password=hash_password(raw_pwd),
                role=role,
                full_name=full_name,
                department=department,
                designation=designation,
                state_scope=state_scope,
                is_active=True,
                is_demo=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    def register_citizen(
        self,
        db: Session,
        req: RegisterRequest,
    ) -> RegisterResponse:
        """Register a new citizen account."""
        settings = get_settings()

        email = (req.email or "").strip().lower() or None
        mobile = (req.mobile or "").strip() or None

        if not email and not mobile:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please provide at least an email address or a mobile number.",
            )

        identifier = email or mobile

        existing = db.execute(
            select(User).where(
                (User.identifier == identifier)
                | (User.email == email if email else False)
                | (User.mobile == mobile if mobile else False)
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email or mobile number already exists. Please sign in.",
            )

        # Public registration is strictly restricted to Citizen role
        if req.role != "citizen":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Public registration is restricted to citizens. Department Officials must be onboarded through Administrator invitation.",
            )

        new_user = User(
            identifier=identifier,
            email=email,
            mobile=mobile,
            hashed_password=hash_password(req.password),
            role="citizen",
            full_name=req.full_name.strip(),
            department=None,
            designation=None,
            state_scope=None,
            is_active=True,
            is_demo=False,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        expires = 86400  # 24 hours
        token = create_access_token(
            user_id=new_user.id,
            identifier=new_user.identifier,
            role="citizen",
            secret_key=settings.admin_api_key,
            department=None,
            state_scope=None,
            expires_in_seconds=expires,
        )

        return RegisterResponse(
            success=True,
            message=f"Welcome to NagrikSaarathi, {new_user.full_name}! Your citizen account has been created successfully.",
            user=UserResponse.model_validate(new_user),
            access_token=token,
            expires_in=expires,
        )

    # ── Principal Administrator Official Management ─────────────────────────

    def create_official_account(
        self,
        db: Session,
        admin_user: User,
        req: OfficialCreateRequest,
        client_ip: Optional[str] = None,
    ) -> UserResponse:
        """Create a new Department Official account bound to a department and state scope."""
        identifier = req.identifier.strip().lower()
        email = (req.email or identifier).strip().lower()

        # Check existing
        existing = db.execute(
            select(User).where(
                (User.identifier == identifier) | (User.email == email)
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with identifier '{identifier}' or email '{email}' already exists.",
            )

        # Ensure department exists in departments table
        dept_name = req.department.strip()
        dept = db.execute(select(Department).where(Department.name == dept_name)).scalar_one_or_none()
        if not dept:
            dept = Department(
                name=dept_name,
                ministry_name=dept_name if "Ministry" in dept_name else None,
                government_level="state" if req.state_scope else "central",
                state_code=req.state_scope.strip().upper() if req.state_scope else None,
                is_active=True,
            )
            db.add(dept)
            db.flush()

        official_user = User(
            identifier=identifier,
            email=email,
            hashed_password=hash_password(req.password),
            role="official",
            full_name=req.full_name.strip(),
            department=dept_name,
            state_scope=req.state_scope.strip().upper() if req.state_scope else None,
            designation=req.designation.strip() if req.designation else None,
            assigned_by_id=admin_user.id,
            is_active=True,
            is_demo=False,
        )
        db.add(official_user)
        db.commit()
        db.refresh(official_user)

        # Audit log
        audit_log = AdminAuditLog(
            user_id=admin_user.id,
            user_identifier=admin_user.identifier,
            user_role=admin_user.role,
            department=admin_user.department,
            action="CREATE_OFFICIAL_ACCOUNT",
            resource_type="USER",
            resource_id=str(official_user.id),
            details={
                "official_identifier": official_user.identifier,
                "department": official_user.department,
                "state_scope": official_user.state_scope,
                "designation": official_user.designation,
            },
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        return UserResponse.model_validate(official_user)

    def list_official_accounts(
        self,
        db: Session,
        search: Optional[str] = None,
        department: Optional[str] = None,
        state_scope: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[UserResponse]:
        """List all Department Official accounts with filtering."""
        query = select(User).where(User.role == "official").order_by(User.created_at.desc())

        if search:
            s = f"%{search.strip().lower()}%"
            query = query.where(
                (User.identifier.ilike(s))
                | (User.full_name.ilike(s))
                | (User.email.ilike(s))
            )
        if department:
            query = query.where(User.department.ilike(f"%{department.strip()}%"))
        if state_scope:
            query = query.where(User.state_scope == state_scope.strip().upper())
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        officials = db.execute(query).scalars().all()
        return [UserResponse.model_validate(o) for o in officials]

    def update_official_account(
        self,
        db: Session,
        admin_user: User,
        official_id: int,
        req: OfficialUpdateRequest,
        client_ip: Optional[str] = None,
    ) -> UserResponse:
        """Update official details or deactivate account (revocation)."""
        official = db.get(User, official_id)
        if not official or official.role != "official":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department Official account not found.",
            )

        changes = {}
        if req.full_name is not None:
            changes["full_name"] = {"old": official.full_name, "new": req.full_name.strip()}
            official.full_name = req.full_name.strip()
        if req.department is not None:
            changes["department"] = {"old": official.department, "new": req.department.strip()}
            official.department = req.department.strip()
        if req.state_scope is not None:
            new_scope = req.state_scope.strip().upper() if req.state_scope.strip() else None
            changes["state_scope"] = {"old": official.state_scope, "new": new_scope}
            official.state_scope = new_scope
        if req.designation is not None:
            changes["designation"] = {"old": official.designation, "new": req.designation.strip()}
            official.designation = req.designation.strip()
        if req.is_active is not None:
            changes["is_active"] = {"old": official.is_active, "new": req.is_active}
            official.is_active = req.is_active
        if req.password:
            changes["password_reset"] = True
            official.hashed_password = hash_password(req.password)

        db.commit()
        db.refresh(official)

        # Audit log
        audit_log = AdminAuditLog(
            user_id=admin_user.id,
            user_identifier=admin_user.identifier,
            user_role=admin_user.role,
            department=admin_user.department,
            action="UPDATE_OFFICIAL_ACCOUNT" if req.is_active is None or req.is_active else "DEACTIVATE_OFFICIAL_ACCOUNT",
            resource_type="USER",
            resource_id=str(official.id),
            details=changes,
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        return UserResponse.model_validate(official)

    # ── Official Controlled Onboarding & Verification Workflows ──────────────

    def create_invitation(
        self,
        db: Session,
        admin_user: User,
        req: OfficialInvitationCreate,
        client_ip: Optional[str] = None,
    ) -> OfficialInvitationResponse:
        """Issue an administrator-controlled, expiring, single-use invitation for a prospective official."""
        email = req.email.strip().lower()

        # Check if already registered active official
        existing_user = db.execute(
            select(User).where((User.email == email) | (User.identifier == email))
        ).scalar_one_or_none()
        if existing_user and existing_user.role == "official":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An official account for '{email}' already exists. Use the account management tab to edit permissions.",
            )

        # Check existing active/pending invitation
        now = datetime.now(timezone.utc)
        existing_inv = db.execute(
            select(OfficialInvitation).where(
                OfficialInvitation.email == email,
                OfficialInvitation.status.in_(["pending_activation", "pending_approval"]),
                OfficialInvitation.expires_at > now,
            )
        ).scalar_one_or_none()
        if existing_inv:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active pending invitation already exists for '{email}' (Token: {existing_inv.invitation_token[:8]}...). Revoke it before issuing a new one.",
            )

        # Ensure department exists in canonical registry
        dept_name = req.department.strip()
        dept = db.execute(select(Department).where(Department.name == dept_name)).scalar_one_or_none()
        if not dept:
            dept = Department(
                name=dept_name,
                ministry_name=dept_name if "Ministry" in dept_name else None,
                government_level="state" if req.state_scope else "central",
                state_code=req.state_scope.strip().upper() if req.state_scope else None,
                is_active=True,
            )
            db.add(dept)
            db.flush()

        # Generate cryptographically secure single-use token
        raw_token = f"GOV-INV-{secrets.token_urlsafe(28)}"
        expires_at = now + timedelta(days=req.expires_in_days)

        invitation = OfficialInvitation(
            invitation_token=raw_token,
            email=email,
            full_name=req.full_name.strip(),
            department=dept_name,
            state_scope=req.state_scope.strip().upper() if req.state_scope else None,
            designation=req.designation.strip() if req.designation else "Department Official",
            allowed_permissions=req.allowed_permissions,
            invited_by_id=admin_user.id,
            status="pending_activation",
            verification_method=req.verification_method,
            verification_notes=req.verification_notes or "Issued by Principal Administrator under controlled onboarding.",
            approved_by_id=admin_user.id,
            approved_at=now,
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        # Audit log entry
        audit_log = AdminAuditLog(
            user_id=admin_user.id,
            user_identifier=admin_user.identifier,
            user_role=admin_user.role,
            department=admin_user.department,
            action="ISSUE_OFFICIAL_INVITATION",
            resource_type="OFFICIAL_INVITATION",
            resource_id=str(invitation.id),
            details={
                "invitee_email": invitation.email,
                "department": invitation.department,
                "state_scope": invitation.state_scope,
                "expires_at": invitation.expires_at.isoformat(),
                "verification_method": invitation.verification_method,
            },
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        return self._format_invitation_response(invitation)

    def list_invitations(
        self,
        db: Session,
        status_filter: Optional[str] = None,
        department: Optional[str] = None,
    ) -> List[OfficialInvitationResponse]:
        """List all official invitations with dynamic expiration check."""
        now = datetime.now(timezone.utc)
        query = select(OfficialInvitation).order_by(OfficialInvitation.created_at.desc())

        if status_filter and status_filter.lower() != "all":
            query = query.where(OfficialInvitation.status == status_filter.lower())
        if department:
            query = query.where(OfficialInvitation.department.ilike(f"%{department.strip()}%"))

        invitations = db.execute(query).scalars().all()
        results = []
        for inv in invitations:
            # Auto-expire if past expiry date and still pending
            if inv.status in ("pending_activation", "pending_approval") and _is_expired(inv.expires_at, now):
                inv.status = "expired"
                db.commit()
            results.append(self._format_invitation_response(inv))
        return results

    def get_invitation_by_token(
        self,
        db: Session,
        token: str,
    ) -> OfficialInvitationResponse:
        """Retrieve and validate invitation token without disclosing internal sensitive details."""
        clean_token = token.strip()
        invitation = db.execute(
            select(OfficialInvitation).where(OfficialInvitation.invitation_token == clean_token)
        ).scalar_one_or_none()

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation token is invalid or does not exist.",
            )

        now = datetime.now(timezone.utc)
        if _is_expired(invitation.expires_at, now):
            invitation.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This official onboarding invitation has expired. Please contact your Principal Administrator.",
            )

        if invitation.status == "revoked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This official invitation has been revoked by the Principal Administrator.",
            )

        if invitation.status == "activated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation token has already been used and activated. Please log in directly.",
            )

        return self._format_invitation_response(invitation)

    def activate_invitation(
        self,
        db: Session,
        req: OfficialInvitationActivate,
        client_ip: Optional[str] = None,
    ) -> LoginResponse:
        """
        Activate an invited official account upon token validation.
        Creates the verified Department Official account and issues session token.
        """
        clean_token = req.token.strip()
        invitation = db.execute(
            select(OfficialInvitation).where(OfficialInvitation.invitation_token == clean_token)
        ).scalar_one_or_none()

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or non-existent invitation token.",
            )

        now = datetime.now(timezone.utc)
        if _is_expired(invitation.expires_at, now) or invitation.status == "expired":
            invitation.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This official onboarding invitation has expired. Contact your Principal Administrator for a new invitation.",
            )

        if invitation.status == "revoked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This official onboarding invitation has been revoked.",
            )

        if invitation.status == "activated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation token has already been activated. Please sign in with your credentials.",
            )

        # Check existing user
        existing_user = db.execute(
            select(User).where((User.email == invitation.email) | (User.identifier == invitation.email))
        ).scalar_one_or_none()

        if existing_user:
            # Upgrade existing user safely
            existing_user.role = "official"
            existing_user.department = invitation.department
            existing_user.state_scope = invitation.state_scope
            existing_user.designation = invitation.designation or existing_user.designation
            existing_user.hashed_password = hash_password(req.password)
            existing_user.is_active = True
            existing_user.assigned_by_id = invitation.invited_by_id
            official_user = existing_user
        else:
            official_user = User(
                identifier=invitation.email,
                email=invitation.email,
                mobile=req.mobile.strip() if req.mobile else None,
                hashed_password=hash_password(req.password),
                role="official",
                full_name=(req.full_name or invitation.full_name).strip(),
                department=invitation.department,
                state_scope=invitation.state_scope,
                designation=invitation.designation,
                assigned_by_id=invitation.invited_by_id,
                is_active=True,
                is_demo=False,
            )
            db.add(official_user)

        db.flush()

        # Mark invitation as activated
        invitation.status = "activated"
        invitation.activated_at = now
        invitation.user_id = official_user.id
        db.commit()
        db.refresh(official_user)

        # Record audit log
        audit_log = AdminAuditLog(
            user_id=official_user.id,
            user_identifier=official_user.identifier,
            user_role="official",
            department=official_user.department,
            action="ACTIVATE_OFFICIAL_ACCOUNT",
            resource_type="OFFICIAL_INVITATION",
            resource_id=str(invitation.id),
            details={
                "invitation_token": invitation.invitation_token[:10] + "...",
                "department": official_user.department,
                "state_scope": official_user.state_scope,
                "verification_method": invitation.verification_method,
            },
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        # Create session token
        settings = get_settings()
        expires = 86400  # 24 hours
        token = create_access_token(
            user_id=official_user.id,
            identifier=official_user.identifier,
            role="official",
            secret_key=settings.admin_api_key,
            department=official_user.department,
            state_scope=official_user.state_scope,
            expires_in_seconds=expires,
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(official_user),
            expires_in=expires,
        )

    def review_invitation(
        self,
        db: Session,
        admin_user: User,
        invitation_id: int,
        req: OfficialInvitationReview,
        client_ip: Optional[str] = None,
    ) -> OfficialInvitationResponse:
        """Principal Administrator approval or rejection of an official invitation."""
        invitation = db.get(OfficialInvitation, invitation_id)
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        now = datetime.now(timezone.utc)
        if req.approved:
            invitation.approved_by_id = admin_user.id
            invitation.approved_at = now
            if req.assigned_department:
                invitation.department = req.assigned_department.strip()
            if req.assigned_scope is not None:
                invitation.state_scope = req.assigned_scope.strip().upper() if req.assigned_scope.strip() else None
            if req.allowed_permissions:
                invitation.allowed_permissions = req.allowed_permissions
            if req.admin_notes:
                invitation.verification_notes = f"{invitation.verification_notes or ''} | Approved: {req.admin_notes}"
            action = "APPROVE_OFFICIAL_INVITATION"
        else:
            invitation.status = "revoked"
            invitation.verification_notes = f"{invitation.verification_notes or ''} | Rejected: {req.admin_notes or 'Administrative rejection'}"
            action = "REJECT_OFFICIAL_INVITATION"

        db.commit()
        db.refresh(invitation)

        audit_log = AdminAuditLog(
            user_id=admin_user.id,
            user_identifier=admin_user.identifier,
            user_role=admin_user.role,
            department=admin_user.department,
            action=action,
            resource_type="OFFICIAL_INVITATION",
            resource_id=str(invitation.id),
            details={
                "invitee_email": invitation.email,
                "approved": req.approved,
                "notes": req.admin_notes,
            },
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        return self._format_invitation_response(invitation)

    def revoke_invitation(
        self,
        db: Session,
        admin_user: User,
        invitation_id: int,
        reason: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> OfficialInvitationResponse:
        """Revoke an active invitation and immediately suspend associated user account if already activated."""
        invitation = db.get(OfficialInvitation, invitation_id)
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        invitation.status = "revoked"
        if reason:
            invitation.verification_notes = f"{invitation.verification_notes or ''} | Revoked: {reason}"

        # If already activated, suspend the official user immediately
        if invitation.user_id:
            user = db.get(User, invitation.user_id)
            if user:
                user.is_active = False

        db.commit()
        db.refresh(invitation)

        audit_log = AdminAuditLog(
            user_id=admin_user.id,
            user_identifier=admin_user.identifier,
            user_role=admin_user.role,
            department=admin_user.department,
            action="REVOKE_OFFICIAL_INVITATION",
            resource_type="OFFICIAL_INVITATION",
            resource_id=str(invitation.id),
            details={"email": invitation.email, "reason": reason},
            ip_address=client_ip,
        )
        db.add(audit_log)
        db.commit()

        return self._format_invitation_response(invitation)

    @staticmethod
    def _format_invitation_response(inv: OfficialInvitation) -> OfficialInvitationResponse:
        return OfficialInvitationResponse(
            id=inv.id,
            invitation_token=inv.invitation_token,
            email=inv.email,
            full_name=inv.full_name,
            department=inv.department,
            state_scope=inv.state_scope,
            designation=inv.designation,
            allowed_permissions=inv.allowed_permissions or [],
            status=inv.status,
            verification_method=inv.verification_method,
            verification_notes=inv.verification_notes,
            expires_at=inv.expires_at.isoformat() if inv.expires_at else None,
            created_at=inv.created_at.isoformat() if inv.created_at else None,
            approved_at=inv.approved_at.isoformat() if inv.approved_at else None,
            activated_at=inv.activated_at.isoformat() if inv.activated_at else None,
            invited_by_id=inv.invited_by_id,
            user_id=inv.user_id,
        )
