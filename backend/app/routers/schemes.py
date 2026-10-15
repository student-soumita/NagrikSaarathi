"""
Government Schemes router for NagrikSaarathi API.

Provides metadata on available government schemes, their form fields,
eligibility requirements, document checklists, and application steps.
Clearly labels fictional/demo schemes with is_demo=True and official disclaimer.
"""

from __future__ import annotations

from typing import List, Optional, Union
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import (
    FormField,
    GovernmentScheme,
    SchemeApplicationStep,
    SchemeDocumentRequirement,
    SchemeEligibilityRequirement,
    SchemeRequest,
    User,
    SCHEDULED_LANGUAGES_22,
)
from backend.app.schemas.scheme_request import (
    SchemeRequestCreate,
    SchemeRequestResponse,
)
from backend.app.services.auth_service import decode_access_token
import secrets
from backend.app.schemas.scheme import (
    BenefitCombinationMatch,
    BenefitCombinationRequest,
    BenefitCombinationResponse,
    CandidateSchemeCreate,
    FormExtractionCandidateResponse,
    FormExtractionRequest,
    FormFieldResponse,
    GovernmentSchemeDetail,
    GovernmentSchemeSummary,
    IngestionResultResponse,
    PaginatedSchemesResponse,
    SchemeApplicationStepResponse,
    SchemeCoverageAuditItem,
    SchemeCoverageAuditResponse,
    SchemeDocumentRequirementResponse,
    SchemeEligibilityRequirementResponse,
    SchemeGuidancePacket,
    SchemeIngestionItem,
)
import re
import uuid
from datetime import datetime, timezone

