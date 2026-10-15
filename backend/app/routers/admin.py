"""
NagrikSaarathi — Principal Administrator Router

Provides complete administrative governance:
- Multi-stage Scheme Proposal review, approval, rejection, and revision requests
- Public catalogue publication only upon explicit Admin approval
- Department Official account provisioning, state-scope assignment, and revocation
- Immutable administrative audit log inspection
- Nationwide catalogue & workflow metrics
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AdminAuditLog, Department, GovernmentScheme, HelpTicket, SchemeProposal, SchemeRequest, User
from backend.app.schemas.auth import (
    OfficialCreateRequest,
    OfficialInvitationCreate,
    OfficialInvitationResponse,
    OfficialInvitationReview,
    OfficialUpdateRequest,
    UserResponse,
)
from backend.app.schemas.department import (
    AdminAuditLogResponse,
    CitizenDifficultyHeatmapResponse,
    RadarRecordResponse,
    RadarReviewRequest,
    SchemeFieldEvidenceResponse,
    SchemeProposalResponse,
    SchemeProposalReview,
    TranslationDriftAlertResponse,
    TranslationDriftApproveRequest,
    TranslationDriftComparisonResponse,
)
from backend.app.security import (
    audit_log_action,
    require_admin_user,
)
from backend.app.services.auth_service import AuthService
from backend.app.services.radar_service import RadarService

router = APIRouter(prefix="/admin", tags=["Principal Administrator Governance"])
_auth_service = AuthService()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Proposal Review & Publishing ─────────────────────────────────────────────

@router.get("/proposals", response_model=List[SchemeProposalResponse])
def get_all_proposals(
    status: Optional[str] = Query(None, description="Filter: draft, submitted, under_review, revision_required, approved, rejected"),
    department_name: Optional[str] = Query(None, description="Filter by department name"),
    proposal_type: Optional[str] = Query(None, description="Filter by proposal type"),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    List all proposals across all departments for Principal Administrator review.
    """
    query = select(SchemeProposal)

    if status and status.lower() != "all":
        query = query.where(SchemeProposal.status == status.lower())
    if department_name:
        query = query.where(SchemeProposal.department_name.ilike(f"%{department_name.strip()}%"))
    if proposal_type and proposal_type.lower() != "all":
        query = query.where(SchemeProposal.proposal_type == proposal_type.lower())

    return db.execute(query.order_by(SchemeProposal.created_at.desc())).scalars().all()


