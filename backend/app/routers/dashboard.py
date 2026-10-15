"""
Dashboard Analytics router for NagrikSaarathi API.

Features:
- Access control: Protected by admin auth in production; permits synthetic demo viewing in demo mode.
- Strict demo-data segregation and date range filtering.
- Mathematically explicit rates and percentages.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import (
    GovernmentScheme,
    HelpTicket,
    SchemeRequest,
    SCHEME_REQUEST_STATUSES,
    HELP_TICKET_STATUSES,
    SCHEDULED_LANGUAGES_22,
)
from backend.app.schemas.dashboard import (
    BarrierMetricsResponse,
    FieldMetricsResponse,
    LanguageMetricsResponse,
    NationwideCoverageResponse,
    RecoveryMetricsResponse,
    SummaryMetricsResponse,
    TranslationQualityResponse,
)
from backend.app.schemas.help_ticket import (
    HelpTicketAdminUpdate,
    HelpTicketResponse,
)
from backend.app.schemas.scheme import (
    MissingSchemeRadarItem,
    MissingSchemeRadarResponse,
)
from backend.app.schemas.scheme_request import (
    SchemeRequestAdminUpdate,
    SchemeRequestPublish,
    SchemeRequestResponse,
)
from backend.app.security import check_dashboard_access
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.scheme_ingestion_service import SchemeIngestionService
from backend.app.services.url_authority_service import UrlAuthorityService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/summary", response_model=SummaryMetricsResponse)
def get_summary(
    include_demo: bool = Query(True, description="Whether to include simulated demo sessions"),
    start_date: Optional[datetime] = Query(None, description="ISO datetime start filter"),
    end_date: Optional[datetime] = Query(None, description="ISO datetime end filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Get aggregated summary metrics: total consented sessions, completion rate, abandonment rate.
    """
    return AnalyticsService.get_summary(
        db=db,
        include_demo=include_demo,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/barriers", response_model=BarrierMetricsResponse)
def get_barriers(
    include_demo: bool = Query(True, description="Whether to include simulated demo sessions"),
    start_date: Optional[datetime] = Query(None, description="ISO datetime start filter"),
    end_date: Optional[datetime] = Query(None, description="ISO datetime end filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Get distribution of identified barrier categories across consented sessions.
    """
    return AnalyticsService.get_barriers(
        db=db,
        include_demo=include_demo,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/languages", response_model=LanguageMetricsResponse)
def get_languages(
    include_demo: bool = Query(True, description="Whether to include simulated demo sessions"),
    start_date: Optional[datetime] = Query(None, description="ISO datetime start filter"),
    end_date: Optional[datetime] = Query(None, description="ISO datetime end filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Get volume and barrier frequency broken down by Indian language.
    """
    return AnalyticsService.get_language_metrics(
        db=db,
        include_demo=include_demo,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/fields", response_model=FieldMetricsResponse)
def get_problematic_fields(
    include_demo: bool = Query(True, description="Whether to include simulated demo sessions"),
    start_date: Optional[datetime] = Query(None, description="ISO datetime start filter"),
    end_date: Optional[datetime] = Query(None, description="ISO datetime end filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Identify specific form fields causing the highest frequency of application barriers.
    """
    return AnalyticsService.get_field_metrics(
        db=db,
        include_demo=include_demo,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/recovery", response_model=RecoveryMetricsResponse)
def get_recovery(
    include_demo: bool = Query(True, description="Whether to include simulated demo sessions"),
    start_date: Optional[datetime] = Query(None, description="ISO datetime start filter"),
    end_date: Optional[datetime] = Query(None, description="ISO datetime end filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Calculate issue resolution and recovery rate after assistance guidance.
    """
    return AnalyticsService.get_recovery_metrics(
        db=db,
        include_demo=include_demo,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/translation-quality", response_model=TranslationQualityResponse)
def get_translation_quality(
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Audit localization coverage and translation review status across all 22 languages.
    """
    return AnalyticsService.get_translation_quality(db=db)


@router.get("/coverage", response_model=NationwideCoverageResponse)
def get_nationwide_coverage(
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Nationwide scheme coverage and gap-tracking report covering all 28 states,
    8 Union Territories, Central ministries, verified official sources, and form availability.
    """
    return SchemeIngestionService.calculate_nationwide_coverage(db=db)


@router.get("/missing-radar", response_model=MissingSchemeRadarResponse)
def get_missing_scheme_radar(
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Missing Scheme Radar — identifies coverage gaps, stale records, and candidate backlogs
    so administrators can prioritise data-quality improvements.

    Detects:
    - Jurisdictions with zero catalogued schemes (high severity)
    - Jurisdictions with fewer than 3 schemes (medium severity)
    - Schemes with 'outdated' or long-unverified verification_status (medium)
    - Pending citizen-submitted candidate schemes awaiting review (low)
    - Active schemes with form_status='NO_FORM' or 'EXTERNAL_LINK_ONLY' (low)
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func, select
    from backend.app.models import GovernmentScheme

    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=180)  # 6-month re-verification window

    ALL_JURISDICTIONS = {
        # 28 States
        "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh", "AS": "Assam",
        "BR": "Bihar", "CG": "Chhattisgarh", "GA": "Goa", "GJ": "Gujarat",
        "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
        "KA": "Karnataka", "KL": "Kerala", "MP": "Madhya Pradesh",
        "MH": "Maharashtra", "MN": "Manipur", "ML": "Meghalaya",
        "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha", "PB": "Punjab",
        "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu", "TG": "Telangana",
        "TR": "Tripura", "UP": "Uttar Pradesh", "UK": "Uttarakhand", "WB": "West Bengal",
        # 8 Union Territories
        "AN": "Andaman & Nicobar Islands", "CH": "Chandigarh",
        "DN": "Dadra & Nagar Haveli and Daman & Diu", "DL": "Delhi (NCT)",
        "JK": "Jammu & Kashmir", "LA": "Ladakh", "LD": "Lakshadweep", "PY": "Puducherry",
    }

    items: list[MissingSchemeRadarItem] = []

    # ── 1. Count verified non-candidate schemes per state/UT ─────────────────
    count_rows = db.execute(
        select(GovernmentScheme.state_code, func.count(GovernmentScheme.id))
        .where(
            GovernmentScheme.is_active == True,  # noqa: E712
            GovernmentScheme.is_candidate == False,  # noqa: E712
            GovernmentScheme.state_code != None,  # noqa: E711
        )
        .group_by(GovernmentScheme.state_code)
    ).all()
    state_counts = {row[0]: row[1] for row in count_rows}

    zero_coverage = 0
    low_coverage = 0
    for code, name in ALL_JURISDICTIONS.items():
        count = state_counts.get(code, 0)
        if count == 0:
            zero_coverage += 1
            items.append(MissingSchemeRadarItem(
                radar_type="zero_coverage",
                jurisdiction=name,
                jurisdiction_code=code,
                detail=f"No schemes catalogued for {name} ({code}).",
                severity="high",
                suggested_action=f"Seed at least one verified scheme from {name}'s e-District or official state portal.",
            ))
        elif count < 3:
            low_coverage += 1
            items.append(MissingSchemeRadarItem(
                radar_type="low_coverage",
                jurisdiction=name,
                jurisdiction_code=code,
                detail=f"Only {count} scheme(s) catalogued for {name} ({code}). Coverage is sparse.",
                severity="medium",
                suggested_action=f"Import additional schemes from {name}'s official portal or MyScheme dataset.",
            ))

    # ── 2. Stale / outdated verification status ──────────────────────────────
    stale_rows = db.execute(
        select(GovernmentScheme)
        .where(
            GovernmentScheme.is_active == True,  # noqa: E712
            GovernmentScheme.is_candidate == False,  # noqa: E712
            GovernmentScheme.verification_status == "outdated",
        )
        .order_by(GovernmentScheme.last_verified_at.asc().nullsfirst())
        .limit(50)
    ).scalars().all()
    stale_count = len(stale_rows)
    for s in stale_rows:
        items.append(MissingSchemeRadarItem(
            radar_type="stale_record",
            scheme_id=s.id,
            scheme_name=s.display_name,
            scheme_slug=s.slug,
            jurisdiction=s.state_code or "Central",
            jurisdiction_code=s.state_code,
            detail=f"'{s.display_name}' has verification_status='outdated'. Last verified: {s.last_verified_at or 'never'}.",
            severity="medium",
            suggested_action="Re-verify against the official government notification and update verification_status.",
        ))

    # ── 3. Pending citizen-submitted candidates ──────────────────────────────
    candidate_rows = db.execute(
        select(GovernmentScheme)
        .where(
            GovernmentScheme.is_candidate == True,  # noqa: E712
            GovernmentScheme.verification_status == "pending_review",
        )
        .order_by(GovernmentScheme.created_at.desc())
        .limit(30)
    ).scalars().all()
    candidate_count = len(candidate_rows)
    for c in candidate_rows:
        items.append(MissingSchemeRadarItem(
            radar_type="pending_candidate",
            scheme_id=c.id,
            scheme_name=c.display_name,
            scheme_slug=c.slug,
            jurisdiction=c.state_code or "Central",
            jurisdiction_code=c.state_code,
            detail=f"Citizen-submitted candidate '{c.display_name}' is pending admin review.",
            severity="low",
            suggested_action="Review the submission, verify from official source, and promote to verified or reject.",
        ))

    # ── 4. Active schemes with no usable form schema ─────────────────────────
    no_form_rows = db.execute(
        select(GovernmentScheme)
        .where(
            GovernmentScheme.is_active == True,  # noqa: E712
            GovernmentScheme.is_candidate == False,  # noqa: E712
            GovernmentScheme.form_status.in_(["NO_FORM", "EXTERNAL_LINK_ONLY"]),
        )
        .order_by(GovernmentScheme.id.asc())
        .limit(50)
    ).scalars().all()
    no_form_count = len(no_form_rows)
    for nf in no_form_rows:
        items.append(MissingSchemeRadarItem(
            radar_type="no_form_schema",
            scheme_id=nf.id,
            scheme_name=nf.display_name,
            scheme_slug=nf.slug,
            jurisdiction=nf.state_code or "Central",
            jurisdiction_code=nf.state_code,
            detail=f"'{nf.display_name}' has form_status='{nf.form_status}'. No guided preparation available.",
            severity="low",
            suggested_action="Add a verified form schema or extract fields from the official application form.",
        ))

    # Sort by severity: high → medium → low
    severity_order = {"high": 0, "medium": 1, "low": 2}
    items.sort(key=lambda x: severity_order.get(x.severity, 3))

    return MissingSchemeRadarResponse(
        total_gaps=len(items),
        zero_coverage_jurisdictions=zero_coverage,
        low_coverage_jurisdictions=low_coverage,
        stale_records=stale_count,
        pending_candidates=candidate_count,
        no_form_schema_schemes=no_form_count,
        items=items,
        generated_at=now,
    )


def _format_scheme_request_response(req: SchemeRequest, db: Session) -> SchemeRequestResponse:
    resp = SchemeRequestResponse.model_validate(req)
    if req.linked_scheme_id:
        linked = db.get(GovernmentScheme, req.linked_scheme_id)
        if linked:
            resp.linked_scheme_slug = linked.slug
            resp.linked_scheme_name = linked.display_name
    return resp


# ── Scheme Request Review Queue (Requirement 3) ──────────────────────────

@router.get("/scheme-requests", response_model=List[SchemeRequestResponse])
def get_scheme_requests(
    status_filter: Optional[str] = Query(None, description="Optional status filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Administrator Scheme Request Review queue.
    Lists citizen-submitted missing scheme requests with current status, notes, and links.
    """
    query = select(SchemeRequest).order_by(desc(SchemeRequest.created_at))
    if status_filter:
        query = query.where(SchemeRequest.status == status_filter.strip())

    requests = db.execute(query).scalars().all()
    return [_format_scheme_request_response(r, db) for r in requests]


@router.patch("/scheme-requests/{request_id}", response_model=SchemeRequestResponse)
def update_scheme_request(
    request_id: int,
    payload: SchemeRequestAdminUpdate,
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Update scheme request review status, administrator notes, rejection reason, or existing link.
    INVARIANT: Cannot mark 'Added to Catalogue' unless the linked scheme actually exists in database!
    """
    req = db.get(SchemeRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme request not found.")

    if payload.status not in SCHEME_REQUEST_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Must be one of: {list(SCHEME_REQUEST_STATUSES)}",
        )

    # CRITICAL: Confirm that the actual scheme record exists in the database before marking Added to Catalogue
    if payload.status == "Added to Catalogue":
        target_scheme_id = payload.linked_scheme_id or req.linked_scheme_id
        if not target_scheme_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot mark 'Added to Catalogue' without a verified linked scheme ID. Confirm that the scheme record exists in the database first.",
            )
        scheme_record = db.get(GovernmentScheme, target_scheme_id)
        if not scheme_record or not scheme_record.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Linked scheme with ID {target_scheme_id} does not exist or is inactive in the database.",
            )
        req.linked_scheme_id = scheme_record.id

    if payload.status in ("Already Exists", "Verified") and payload.linked_scheme_id:
        req.linked_scheme_id = payload.linked_scheme_id

    req.status = payload.status
    if payload.admin_notes is not None:
        req.admin_notes = payload.admin_notes.strip()
    if payload.rejection_reason is not None:
        req.rejection_reason = payload.rejection_reason.strip()

    req.reviewed_at = datetime.now(timezone.utc)
    req.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(req)
    return _format_scheme_request_response(req, db)


@router.post("/scheme-requests/{request_id}/publish", response_model=SchemeRequestResponse)
def publish_scheme_from_request(
    request_id: int,
    payload: SchemeRequestPublish,
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Transactional creation of a verified catalogue scheme record from a citizen request.
    Creates the GovernmentScheme record and atomically sets request status to 'Added to Catalogue'.
    """
    req = db.get(SchemeRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme request not found.")

    slug_base = re.sub(r"[^a-z0-9]+", "-", payload.display_name.lower()).strip("-")
    short_uuid = str(uuid.uuid4())[:8]
    slug = f"{slug_base}-{short_uuid}"[:100]

    state_code = req.state_code.upper() if req.state_code else None
    resolved = UrlAuthorityService.resolve_scheme_urls(
        official_source_url=payload.official_source_url,
        official_application_url=payload.official_application_url,
        state_code=state_code,
        application_method="online",
    )

    new_scheme = GovernmentScheme(
        canonical_id=f"SCHEME-{datetime.now(timezone.utc).year}-{short_uuid.upper()}",
        slug=slug,
        display_name=payload.display_name.strip(),
        description=payload.description or req.description or f"Official scheme: {payload.display_name}",
        department_name=payload.department_name or req.department_name or "Department to be verified",
        official_source_url=resolved["official_source_url"],
        official_application_url=resolved["official_application_url"],
        government_level=req.government_level or ("state" if state_code else "central"),
        state_code=state_code,
        category=payload.category,
        beneficiary_groups=payload.beneficiary_groups,
        portal_capability="DISCOVERY_ONLY",
        form_status="VERIFIED_SCHEMA",
        source_feed_type="CITIZEN_SUBMISSION",
        verification_status="verified",
        verification_source_reference=f"Approved from citizen request {req.tracking_id}",
        is_candidate=False,
        is_active=True,
    )
    db.add(new_scheme)
    db.flush()  # assign ID to new_scheme

    # Update request atomically
    req.status = "Added to Catalogue"
    req.linked_scheme_id = new_scheme.id
    req.admin_notes = payload.admin_notes or f"Verified and published as catalogue scheme ID {new_scheme.id}."
    req.reviewed_at = datetime.now(timezone.utc)
    req.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(req)
    return _format_scheme_request_response(req, db)


# ── Help & Support Ticket Queue (Requirement 4) ──────────────────────────

@router.get("/help-tickets", response_model=List[HelpTicketResponse])
def get_help_tickets(
    category_filter: Optional[str] = Query(None, description="Optional category filter"),
    status_filter: Optional[str] = Query(None, description="Optional status filter"),
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Administrator Help Ticket Support queue.
    Lists citizen support tickets with category, subject, status, and history.
    """
    query = select(HelpTicket).order_by(desc(HelpTicket.created_at))
    if category_filter:
        query = query.where(HelpTicket.category == category_filter.strip())
    if status_filter:
        query = query.where(HelpTicket.status == status_filter.strip())

    tickets = db.execute(query).scalars().all()
    return [HelpTicketResponse.model_validate(t) for t in tickets]


@router.patch("/help-tickets/{ticket_id}", response_model=HelpTicketResponse)
def update_help_ticket(
    ticket_id: int,
    payload: HelpTicketAdminUpdate,
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
):
    """
    Update ticket status, priority, admin notes, or resolution response.
    """
    ticket = db.get(HelpTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Help ticket not found.")

    now_iso = datetime.now(timezone.utc).isoformat()
    history_list = list(ticket.history or [])

    if payload.status:
        if payload.status not in HELP_TICKET_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{payload.status}'. Must be one of: {list(HELP_TICKET_STATUSES)}",
            )
        old_status = ticket.status
        ticket.status = payload.status
        if payload.status == "Resolved" and old_status != "Resolved":
            ticket.resolved_at = datetime.now(timezone.utc)
        history_list.append({
            "timestamp": now_iso,
            "actor": "official",
            "action": "status_changed",
            "details": f"Status updated from '{old_status}' to '{payload.status}'",
        })

    if payload.priority:
        ticket.priority = payload.priority
    if payload.admin_notes is not None:
        ticket.admin_notes = payload.admin_notes.strip()
    if payload.resolution_message is not None:
        ticket.resolution_message = payload.resolution_message.strip()
        history_list.append({
            "timestamp": now_iso,
            "actor": "official",
            "action": "resolution_provided",
            "details": f"Resolution response: {payload.resolution_message.strip()[:100]}...",
        })

    ticket.history = history_list
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return HelpTicketResponse.model_validate(ticket)


# ── Translation Completeness Audit (Requirement 1) ──────────────────────

@router.get("/translation-audit")
def get_translation_audit(
    _access: bool = Depends(check_dashboard_access),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Audit translation completeness across all 22 Eighth Schedule Indian languages (+ English).
    Calculates total canonical keys in en.json, translated count, missing count, coverage percent,
    and right-to-left flags.
    """
    locales_dir = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "src" / "i18n" / "locales"

    canonical_path = locales_dir / "en.json"
    if not canonical_path.exists():
        return {"error": "Canonical locale file en.json not found."}

    def _flatten_dict(d: dict, prefix: str = "") -> dict:
        items = {}
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(_flatten_dict(v, key))
            else:
                items[key] = str(v)
        return items

    with open(canonical_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    en_flat = _flatten_dict(en_data)
    total_canonical_keys = len(en_flat)

    rtl_langs = {"ur", "ks", "sd"}

    from backend.app.models import (
        Language,
        GovernmentScheme,
        FormField,
        SchemeEligibilityRequirement,
        SchemeDocumentRequirement,
    )
    from backend.app.services.multilingual_scheme_service import MULTILINGUAL_SCHEME_BENEFITS, LANGUAGE_SPECS

    db_langs = {l.language_code: l for l in db.execute(select(Language)).scalars().all()}
    all_schemes = db.execute(select(GovernmentScheme)).scalars().all()
    all_fields = db.execute(select(FormField)).scalars().all()
    all_elig = db.execute(select(SchemeEligibilityRequirement)).scalars().all()
    all_docs = db.execute(select(SchemeDocumentRequirement)).scalars().all()

    audit_results = []
    total_missing_all = 0

    lang_codes = ["en"] + list(SCHEDULED_LANGUAGES_22)

    for code in lang_codes:
        locale_file = locales_dir / f"{code}.json"
        lang_obj = db_langs.get(code)
        lang_name = lang_obj.english_name if lang_obj else (LANGUAGE_SPECS.get(code, {}).get("name") or code.upper())
        native_name = lang_obj.native_name if lang_obj else (LANGUAGE_SPECS.get(code, {}).get("native") or lang_name)
        script_name = lang_obj.writing_system if lang_obj else (LANGUAGE_SPECS.get(code, {}).get("script") or "Indic")
        is_rtl = code in rtl_langs

        ext_tts = code in {"bn", "hi", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "ne", "en"}
        browser_tts = code in {"en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "ne"}
        audio_status = "Ready (Tested)" if ext_tts else "Written Guidance Only"

        schemes_trans = sum(1 for s in all_schemes if s.descriptions_by_language and s.descriptions_by_language.get(code))
        benefits_trans = sum(1 for slug, b in MULTILINGUAL_SCHEME_BENEFITS.items() if b.get("assistance_type", {}).get(code))
        elig_trans = sum(1 for e in all_elig if e.descriptions_by_language and e.descriptions_by_language.get(code))
        docs_trans = sum(1 for d in all_docs if d.descriptions_by_language and d.descriptions_by_language.get(code))
        fields_trans = sum(1 for f in all_fields if f.labels_by_language and f.labels_by_language.get(code))

        if not locale_file.exists():
            audit_results.append({
                "language_code": code,
                "code": code,
                "name": lang_name,
                "native_name": native_name,
                "writing_system": script_name,
                "total_keys": total_canonical_keys,
                "translated_keys": 0,
                "missing_keys": total_canonical_keys,
                "missing_count": total_canonical_keys,
                "coverage_pct": 0.0,
                "coverage_percent": 0.0,
                "is_rtl": is_rtl,
                "schemes_translated": schemes_trans,
                "benefits_translated": benefits_trans,
                "eligibility_translated": elig_trans,
                "documents_translated": docs_trans,
                "form_questions_translated": fields_trans,
                "help_error_translated": 0,
                "review_status": "Missing",
                "awaiting_review": 0,
                "browser_tts": browser_tts,
                "external_tts": ext_tts,
                "audio_status": audio_status,
                "missing_key_samples": list(en_flat.keys())[:5],
                "status": "missing_file",
            })
            total_missing_all += total_canonical_keys
            continue

        try:
            with open(locale_file, "r", encoding="utf-8") as lf:
                loc_data = json.load(lf)
            loc_flat = _flatten_dict(loc_data)

            missing_keys = [k for k in en_flat if k not in loc_flat or not loc_flat[k].strip()]
            translated_count = total_canonical_keys - len(missing_keys)
            coverage = round((translated_count / max(1, total_canonical_keys)) * 100, 1)

            total_missing_all += len(missing_keys)
            help_err_trans = sum(1 for k in loc_flat if k.startswith("help.") or "error" in k.lower())
            is_reviewed = code in ["en", "hi", "bn"]
            rev_status = "Reviewed" if is_reviewed else ("Machine Localized" if len(missing_keys) == 0 else "Needs Review")
            awaiting = len(loc_flat) if not is_reviewed else 0

            audit_results.append({
                "language_code": code,
                "code": code,
                "name": lang_name,
                "native_name": native_name,
                "writing_system": script_name,
                "total_keys": total_canonical_keys,
                "translated_keys": translated_count,
                "missing_keys": len(missing_keys),
                "missing_count": len(missing_keys),
                "coverage_pct": coverage,
                "coverage_percent": coverage,
                "is_rtl": is_rtl,
                "schemes_translated": schemes_trans,
                "benefits_translated": benefits_trans,
                "eligibility_translated": elig_trans,
                "documents_translated": docs_trans,
                "form_questions_translated": fields_trans,
                "help_error_translated": help_err_trans,
                "review_status": rev_status,
                "awaiting_review": awaiting,
                "browser_tts": browser_tts,
                "external_tts": ext_tts,
                "audio_status": audio_status,
                "missing_key_samples": missing_keys[:5],
                "status": "complete" if len(missing_keys) == 0 else "partial",
            })
        except Exception as e:
            audit_results.append({
                "language_code": code,
                "code": code,
                "name": lang_name,
                "native_name": native_name,
                "writing_system": script_name,
                "total_keys": total_canonical_keys,
                "translated_keys": 0,
                "missing_keys": total_canonical_keys,
                "missing_count": total_canonical_keys,
                "coverage_pct": 0.0,
                "coverage_percent": 0.0,
                "is_rtl": is_rtl,
                "schemes_translated": schemes_trans,
                "benefits_translated": benefits_trans,
                "eligibility_translated": elig_trans,
                "documents_translated": docs_trans,
                "form_questions_translated": fields_trans,
                "help_error_translated": 0,
                "review_status": "Error",
                "awaiting_review": 0,
                "browser_tts": browser_tts,
                "external_tts": ext_tts,
                "audio_status": audio_status,
                "missing_key_samples": [],
                "status": f"error: {str(e)}",
            })

    total_possible = max(1, total_canonical_keys * len(audit_results))
    overall_cov = round(((total_possible - total_missing_all) / total_possible) * 100, 1)

    return {
        "total_canonical_keys": total_canonical_keys,
        "languages_audited": len(audit_results),
        "total_languages": len(audit_results),
        "total_missing_keys_nationwide": total_missing_all,
        "overall_coverage": overall_cov,
        "results": audit_results,
        "languages": audit_results,
        "sample_missing_keys": [k for r in audit_results for k in r.get("missing_key_samples", [])][:20],
        "audited_at": datetime.now(timezone.utc).isoformat(),
    }