from backend.app.services.scheme_ingestion_service import SchemeIngestionService
from backend.app.services.multilingual_scheme_service import multilingual_scheme_service

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=Union[PaginatedSchemesResponse, List[GovernmentSchemeSummary]])
def list_schemes(
    search: Optional[str] = Query(None, description="Search query across name, alternate names, ministry, keywords"),
    level: Optional[str] = Query(None, description="Filter by level: central, state, ut, local"),
    state: Optional[str] = Query(None, description="Filter by state code, e.g. MH, DL"),
    category: Optional[str] = Query(None, description="Filter by scheme category"),
    capability: Optional[str] = Query(None, description="Filter by portal capability"),
    form_status: Optional[str] = Query(None, description="Filter by form availability"),
    active_only: bool = True,
    include_candidates: bool = False,
    page: Optional[int] = Query(None, ge=1, description="Page number. When supplied, returns paginated envelope."),
    page_size: int = Query(12, ge=1, le=100, description="Items per page for pagination"),
    sort_by: str = Query("id", description="Field to sort by: id, name, level"),
    db: Session = Depends(get_db),
):
    """
    List registered government schemes with universal search, pagination, and multi-jurisdiction filtering.
    When 'page' query param is omitted, returns a flat List for full backward compatibility.
    """
    query = select(GovernmentScheme)
    if active_only:
        query = query.where(GovernmentScheme.is_active == True)  # noqa: E712
    if not include_candidates:
        query = query.where(GovernmentScheme.is_candidate == False)  # noqa: E712

    if level:
        query = query.where(GovernmentScheme.government_level == level.lower())
    if state:
        query = query.where(GovernmentScheme.state_code == state.upper())
    if category:
        query = query.where(GovernmentScheme.category == category.lower())
    if capability:
        query = query.where(GovernmentScheme.portal_capability == capability.upper())
    if form_status:
        query = query.where(GovernmentScheme.form_status == form_status.upper())

    if search:
        search_term = f"%{search.strip().lower()}%"
        query = query.where(
            or_(
                GovernmentScheme.display_name.ilike(search_term),
                GovernmentScheme.department_name.ilike(search_term),
                GovernmentScheme.ministry_name.ilike(search_term),
                GovernmentScheme.description.ilike(search_term),
                GovernmentScheme.slug.ilike(search_term),
                GovernmentScheme.canonical_id.ilike(search_term),
            )
        )

    # Sorting
    if sort_by == "name":
        query = query.order_by(GovernmentScheme.display_name.asc())
    elif sort_by == "level":
        query = query.order_by(GovernmentScheme.government_level.asc(), GovernmentScheme.id.asc())
    else:
        query = query.order_by(GovernmentScheme.id.asc())

    # Pagination handling
    if page is not None:
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        paginated_query = query.offset((page - 1) * page_size).limit(page_size)
        items = db.execute(paginated_query).scalars().all()
        total_pages = max(1, (total + page_size - 1) // page_size)

        return PaginatedSchemesResponse(
            items=[GovernmentSchemeSummary.model_validate(s) for s in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    # Backward-compatible unpaginated list
    schemes = db.execute(query).scalars().all()
    return [GovernmentSchemeSummary.model_validate(s) for s in schemes]


@router.post("/candidate", response_model=GovernmentSchemeSummary, status_code=status.HTTP_201_CREATED)
def submit_candidate_scheme(
    payload: CandidateSchemeCreate,
    db: Session = Depends(get_db),
):
    """
    Allow citizens to submit an unlisted scheme URL/name for verification and assistance.
    Creates a candidate scheme marked with verification_status='pending_review' and is_candidate=True.
    """
    slug_base = re.sub(r"[^a-z0-9]+", "-", payload.display_name.lower()).strip("-")
    short_uuid = str(uuid.uuid4())[:8]
    slug = f"cand-{short_uuid}-{slug_base}"[:100]

    from backend.app.services.url_authority_service import UrlAuthorityService

    state_code = payload.state_code.upper() if payload.state_code else None
    resolved = UrlAuthorityService.resolve_scheme_urls(
        official_source_url=payload.official_source_url,
        official_application_url=None,
        state_code=state_code,
        application_method="online",
    )

    scheme = GovernmentScheme(
        canonical_id=f"CAND-{short_uuid.upper()}",
        slug=slug,
        display_name=payload.display_name.strip(),
        description=payload.description or "Citizen-submitted scheme awaiting verification.",
        department_name=payload.department_name or "Department to be verified",
        official_source_url=resolved["official_source_url"],
        official_application_url=resolved["official_application_url"],
        government_level=payload.government_level or ("state" if state_code else "central"),
        state_code=state_code,
        category=payload.category or "other",
        portal_capability="DISCOVERY_ONLY",
        form_status="NO_FORM",
        source_feed_type="CITIZEN_SUBMISSION",
        verification_status="pending_review",
        verification_source_reference=payload.user_notes or "Submitted by citizen via NagrikSaarathi candidate portal",
        is_candidate=True,
        is_active=True,
    )
    db.add(scheme)

    # Also automatically record a trackable SchemeRequest for transparency
    tracking_req = SchemeRequest(
        tracking_id=f"REQ-{datetime.now(timezone.utc).year}-{short_uuid[:6].upper()}",
        scheme_name=payload.display_name.strip(),
        government_level=scheme.government_level,
        state_code=state_code,
        department_name=scheme.department_name,
        description=payload.description,
        official_portal_url=resolved["official_source_url"],
        status="Under Review",
        admin_notes="Candidate submission registered and pending review.",
        linked_scheme_id=scheme.id,
    )
    db.add(tracking_req)

    db.commit()
    db.refresh(scheme)
    return GovernmentSchemeSummary.model_validate(scheme)


def _try_get_user(
    authorization: Optional[str] = Header(None),
    nagrik_session: Optional[str] = Cookie(None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> Optional[User]:
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


def _format_scheme_request_response(req: SchemeRequest, db: Session) -> SchemeRequestResponse:
    resp = SchemeRequestResponse.model_validate(req)
    if req.linked_scheme_id:
        linked = db.get(GovernmentScheme, req.linked_scheme_id)
        if linked:
            resp.linked_scheme_slug = linked.slug
            resp.linked_scheme_name = linked.display_name
    return resp


@router.post("/requests", response_model=SchemeRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_scheme_request(
    payload: SchemeRequestCreate,
    user: Optional[User] = Depends(_try_get_user),
    db: Session = Depends(get_db),
):
    """
    Allow citizens to submit missing schemes and receive an explicit unique tracking ID.
    Pre-checks if the scheme is already present in the catalogue.
    """
    year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    tracking_id = f"REQ-{year}-{suffix}"

    # Check for existing matching scheme by name (case-insensitive)
    existing_scheme = db.execute(
        select(GovernmentScheme).where(
            func.lower(GovernmentScheme.display_name) == payload.scheme_name.strip().lower(),
            GovernmentScheme.is_active == True,  # noqa: E712
            GovernmentScheme.is_candidate == False,  # noqa: E712
        )
    ).scalars().first()

    status_val = "Already Exists" if existing_scheme else "Request Received"
    notes = "This scheme already exists in the NagrikSaarathi catalogue." if existing_scheme else None

    req = SchemeRequest(
        tracking_id=tracking_id,
        user_id=user.id if user else None,
        citizen_contact=payload.citizen_contact.strip() if payload.citizen_contact else (user.email or user.mobile if user else None),
        scheme_name=payload.scheme_name.strip(),
        government_level=payload.government_level,
        state_code=payload.state_code.upper() if payload.state_code else None,
        department_name=payload.department_name.strip() if payload.department_name else None,
        description=payload.description.strip() if payload.description else None,
        official_portal_url=payload.official_portal_url.strip() if payload.official_portal_url else None,
        status=status_val,
        admin_notes=notes,
        linked_scheme_id=existing_scheme.id if existing_scheme else None,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return _format_scheme_request_response(req, db)


@router.get("/requests/track/{tracking_id}", response_model=SchemeRequestResponse)
def track_scheme_request(
    tracking_id: str,
    db: Session = Depends(get_db),
):
    """
    Track status, reviews, and catalogue links of a submitted scheme request.
    """
    req = db.execute(
        select(SchemeRequest).where(SchemeRequest.tracking_id == tracking_id.strip().upper())
    ).scalar_one_or_none()

    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme request '{tracking_id}' not found.",
        )
    return _format_scheme_request_response(req, db)


@router.get("/requests/my", response_model=List[SchemeRequestResponse])
def get_my_scheme_requests(
    contact: Optional[str] = Query(None, description="Citizen email or phone for guest tracking"),
    user: Optional[User] = Depends(_try_get_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve scheme requests submitted by current authenticated user, or by contact for visitors.
    """
    if user:
        requests = db.execute(
            select(SchemeRequest)
            .where((SchemeRequest.user_id == user.id) | (SchemeRequest.citizen_contact == user.identifier))
            .order_by(desc(SchemeRequest.created_at))
        ).scalars().all()
    elif contact:
        requests = db.execute(
            select(SchemeRequest)
            .where(SchemeRequest.citizen_contact == contact.strip())
            .order_by(desc(SchemeRequest.created_at))
        ).scalars().all()
    else:
        return []

    return [_format_scheme_request_response(r, db) for r in requests]


@router.post("/extract-form", response_model=FormExtractionCandidateResponse, status_code=status.HTTP_201_CREATED)
def extract_form_schema(
    payload: FormExtractionRequest,
    db: Session = Depends(get_db),
):
    """
    Extract form fields and create a draft schema for uncatalogued schemes from uploaded form text or notice.
    Creates an unverified candidate scheme with form_status='EXTRACTED_DRAFT' so the existing
    universal form engine can immediately render it without manual coding.
    """
    from backend.app.services.url_authority_service import UrlAuthorityService

    slug_base = re.sub(r"[^a-z0-9]+", "-", payload.scheme_name.lower()).strip("-")
    short_uuid = str(uuid.uuid4())[:8]
    slug = f"extracted-{short_uuid}-{slug_base}"[:100]

    state_code = payload.state_code.upper() if payload.state_code else None
    resolved = UrlAuthorityService.resolve_scheme_urls(
        official_source_url=payload.official_url,
        official_application_url=None,
        state_code=state_code,
        application_method="online",
    )

    # Create candidate scheme
    scheme = GovernmentScheme(
        canonical_id=f"EXTRACT-{short_uuid.upper()}",
        slug=slug,
        display_name=payload.scheme_name.strip(),
        description="Draft form schema extracted from citizen-uploaded document / notice.",
        department_name="Department under review",
        official_source_url=resolved["official_source_url"],
        official_application_url=resolved["official_application_url"],
        state_code=state_code,
        government_level="state" if state_code else "central",
        category=payload.category or "other",
        portal_capability="GUIDED_PREPARATION",
        form_status="EXTRACTED_DRAFT",
        source_feed_type="CITIZEN_SUBMISSION",
        verification_status="pending_review",
        verification_source_reference=payload.user_notes or "Machine-extracted draft schema from uploaded form text",
        extracted_form_raw=payload.form_text_or_url[:4000],
        is_candidate=True,
        is_active=True,
    )
    db.add(scheme)
    db.flush()

    # Extract fields using universal extractor
    extracted_field_defs = SchemeIngestionService.extract_form_fields_from_text(payload.form_text_or_url)
    created_fields: List[FormField] = []

    for f_def in extracted_field_defs:
        field = FormField(
            scheme_id=scheme.id,
            field_key=f_def["field_key"],
            field_type=f_def["field_type"],
            required=f_def.get("required", True),
            sort_order=f_def["sort_order"],
            labels_by_language=f_def.get("labels_by_language", {}),
            explanations_by_language=f_def.get("explanations_by_language", {}),
            instructions_by_language=f_def.get("instructions_by_language", {}),
            verification_status="pending_review",
            last_verified_at=datetime.now(timezone.utc),
        )
        db.add(field)
        created_fields.append(field)

    db.commit()
    db.refresh(scheme)

    confidence = min(0.95, 0.50 + (len(created_fields) * 0.05))
    summary = f"Extracted {len(created_fields)} candidate form fields. Marked as pending_review."

    return FormExtractionCandidateResponse(
        scheme=GovernmentSchemeSummary.model_validate(scheme),
        extracted_fields=[FormFieldResponse.model_validate(f) for f in created_fields],
        confidence_score=confidence,
        extraction_summary=summary,
    )


@router.post("/admin/import", response_model=IngestionResultResponse)
def admin_bulk_import(
    items: List[SchemeIngestionItem],
    source_name: str = Query("ADMIN_CATALOGUE_UPLOAD", description="Name of source or file"),
    source_url: Optional[str] = Query(None, description="Optional provenance URL"),
    db: Session = Depends(get_db),
):
    """
    Administrative bulk scheme import endpoint.
    Accepts JSON catalogue items, deduplicates, and creates or updates verified records.
    """
    dict_items = [i.model_dump() for i in items]
    return SchemeIngestionService.ingest_records(
        db=db,
        items=dict_items,
        source_name=source_name,
        source_url=source_url,
    )


@router.post("/seed-nationwide", response_model=IngestionResultResponse)
def trigger_nationwide_seed(
    db: Session = Depends(get_db),
):
    """
    Trigger nationwide ingestion of official Central, 28 States, and 8 UT schemes.
    """
    return SchemeIngestionService.seed_nationwide_registry(db)


@router.post("/benefit-combinations", response_model=BenefitCombinationResponse)
def find_benefit_combinations(
    profile: BenefitCombinationRequest,
    db: Session = Depends(get_db),
):
    """
    Find compatible multi-scheme benefit stacks for a citizen profile.

    Accepts lightweight profile signals (age, state, categories, beneficiary groups)
    and returns ranked scheme matches with compatibility scores and match reasons.
    No PII is stored — the profile is used only for in-request scoring.
    """
    from sqlalchemy import and_

    query = select(GovernmentScheme).where(
        and_(
            GovernmentScheme.is_active == True,  # noqa: E712
            GovernmentScheme.is_candidate == False,  # noqa: E712
        )
    )
    all_schemes = db.execute(query).scalars().all()

    state_upper = profile.state_code.upper() if profile.state_code else None
    category_set = {c.lower() for c in profile.category_interests}
    group_set = {g.lower() for g in profile.beneficiary_groups}
    gender_lower = profile.gender.lower() if profile.gender else None

    matches: list[BenefitCombinationMatch] = []

    for scheme in all_schemes:
        score = 0.0
        reasons: list[str] = []

        # — State/UT match (highest weight for state-level schemes)
        if scheme.government_level == "central":
            score += 0.25
            reasons.append("Available nationwide (Central Government scheme)")
        elif state_upper and scheme.state_code == state_upper:
            score += 0.35
            reasons.append(f"Available in your selected state/UT ({scheme.state_code})")
        elif state_upper and scheme.state_code and scheme.state_code != state_upper:
            # Different state — skip unless category matches strongly
            if not category_set.intersection({scheme.category}):
                continue

        # — Category match
        if scheme.category and scheme.category in category_set:
            score += 0.30
            reasons.append(f"Matches your interest: {scheme.category.replace('_', ' ').title()}")

        # — Beneficiary group overlap
        scheme_groups = {g.lower() for g in (scheme.beneficiary_groups or [])}
        common_groups = group_set.intersection(scheme_groups)
        if common_groups:
            group_score = min(0.25, len(common_groups) * 0.10)
            score += group_score
            reasons.append(f"Covers beneficiary group(s): {', '.join(g.title() for g in common_groups)}")

        # — Age range fit
        if profile.age is not None:
            if scheme.min_age is not None and profile.age < scheme.min_age:
                continue  # Strictly under-age
            if scheme.max_age is not None and profile.age > scheme.max_age:
                continue  # Strictly over-age
            if scheme.min_age is not None or scheme.max_age is not None:
                score += 0.10
                reasons.append("Matches your age range")

        # — Gender alignment via beneficiary group keywords
        if gender_lower in ("female", "woman", "women"):
            if any(g in scheme_groups for g in ("women", "female", "girls", "girl_child")):
                score += 0.10
                reasons.append("Scheme specifically targets women/girl beneficiaries")
        elif gender_lower in ("male", "man", "men"):
            if any(g in scheme_groups for g in ("men", "male", "boys")):
                score += 0.05

        # — Guided preparation bonus (more useful to the citizen)
        if scheme.portal_capability in ("GUIDED_PREPARATION", "DRAFT_EXPORT"):
            score += 0.05
            reasons.append("Guided application preparation supported")

        if score > 0.05 and reasons:
            matches.append(BenefitCombinationMatch(
                scheme=GovernmentSchemeSummary.model_validate(scheme),
                compatibility_score=round(min(score, 1.0), 3),
                match_reasons=reasons,
                is_stackable=True,
            ))

    # Sort by descending score, then alphabetically
    matches.sort(key=lambda m: (-m.compatibility_score, m.scheme.display_name))
    matches = matches[: profile.max_results]

    # Build profile summary
    parts = []
    if profile.age is not None:
        parts.append(f"Age {profile.age}")
    if state_upper:
        parts.append(f"State: {state_upper}")
    if category_set:
        parts.append(f"Categories: {', '.join(c.title() for c in sorted(category_set))}")
    if group_set:
        parts.append(f"Groups: {', '.join(g.title() for g in sorted(group_set))}")
    profile_summary = " · ".join(parts) if parts else "General citizen (no profile filters applied)"

    return BenefitCombinationResponse(
        matches=matches,
        total_matched=len(matches),
        profile_summary=profile_summary,
    )


@router.get("/coverage-audit", response_model=SchemeCoverageAuditResponse)
def get_scheme_coverage_audit(
    db: Session = Depends(get_db),
):
    """
    Automated coverage check that audits every registered scheme and verifies
    whether it has a complete, working guided application workflow.
    """
    schemes = db.execute(
        select(GovernmentScheme)
        .options(
            selectinload(GovernmentScheme.fields),
            selectinload(GovernmentScheme.eligibility_requirements),
            selectinload(GovernmentScheme.document_requirements),
            selectinload(GovernmentScheme.application_steps),
        )
        .where(GovernmentScheme.is_active == True)  # noqa: E712
    ).scalars().all()

    items: List[SchemeCoverageAuditItem] = []
    fully_supported = 0
    pending_verification = 0
    unsupported = 0

    for s in schemes:
        has_fields = len(s.fields) > 0
        has_elig = len(s.eligibility_requirements) > 0
        has_docs = len(s.document_requirements) > 0
        has_steps = len(s.application_steps) > 0
        is_full = has_fields and has_elig and has_docs and has_steps and s.form_status == "VERIFIED_SCHEMA"

        if is_full:
            fully_supported += 1
        elif has_fields or has_elig or has_docs:
            pending_verification += 1
        else:
            unsupported += 1

        items.append(
            SchemeCoverageAuditItem(
                id=s.id,
                canonical_id=s.canonical_id,
                slug=s.slug,
                display_name=s.display_name,
                government_level=s.government_level,
                state_code=s.state_code,
                category=s.category,
                form_status=s.form_status,
                verification_status=s.verification_status,
                has_fields=has_fields,
                fields_count=len(s.fields),
                has_eligibility=has_elig,
                has_documents=has_docs,
                has_steps=has_steps,
                is_fully_supported=is_full,
            )
        )

    total = len(schemes)
    cov_pct = (fully_supported / total * 100.0) if total > 0 else 0.0

    return SchemeCoverageAuditResponse(
        total_schemes=total,
        fully_supported_schemes=fully_supported,
        pending_verification_schemes=pending_verification,
        unsupported_schemes=unsupported,
        coverage_percentage=round(cov_pct, 1),
        items=items,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/{scheme_id}", response_model=GovernmentSchemeDetail)
async def get_scheme_detail(
    scheme_id: int,
    lang: Optional[str] = Query(None, description="Optional target language code for translated content"),
    db: Session = Depends(get_db),
):
    """
    Get detailed scheme definition including ordered form fields,
    eligibility criteria, document requirements, and step-by-step instructions.
    When lang is provided, benefit details and descriptions are delivered in that language.
    """
    scheme = db.execute(
        select(GovernmentScheme)
        .options(
            selectinload(GovernmentScheme.fields),
            selectinload(GovernmentScheme.eligibility_requirements),
            selectinload(GovernmentScheme.document_requirements),
            selectinload(GovernmentScheme.application_steps),
        )
        .where(GovernmentScheme.id == scheme_id)
    ).scalar_one_or_none()

    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {scheme_id} not found.",
        )
    detail = GovernmentSchemeDetail.model_validate(scheme)
    if lang:
        localized_b = await multilingual_scheme_service.get_localized_scheme_benefits(db, scheme, lang)
        detail.benefit_details = localized_b
    return detail


@router.get("/{scheme_id}/benefits")
async def get_scheme_benefits(
    scheme_id: int,
    lang: str = Query("en", description="Target language code"),
    db: Session = Depends(get_db),
):
    """
    Get verified, fully localized scheme benefit details in any of the 22 Eighth Schedule Indian languages.
    Preserves exact statutory numbers, thresholds, and official portal citations.
    """
    scheme = db.get(GovernmentScheme, scheme_id)
    if not scheme:
        scheme = db.execute(select(GovernmentScheme).where(GovernmentScheme.slug == str(scheme_id))).scalar_one_or_none()
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID or slug '{scheme_id}' not found.",
        )
    return await multilingual_scheme_service.get_localized_scheme_benefits(db, scheme, lang)


@router.get("/{scheme_id}/fields", response_model=List[FormFieldResponse])
def get_scheme_fields(
    scheme_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch all form fields for a scheme, ordered by sort_order.
    """
    fields = db.execute(
        select(FormField)
        .where(FormField.scheme_id == scheme_id)
        .order_by(FormField.sort_order)
    ).scalars().all()

    if not fields:
        scheme_exists = db.execute(
            select(GovernmentScheme.id).where(GovernmentScheme.id == scheme_id)
        ).scalar_one_or_none()
        if not scheme_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme with ID {scheme_id} not found.",
            )
        return []

    return [FormFieldResponse.model_validate(f) for f in fields]


@router.get("/{scheme_id}/eligibility", response_model=List[SchemeEligibilityRequirementResponse])
def get_scheme_eligibility(
    scheme_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch all structured eligibility requirements for a scheme.
    """
    reqs = db.execute(
        select(SchemeEligibilityRequirement)
        .where(SchemeEligibilityRequirement.scheme_id == scheme_id)
        .order_by(SchemeEligibilityRequirement.sort_order)
    ).scalars().all()

    scheme_exists = db.execute(
        select(GovernmentScheme.id).where(GovernmentScheme.id == scheme_id)
    ).scalar_one_or_none()
    if not scheme_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {scheme_id} not found.",
        )

    return [SchemeEligibilityRequirementResponse.model_validate(r) for r in reqs]


@router.get("/{scheme_id}/documents", response_model=List[SchemeDocumentRequirementResponse])
def get_scheme_documents(
    scheme_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch all required and conditional documents for a scheme.
    """
    docs = db.execute(
        select(SchemeDocumentRequirement)
        .where(SchemeDocumentRequirement.scheme_id == scheme_id)
        .order_by(SchemeDocumentRequirement.sort_order)
    ).scalars().all()

    scheme_exists = db.execute(
        select(GovernmentScheme.id).where(GovernmentScheme.id == scheme_id)
    ).scalar_one_or_none()
    if not scheme_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {scheme_id} not found.",
        )

    return [SchemeDocumentRequirementResponse.model_validate(d) for d in docs]


@router.get("/{scheme_id}/steps", response_model=List[SchemeApplicationStepResponse])
def get_scheme_steps(
    scheme_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch step-by-step application instructions for a scheme.
    """
    steps = db.execute(
        select(SchemeApplicationStep)
        .where(SchemeApplicationStep.scheme_id == scheme_id)
        .order_by(SchemeApplicationStep.step_number)
    ).scalars().all()

    scheme_exists = db.execute(
        select(GovernmentScheme.id).where(GovernmentScheme.id == scheme_id)
    ).scalar_one_or_none()
    if not scheme_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {scheme_id} not found.",
        )

    return [SchemeApplicationStepResponse.model_validate(s) for s in steps]


@router.get("/{scheme_id}/guidance", response_model=SchemeGuidancePacket)
async def get_scheme_guidance_packet(
    scheme_id: int,
    lang: str = Query("hi", description="Citizen target language code"),
    db: Session = Depends(get_db),
):
    """
    Get full Guided Self-Application packet for a scheme including
    metadata, eligibility rules, document checklist, steps, and fields,
    with language coverage and multilingual resolution for any of the 22 languages.
    """
    scheme = db.execute(
        select(GovernmentScheme)
        .options(
            selectinload(GovernmentScheme.fields),
            selectinload(GovernmentScheme.eligibility_requirements),
            selectinload(GovernmentScheme.document_requirements),
            selectinload(GovernmentScheme.application_steps),
        )
        .where(GovernmentScheme.id == scheme_id)
    ).scalar_one_or_none()

    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID {scheme_id} not found.",
        )

    # Localize scheme summary
    scheme_summary = GovernmentSchemeSummary.model_validate(scheme)
    localized_b = await multilingual_scheme_service.get_localized_scheme_benefits(db, scheme, lang)
    scheme_summary.benefit_details = localized_b

    # Ensure descriptions_by_language has target language
    if lang not in scheme_summary.descriptions_by_language:
        trans_desc = await multilingual_scheme_service.get_or_translate_text(
            db, scheme.description, lang, scheme_slug=scheme.slug, field_type="description"
        )
        scheme_summary.descriptions_by_language[lang] = trans_desc.get("translated_text") or scheme.description

    # Ensure application_instructions_by_language has target language
    base_inst = scheme.application_instructions_by_language.get("en") or scheme.description
    if lang not in scheme_summary.application_instructions_by_language:
        trans_inst = await multilingual_scheme_service.get_or_translate_text(
            db, base_inst, lang, scheme_slug=scheme.slug, field_type="instructions"
        )
        scheme_summary.application_instructions_by_language[lang] = trans_inst.get("translated_text") or base_inst

    # Check whether target language is translated across components
    missing_for_scheme = scheme.missing_languages([lang])
    is_complete = len(missing_for_scheme) == 0

    all_missing = scheme.missing_languages(SCHEDULED_LANGUAGES_22)

    # Determine form completeness and transparent disclosures
    is_fully_configured = (
        len(scheme.fields) > 0
        and len(scheme.eligibility_requirements) > 0
        and len(scheme.document_requirements) > 0
        and scheme.form_status == "VERIFIED_SCHEMA"
    )
    form_completeness = "complete" if is_fully_configured else "pending_verification"

    disclosures: List[str] = []
    if scheme.verification_status != "verified":
        disclosures.append("Administrative field rules are undergoing official state gazette reverification.")
    if not scheme.official_application_url:
        disclosures.append("Direct departmental web submission link is under official notification.")
    if scheme.is_candidate:
        disclosures.append("Candidate scheme extracted from public notice. Requirements are subject to departmental confirmation.")

    return SchemeGuidancePacket(
        scheme=scheme_summary,
        eligibility_requirements=[
            SchemeEligibilityRequirementResponse.model_validate(r) for r in scheme.eligibility_requirements
        ],
        document_requirements=[
            SchemeDocumentRequirementResponse.model_validate(d) for d in scheme.document_requirements
        ],
        application_steps=[
            SchemeApplicationStepResponse.model_validate(s) for s in scheme.application_steps
        ],
        fields=[
            FormFieldResponse.model_validate(f) for f in scheme.fields
        ],
        target_language=lang,
        is_translation_complete=is_complete,
        missing_languages=all_missing,
        form_completeness=form_completeness,
        unverified_disclosures=disclosures,
    )