@router.get("/proposals/{proposal_id}", response_model=SchemeProposalResponse)
def get_proposal_detail(
    proposal_id: int,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """View full details and evidence for a specific scheme proposal."""
    proposal = db.get(SchemeProposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found.")
    return proposal


@router.post("/proposals/{proposal_id}/review", response_model=SchemeProposalResponse)
def review_proposal(
    proposal_id: int,
    req: SchemeProposalReview,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Principal Administrator decision point for a proposal:
    - 'approve': Publishes new scheme or applies updates directly to the official catalogue.
    - 'request_revision': Returns proposal to official with required changes note.
    - 'reject': Formally rejects proposal with stated rationale.
    """
    proposal = db.get(SchemeProposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found.")

    if proposal.status in ("approved", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal has already been {proposal.status}. Decisions cannot be overwritten.",
        )

    now = _utcnow()
    proposal.reviewed_by_id = admin.id
    proposal.reviewed_at = now
    proposal.admin_notes = req.admin_notes

    client_ip = request.client.host if request.client else "unknown"

    if req.action == "approve":
        # 1. Update or Insert GovernmentScheme atomically
        if proposal.proposal_type == "new_scheme":
            slug_base = re.sub(r"[^a-z0-9]+", "-", proposal.scheme_name.lower()).strip("-")
            scheme_slug = f"{slug_base[:80]}-{uuid.uuid4().hex[:6]}"
            canonical_id = f"SCHEME-{uuid.uuid4().hex[:8].upper()}"
            benefit_payload = {"summary": proposal.benefit_summary}
            if proposal.benefit_details:
                benefit_payload.update(proposal.benefit_details)

            new_scheme = GovernmentScheme(
                slug=scheme_slug,
                canonical_id=canonical_id,
                display_name=proposal.scheme_name,
                department_name=proposal.department_name,
                ministry_name=proposal.department_name if "Ministry" in proposal.department_name else None,
                government_level=proposal.government_level,
                state_code=proposal.state_code,
                category=proposal.category or "other",
                description=proposal.description,
                benefit_details=benefit_payload,
                official_source_url=proposal.official_source_url or "",
                official_application_url=proposal.official_application_url,
                source_document_reference=proposal.source_evidence,
                is_active=True,
                is_demo=False,
                created_at=now,
                updated_at=now,
            )
            db.add(new_scheme)
            db.flush()
            proposal.scheme_id = new_scheme.id

        elif proposal.scheme_id:
            target_scheme = db.get(GovernmentScheme, proposal.scheme_id)
            if target_scheme:
                if proposal.scheme_name:
                    target_scheme.display_name = proposal.scheme_name
                if proposal.description:
                    target_scheme.description = proposal.description
                if proposal.category:
                    target_scheme.category = proposal.category
                if proposal.benefit_summary or proposal.benefit_details:
                    b_dict = dict(target_scheme.benefit_details or {})
                    if proposal.benefit_summary:
                        b_dict["summary"] = proposal.benefit_summary
                    if proposal.benefit_details:
                        b_dict.update(proposal.benefit_details)
                    target_scheme.benefit_details = b_dict
                if proposal.official_source_url:
                    target_scheme.official_source_url = proposal.official_source_url
                if proposal.official_application_url:
                    target_scheme.official_application_url = proposal.official_application_url
                if proposal.source_evidence:
                    target_scheme.source_document_reference = proposal.source_evidence
                target_scheme.updated_at = now
                db.flush()

        proposal.status = "approved"
        proposal.published_at = now

        audit_log_action(
            db=db,
            user=admin,
            action="APPROVE_AND_PUBLISH_PROPOSAL",
            resource_type="SCHEME_PROPOSAL",
            resource_id=proposal.proposal_number,
            details={
                "proposal_type": proposal.proposal_type,
                "scheme_id": proposal.scheme_id,
                "scheme_name": proposal.scheme_name,
                "admin_notes": req.admin_notes,
            },
            ip_address=client_ip,
        )

    elif req.action == "request_revision":
        if not req.revision_notes and not req.admin_notes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please specify revision instructions for the Department Official.",
            )
        proposal.status = "revision_required"
        proposal.revision_requested_notes = req.revision_notes or req.admin_notes

        audit_log_action(
            db=db,
            user=admin,
            action="REQUEST_PROPOSAL_REVISION",
            resource_type="SCHEME_PROPOSAL",
            resource_id=proposal.proposal_number,
            details={"revision_notes": proposal.revision_requested_notes},
            ip_address=client_ip,
        )

    elif req.action == "reject":
        if not req.rejection_reason and not req.admin_notes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please provide a valid reason for rejecting this proposal.",
            )
        proposal.status = "rejected"
        proposal.rejection_reason = req.rejection_reason or req.admin_notes

        audit_log_action(
            db=db,
            user=admin,
            action="REJECT_PROPOSAL",
            resource_type="SCHEME_PROPOSAL",
            resource_id=proposal.proposal_number,
            details={"rejection_reason": proposal.rejection_reason},
            ip_address=client_ip,
        )

    db.commit()
    db.refresh(proposal)
    return proposal


# ── Department Official Account Management ──────────────────────────────────

@router.get("/officials", response_model=List[UserResponse])
def list_department_officials(
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    state_scope: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """List all registered Department Officials with department and state scope assignments."""
    return _auth_service.list_official_accounts(
        db=db,
        search=search,
        department=department,
        state_scope=state_scope,
        is_active=is_active,
    )


@router.post("/officials", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_department_official(
    req: OfficialCreateRequest,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Provision a new Department Official account assigned to a specific department and geographic scope.
    """
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.create_official_account(
        db=db,
        admin_user=admin,
        req=req,
        client_ip=client_ip,
    )


@router.patch("/officials/{official_id}", response_model=UserResponse)
def update_department_official(
    official_id: int,
    req: OfficialUpdateRequest,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Update department, state scope, designation, or deactivate (revoke) an official's access.
    Deactivated officials are immediately blocked on their subsequent requests.
    """
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.update_official_account(
        db=db,
        admin_user=admin,
        official_id=official_id,
        req=req,
        client_ip=client_ip,
    )


# ── Controlled Official Onboarding (Invitations & Review) ────────────────────

@router.get("/official-invitations", response_model=List[OfficialInvitationResponse])
def list_official_invitations(
    status: Optional[str] = Query(None, description="Filter: pending_activation, pending_approval, activated, expired, revoked"),
    department: Optional[str] = Query(None, description="Filter by department"),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """List all official onboarding invitations with live expiration enforcement."""
    return _auth_service.list_invitations(db=db, status_filter=status, department=department)


@router.post("/official-invitations", response_model=OfficialInvitationResponse, status_code=status.HTTP_201_CREATED)
def create_official_invitation(
    req: OfficialInvitationCreate,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Issue a new cryptographically secure, single-use, expiring invitation for a prospective official.
    Records intended department, geographic scope, allowed permissions, and verification method.
    """
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.create_invitation(db=db, admin_user=admin, req=req, client_ip=client_ip)


@router.post("/official-invitations/{invitation_id}/review", response_model=OfficialInvitationResponse)
def review_official_invitation(
    invitation_id: int,
    req: OfficialInvitationReview,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Review and approve/reject an official onboarding invitation or activation request.
    """
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.review_invitation(db=db, admin_user=admin, invitation_id=invitation_id, req=req, client_ip=client_ip)


@router.post("/official-invitations/{invitation_id}/revoke", response_model=OfficialInvitationResponse)
def revoke_official_invitation(
    invitation_id: int,
    request: Request,
    reason: Optional[str] = Query(None, description="Administrative rationale for revocation"),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Revoke an invitation token. If the account was already activated, immediately suspends access.
    """
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.revoke_invitation(db=db, admin_user=admin, invitation_id=invitation_id, reason=reason, client_ip=client_ip)


@router.post("/officials/{official_id}/suspend", response_model=UserResponse)
def suspend_official(
    official_id: int,
    request: Request,
    reason: Optional[str] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Immediately suspend/revoke a Department Official's platform access."""
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.update_official_account(
        db=db,
        admin_user=admin,
        official_id=official_id,
        req=OfficialUpdateRequest(is_active=False),
        client_ip=client_ip,
    )


@router.post("/officials/{official_id}/activate", response_model=UserResponse)
def reactivate_official(
    official_id: int,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Reactivate a previously suspended Department Official."""
    client_ip = request.client.host if request.client else "unknown"
    return _auth_service.update_official_account(
        db=db,
        admin_user=admin,
        official_id=official_id,
        req=OfficialUpdateRequest(is_active=True),
        client_ip=client_ip,
    )


@router.get("/audit-logs", response_model=List[AdminAuditLogResponse])
def get_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Inspect immutable administrative audit logs for full compliance and accountability.
    """
    query = select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc())

    if action:
        query = query.where(AdminAuditLog.action.ilike(f"%{action.strip()}%"))
    if resource_type:
        query = query.where(AdminAuditLog.resource_type == resource_type.strip().upper())
    if department:
        query = query.where(AdminAuditLog.department.ilike(f"%{department.strip()}%"))

    logs = db.execute(query.limit(limit).offset(offset)).scalars().all()
    return logs


@router.get("/stats")
def get_admin_governance_stats(
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    High-level platform governance and oversight metrics.
    """
    total_schemes = db.execute(select(func.count(GovernmentScheme.id))).scalar() or 0
    total_departments = db.execute(select(func.count(Department.id))).scalar() or 0
    total_officials = db.execute(select(func.count(User.id)).where(User.role == "official")).scalar() or 0
    active_officials = db.execute(
        select(func.count(User.id)).where(User.role == "official", User.is_active == True)
    ).scalar() or 0

    prop_counts = dict(
        db.execute(
            select(SchemeProposal.status, func.count(SchemeProposal.id)).group_by(SchemeProposal.status)
        ).all()
    )

    pending_proposals = prop_counts.get("submitted", 0) + prop_counts.get("under_review", 0)
    revision_proposals = prop_counts.get("revision_required", 0)
    approved_proposals = prop_counts.get("approved", 0)
    rejected_proposals = prop_counts.get("rejected", 0)

    total_citizen_requests = db.execute(select(func.count(SchemeRequest.id))).scalar() or 0
    total_help_tickets = db.execute(select(func.count(HelpTicket.id))).scalar() or 0

    return {
        "total_schemes": total_schemes,
        "total_departments": total_departments,
        "total_officials": total_officials,
        "active_officials": active_officials,
        "pending_proposals": pending_proposals,
        "revision_proposals": revision_proposals,
        "approved_proposals": approved_proposals,
        "rejected_proposals": rejected_proposals,
        "total_citizen_requests": total_citizen_requests,
        "total_help_tickets": total_help_tickets,
    }


# ── PRIORITY 2: Scheme Rule Change Radar Review & Publishing Queue ───────────

@router.get("/radar", response_model=List[RadarRecordResponse])
def get_all_radar_records(
    department_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """List Scheme Rule Change Radar change records across all departments for review."""
    return RadarService.list_radar_records(db=db, department_name=department_name, status_filter=status)


@router.get("/radar/{radar_id}", response_model=RadarRecordResponse)
def get_radar_record_detail(
    radar_id: int,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """View full candidate diff, citations, and uncertain flags for a radar change record."""
    records = RadarService.list_radar_records(db=db, status_filter=None)
    for r in records:
        if r.id == radar_id:
            return r
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Radar record not found.")


@router.post("/radar/{radar_id}/review", response_model=RadarRecordResponse)
def review_radar_record(
    radar_id: int,
    req: RadarReviewRequest,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Principal Administrator decision point for Scheme Rule Change Radar:
    - 'approve': Publishes changes to GovernmentScheme, saves revision snapshot, and triggers Translation Drift Monitor.
    - 'request_revision': Returns change set to official with required corrections.
    - 'reject': Formally rejects change set.
    """
    client_ip = request.client.host if request.client else "unknown"
    return RadarService.review_radar_record(db=db, admin_user=admin, radar_id=radar_id, req=req, client_ip=client_ip)


# ── PRIORITY 3: Nationwide Citizen Difficulty Heatmap ────────────────────────

@router.get("/heatmap", response_model=CitizenDifficultyHeatmapResponse)
def get_admin_difficulty_heatmap(
    department_name: Optional[str] = Query(None),
    scheme_id: Optional[int] = Query(None),
    form_step: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Nationwide privacy-preserving citizen difficulty heatmap across departments and schemes.
    Enforces privacy threshold (< 3 sessions returns 'Not enough data yet').
    """
    return RadarService.get_difficulty_heatmap(
        db=db,
        department_name=department_name,
        scheme_id=scheme_id,
        form_step=form_step,
        language=language,
        start_date=start_date,
        end_date=end_date,
    )


# ── PRIORITY 4: Evidence & Official Link Verification Queue ──────────────────

@router.get("/evidence", response_model=List[SchemeFieldEvidenceResponse])
def get_all_field_evidence(
    department_name: Optional[str] = Query(None),
    scheme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Master evidence verification queue across all schemes and departments."""
    return RadarService.get_evidence_records(
        db=db,
        department_name=department_name,
        scheme_id=scheme_id,
        status_filter=status,
    )


@router.post("/evidence/{evidence_id}/verify", response_model=SchemeFieldEvidenceResponse)
def verify_field_evidence(
    evidence_id: int,
    request: Request,
    approved: bool = Query(True),
    notes: Optional[str] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Principal Administrator verification decision for factual field quotation."""
    client_ip = request.client.host if request.client else "unknown"
    return RadarService.verify_field_evidence(
        db=db,
        admin_user=admin,
        evidence_id=evidence_id,
        approved=approved,
        notes=notes,
        client_ip=client_ip,
    )


# ── PRIORITY 5: Translation Drift Monitor Master Queue ───────────────────────

@router.get("/translation-drift", response_model=List[TranslationDriftAlertResponse])
def get_all_translation_drift_alerts(
    department_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Master queue of active translation drift alerts across the 22 scheduled languages."""
    return RadarService.list_drift_alerts(db=db, department_name=department_name, status_filter=status)


@router.get("/translation-drift/{alert_id}/compare", response_model=TranslationDriftComparisonResponse)
def get_translation_drift_comparison(
    alert_id: int,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Side-by-side comparison of source text change and candidate translation."""
    return RadarService.get_drift_comparison(db=db, alert_id=alert_id)


@router.post("/translation-drift/{alert_id}/review", response_model=TranslationDriftAlertResponse)
def review_translation_drift_alert(
    alert_id: int,
    req: TranslationDriftApproveRequest,
    request: Request,
    admin: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Approve verified human translation or candidate translation to resolve drift."""
    client_ip = request.client.host if request.client else "unknown"
    return RadarService.review_drift_alert(db=db, reviewer_user=admin, alert_id=alert_id, req=req, client_ip=client_ip)

