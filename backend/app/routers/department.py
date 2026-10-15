"""
NagrikSaarathi — Department Official Router

Provides backend-enforced, department-scoped workflows for Department Officials:
- View assigned government schemes
- View real database aggregated statistics
- Submit and track multi-stage scheme proposals (new scheme, metadata update, URL correction)
- Respond to revision requests from Principal Administrator
- Strict department & state jurisdiction scope enforcement
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Department, GovernmentScheme, SchemeProposal, User
from backend.app.schemas.department import (
    CitizenDifficultyHeatmapResponse,
    DepartmentResponse,
    DepartmentStatsResponse,
    RadarAnalyzeRequest,
    RadarAnalyzeResponse,
    RadarRecordResponse,
    RadarSubmitRequest,
    SchemeEvidenceHealthSummary,
    SchemeFieldEvidenceCreate,
    SchemeFieldEvidenceResponse,
    SchemeProposalCreate,
    SchemeProposalResponse,
    SchemeProposalUpdate,
    TranslationDriftAlertResponse,
)
from backend.app.security import (
    audit_log_action,
    require_official_user,
    verify_official_scope,
)
from backend.app.services.radar_service import RadarService

router = APIRouter(prefix="/department", tags=["Department Official Operations"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@router.get("/list", response_model=List[DepartmentResponse])
def list_departments(
    government_level: Optional[str] = Query(None, description="Filter by central/state/ut"),
    db: Session = Depends(get_db),
):
    """Public/Authenticated endpoint listing canonical departments for proposal dropdowns."""
    query = select(Department).where(Department.is_active == True).order_by(Department.name.asc())
    if government_level:
        query = query.where(Department.government_level == government_level.lower())
    return db.execute(query).scalars().all()


@router.get("/my-schemes")
def get_my_department_schemes(
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Fetch government schemes strictly scoped to the authenticated Department Official's department
    and optional state jurisdiction.
    """
    dept_name = user.department.strip()
    query = select(GovernmentScheme).where(
        GovernmentScheme.department_name.ilike(f"%{dept_name}%")
        | (GovernmentScheme.ministry_name.ilike(f"%{dept_name}%"))
    )

    if user.state_scope:
        query = query.where(
            (GovernmentScheme.state_code == user.state_scope.upper())
            | (GovernmentScheme.government_level == "central")
        )

    schemes = db.execute(query.order_by(GovernmentScheme.display_name.asc())).scalars().all()

    return [
        {
            "id": s.id,
            "scheme_code": s.slug,
            "slug": s.slug,
            "scheme_name": s.display_name,
            "display_name": s.display_name,
            "department_name": s.department_name,
            "ministry_name": s.ministry_name,
            "government_level": s.government_level,
            "state_code": s.state_code,
            "category": s.category,
            "description": s.description,
            "official_source_url": s.official_source_url,
            "official_application_url": s.official_application_url,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in schemes
    ]


@router.get("/stats", response_model=DepartmentStatsResponse)
def get_department_statistics(
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Return real database metrics scoped to the official's assigned department.
    """
    dept_name = user.department.strip()

    # Total schemes in department
    scheme_query = select(func.count(GovernmentScheme.id)).where(
        GovernmentScheme.department_name.ilike(f"%{dept_name}%")
        | (GovernmentScheme.ministry_name.ilike(f"%{dept_name}%"))
    )
    if user.state_scope:
        scheme_query = scheme_query.where(
            (GovernmentScheme.state_code == user.state_scope.upper())
            | (GovernmentScheme.government_level == "central")
        )
    total_schemes = db.execute(scheme_query).scalar() or 0

    # Published active schemes
    pub_query = scheme_query.where(GovernmentScheme.is_active == True)
    published_schemes = db.execute(pub_query).scalar() or 0

    # Unverified / missing portal links
    unverified_query = scheme_query.where(
        (GovernmentScheme.official_application_url.is_(None))
        | (GovernmentScheme.official_application_url == "")
    )
    unverified_links_count = db.execute(unverified_query).scalar() or 0

    # Proposals metrics by status
    base_prop = select(SchemeProposal.status, func.count(SchemeProposal.id)).where(
        SchemeProposal.department_name.ilike(f"%{dept_name}%")
    ).group_by(SchemeProposal.status)

    if user.state_scope:
        base_prop = base_prop.where(
            (SchemeProposal.state_code == user.state_scope.upper())
            | (SchemeProposal.government_level == "central")
        )

    status_counts = dict(db.execute(base_prop).all())

    draft_proposals = status_counts.get("draft", 0)
    pending_proposals = status_counts.get("submitted", 0) + status_counts.get("under_review", 0)
    revision_required_proposals = status_counts.get("revision_required", 0)
    approved_proposals = status_counts.get("approved", 0)
    rejected_proposals = status_counts.get("rejected", 0)

    return DepartmentStatsResponse(
        department_name=user.department,
        state_scope=user.state_scope,
        total_schemes=total_schemes,
        published_schemes=published_schemes,
        draft_proposals=draft_proposals,
        pending_proposals=pending_proposals,
        revision_required_proposals=revision_required_proposals,
        approved_proposals=approved_proposals,
        rejected_proposals=rejected_proposals,
        unverified_links_count=unverified_links_count,
    )


@router.get("/proposals", response_model=List[SchemeProposalResponse])
def get_department_proposals(
    status: Optional[str] = Query(None, description="Filter by status: draft, submitted, under_review, revision_required, approved, rejected"),
    proposal_type: Optional[str] = Query(None, description="Filter by type: new_scheme, metadata_update, url_correction, eligibility_update"),
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    List all proposals submitted by or belonging to the official's assigned department.
    """
    dept_name = user.department.strip()
    query = select(SchemeProposal).where(
        SchemeProposal.department_name.ilike(f"%{dept_name}%")
    )

    if user.state_scope:
        query = query.where(
            (SchemeProposal.state_code == user.state_scope.upper())
            | (SchemeProposal.government_level == "central")
        )

    if status and status.lower() != "all":
        query = query.where(SchemeProposal.status == status.lower())
    if proposal_type and proposal_type.lower() != "all":
        query = query.where(SchemeProposal.proposal_type == proposal_type.lower())

    proposals = db.execute(query.order_by(SchemeProposal.created_at.desc())).scalars().all()
    return proposals


@router.post("/proposals", response_model=SchemeProposalResponse, status_code=status.HTTP_201_CREATED)
def create_scheme_proposal(
    req: SchemeProposalCreate,
    request: Request,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Submit a new scheme proposal or correction.
    Strictly verifies that the official has jurisdiction over the specified department and state.
    """
    dept_name = req.department_name or user.department
    verify_official_scope(user, dept_name, req.state_code)

    # If updating an existing scheme, ensure the target scheme exists and belongs to department
    if req.scheme_id:
        target_scheme = db.get(GovernmentScheme, req.scheme_id)
        if not target_scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target scheme ID {req.scheme_id} does not exist in the catalogue.",
            )
        verify_official_scope(user, target_scheme.department_name or user.department, target_scheme.state_code)

    # Generate unique proposal number: PRP-YYYYMMDD-XXXX
    date_str = _utcnow().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6].upper()
    proposal_number = f"PRP-{date_str}-{short_uuid}"

    proposal = SchemeProposal(
        proposal_number=proposal_number,
        proposal_type=req.proposal_type,
        scheme_id=req.scheme_id,
        official_id=user.id,
        department_name=user.department,
        state_code=req.state_code.strip().upper() if req.state_code else user.state_scope,
        government_level=req.government_level,
        scheme_name=req.scheme_name.strip(),
        description=req.description.strip(),
        category=req.category,
        benefit_summary=req.benefit_summary,
        benefit_details=req.benefit_details or {},
        eligibility_criteria=req.eligibility_criteria or [],
        document_requirements=req.document_requirements or [],
        application_instructions=req.application_instructions,
        official_source_url=req.official_source_url,
        official_application_url=req.official_application_url,
        source_evidence=req.source_evidence.strip(),
        status="submitted",
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    # Immutable audit logging
    client_ip = request.client.host if request.client else "unknown"
    audit_log_action(
        db=db,
        user=user,
        action="SUBMIT_PROPOSAL",
        resource_type="SCHEME_PROPOSAL",
        resource_id=proposal.proposal_number,
        details={
            "proposal_type": proposal.proposal_type,
            "scheme_name": proposal.scheme_name,
            "department": proposal.department_name,
            "source_evidence": proposal.source_evidence,
        },
        ip_address=client_ip,
    )

    return proposal


@router.get("/proposals/{proposal_id}", response_model=SchemeProposalResponse)
def get_scheme_proposal_detail(
    proposal_id: int,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """View details of a specific proposal within official jurisdiction."""
    proposal = db.get(SchemeProposal, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )
    verify_official_scope(user, proposal.department_name, proposal.state_code)
    return proposal


@router.patch("/proposals/{proposal_id}", response_model=SchemeProposalResponse)
def update_scheme_proposal(
    proposal_id: int,
    req: SchemeProposalUpdate,
    request: Request,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Update a draft proposal or respond to a revision request from Principal Administrator.
    Once resubmitted, status changes back to 'submitted' for Administrator review.
    """
    proposal = db.get(SchemeProposal, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )

    verify_official_scope(user, proposal.department_name, proposal.state_code)

    if proposal.status in ("approved", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit proposal in '{proposal.status}' state. Only draft or revision_required proposals can be modified.",
        )

    # Apply updates
    if req.scheme_name is not None:
        proposal.scheme_name = req.scheme_name.strip()
    if req.category is not None:
        proposal.category = req.category
    if req.description is not None:
        proposal.description = req.description.strip()
    if req.benefit_summary is not None:
        proposal.benefit_summary = req.benefit_summary
    if req.benefit_details is not None:
        proposal.benefit_details = req.benefit_details
    if req.eligibility_criteria is not None:
        proposal.eligibility_criteria = req.eligibility_criteria
    if req.document_requirements is not None:
        proposal.document_requirements = req.document_requirements
    if req.application_instructions is not None:
        proposal.application_instructions = req.application_instructions
    if req.official_source_url is not None:
        proposal.official_source_url = req.official_source_url
    if req.official_application_url is not None:
        proposal.official_application_url = req.official_application_url
    if req.source_evidence is not None:
        proposal.source_evidence = req.source_evidence.strip()

    # If responding to revision request or explicit submit
    was_revision = proposal.status == "revision_required"
    if req.submit_now or was_revision:
        proposal.status = "submitted"

    proposal.updated_at = _utcnow()
    db.commit()
    db.refresh(proposal)

    client_ip = request.client.host if request.client else "unknown"
    audit_log_action(
        db=db,
        user=user,
        action="RESUBMIT_REVISION" if was_revision else "UPDATE_PROPOSAL",
        resource_type="SCHEME_PROPOSAL",
        resource_id=proposal.proposal_number,
        details={"status": proposal.status, "updated_fields": list(req.model_dump(exclude_unset=True).keys())},
        ip_address=client_ip,
    )

    return proposal


# ── PRIORITY 2: Scheme Rule Change Radar Endpoints ───────────────────────────

@router.post("/radar/analyze", response_model=RadarAnalyzeResponse)
def analyze_scheme_rule_changes(
    req: RadarAnalyzeRequest,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Extract candidate scheme changes from an official source document/order,
    compare with the currently published scheme record, and highlight structured diffs.
    """
    scheme = db.get(GovernmentScheme, req.scheme_id)
    if not scheme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    verify_official_scope(user, scheme.department_name or user.department, scheme.state_code)

    return RadarService.analyze_source_document(db=db, user=user, req=req)


@router.post("/radar/submit", response_model=RadarRecordResponse, status_code=status.HTTP_201_CREATED)
def submit_scheme_rule_change_set(
    req: RadarSubmitRequest,
    request: Request,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Submit a candidate scheme change set with diffs, citations, and evidence for review.
    Does NOT overwrite published record until Principal Administrator approves.
    """
    scheme = db.get(GovernmentScheme, req.scheme_id)
    if not scheme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    verify_official_scope(user, scheme.department_name or user.department, scheme.state_code)

    client_ip = request.client.host if request.client else "unknown"
    return RadarService.submit_change_record(db=db, user=user, req=req, client_ip=client_ip)


@router.get("/radar", response_model=List[RadarRecordResponse])
def get_department_radar_records(
    status: Optional[str] = Query(None, description="Filter: draft, submitted, under_review, revision_required, approved, published, rejected"),
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """List Scheme Rule Change Radar change records scoped to official's department."""
    return RadarService.list_radar_records(db=db, department_name=user.department, status_filter=status)


# ── PRIORITY 3: Citizen Difficulty Heatmap Endpoints ─────────────────────────

@router.get("/heatmap", response_model=CitizenDifficultyHeatmapResponse)
def get_department_difficulty_heatmap(
    scheme_id: Optional[int] = Query(None, description="Optional scheme filter"),
    form_step: Optional[str] = Query(None, description="Optional step filter"),
    language: Optional[str] = Query(None, description="Optional language filter"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """
    Aggregate privacy-preserving citizen difficulty metrics for guided forms within official's scope.
    Enforces privacy threshold (< 3 sessions returns 'Not enough data yet').
    """
    if scheme_id:
        target = db.get(GovernmentScheme, scheme_id)
        if target:
            verify_official_scope(user, target.department_name or user.department, target.state_code)

    return RadarService.get_difficulty_heatmap(
        db=db,
        department_name=user.department,
        scheme_id=scheme_id,
        form_step=form_step,
        language=language,
        start_date=start_date,
        end_date=end_date,
    )


# ── PRIORITY 4: Evidence-Linked Scheme Editor Endpoints ───────────────────────

@router.get("/evidence", response_model=List[SchemeFieldEvidenceResponse])
def get_department_evidence(
    scheme_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """List evidence records for department schemes with verification health indicators."""
    return RadarService.get_evidence_records(
        db=db,
        department_name=user.department,
        scheme_id=scheme_id,
        status_filter=status,
    )


@router.post("/evidence", response_model=SchemeFieldEvidenceResponse, status_code=status.HTTP_201_CREATED)
def submit_department_field_evidence(
    req: SchemeFieldEvidenceCreate,
    request: Request,
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """Submit traceable official evidence quotation for a factual scheme field."""
    scheme = db.get(GovernmentScheme, req.scheme_id)
    if not scheme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found.")
    verify_official_scope(user, scheme.department_name or user.department, scheme.state_code)

    client_ip = request.client.host if request.client else "unknown"
    return RadarService.submit_field_evidence(db=db, user=user, req=req, client_ip=client_ip)


@router.get("/evidence/summary", response_model=SchemeEvidenceHealthSummary)
def get_department_evidence_health(
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """Return health breakdown of department scheme evidence (broken URLs, unverified, outdated)."""
    return RadarService.get_evidence_health_summary(db=db, department_name=user.department)


# ── PRIORITY 5: Translation Drift Monitor Endpoints ──────────────────────────

@router.get("/translation-drift", response_model=List[TranslationDriftAlertResponse])
def get_department_translation_drift(
    status: Optional[str] = Query(None, description="Filter: drift_detected, in_review, verified_human, approved, dismissed"),
    user: User = Depends(require_official_user),
    db: Session = Depends(get_db),
):
    """List translation drift alerts triggered by rule changes for department schemes."""
    return RadarService.list_drift_alerts(db=db, department_name=user.department, status_filter=status)

