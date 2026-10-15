"""
NagrikSaarathi — Department & Scheme Proposal Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ministry_name: Optional[str] = None
    government_level: str = "central"
    state_code: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=250)
    ministry_name: Optional[str] = Field(None, max_length=250)
    government_level: str = Field("central", pattern="^(central|state|ut)$")
    state_code: Optional[str] = Field(None, max_length=10)


class SchemeProposalCreate(BaseModel):
    """Proposal payload submitted by a Department Official."""
    proposal_type: str = Field("new_scheme", pattern="^(new_scheme|metadata_update|url_correction|eligibility_update)$")
    scheme_id: Optional[int] = Field(None, description="Existing scheme ID if updating or correcting an existing scheme")
    scheme_name: str = Field(..., min_length=3, max_length=250)
    department_name: Optional[str] = Field(None, description="Defaults to official assigned department")
    government_level: str = Field("central", pattern="^(central|state|ut)$")
    state_code: Optional[str] = Field(None, max_length=10)
    category: str = Field("welfare", max_length=40)
    description: str = Field(..., min_length=20)
    benefit_summary: Optional[str] = None
    benefit_details: Dict[str, Any] = Field(default_factory=dict)
    eligibility_criteria: List[Dict[str, Any]] = Field(default_factory=list)
    document_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    application_instructions: Optional[str] = None
    official_source_url: Optional[str] = Field(None, max_length=500)
    official_application_url: Optional[str] = Field(None, max_length=500)
    source_evidence: str = Field(..., min_length=10, description="Mandatory official gazette, government order, or ministry citation")


class SchemeProposalUpdate(BaseModel):
    """Update payload by official when proposal is in draft or revision_required status."""
    scheme_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    benefit_summary: Optional[str] = None
    benefit_details: Optional[Dict[str, Any]] = None
    eligibility_criteria: Optional[List[Dict[str, Any]]] = None
    document_requirements: Optional[List[Dict[str, Any]]] = None
    application_instructions: Optional[str] = None
    official_source_url: Optional[str] = None
    official_application_url: Optional[str] = None
    source_evidence: Optional[str] = None
    submit_now: bool = False  # If true, transitions status from draft/revision_required to submitted


class SchemeProposalReview(BaseModel):
    """Review decision submitted by Principal Administrator."""
    action: str = Field(..., pattern="^(approve|reject|request_revision)$")
    admin_notes: Optional[str] = None
    revision_notes: Optional[str] = Field(None, description="Required when requesting revision")
    rejection_reason: Optional[str] = Field(None, description="Required when rejecting proposal")


class SchemeProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_number: str
    proposal_type: str
    scheme_id: Optional[int] = None
    official_id: int
    department_name: str
    state_code: Optional[str] = None
    government_level: str
    scheme_name: str
    description: str
    category: str
    benefit_summary: Optional[str] = None
    benefit_details: Dict[str, Any] = Field(default_factory=dict)
    eligibility_criteria: List[Dict[str, Any]] = Field(default_factory=list)
    document_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    application_instructions: Optional[str] = None
    official_source_url: Optional[str] = None
    official_application_url: Optional[str] = None
    source_evidence: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    revision_requested_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


class AdminAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    user_identifier: str
    user_role: str
    department: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    created_at: datetime


class DepartmentStatsResponse(BaseModel):
    department_name: str
    state_scope: Optional[str] = None
    total_schemes: int
    published_schemes: int
    draft_proposals: int
    pending_proposals: int
    revision_required_proposals: int
    approved_proposals: int
    rejected_proposals: int
    unverified_links_count: int


# ── Scheme Rule Change Radar Schemas ─────────────────────────────────────────

class RadarAnalyzeRequest(BaseModel):
    scheme_id: int = Field(..., description="Target existing government scheme ID")
    source_url: str = Field(..., min_length=5, max_length=500, description="Official government notification or gazette URL")
    source_title: str = Field(..., min_length=3, max_length=250, description="Title of the source order or notification")
    source_version: Optional[str] = Field(None, max_length=60, description="Version or Notification Number")
    source_publication_date: Optional[str] = Field(None, max_length=40, description="Date of issuance (e.g. 2026-04-01)")
    source_document_text: str = Field(..., min_length=20, description="Raw text of the revised official guideline or order")


class RadarChangeItem(BaseModel):
    category: str = Field(..., description="eligibility | benefits | documents | exclusions | deadlines | official_urls | instructions")
    field_name: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    supporting_passage: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_manual_validation: bool = True
    flag_reason: Optional[str] = None


class RadarDiffSummary(BaseModel):
    total_differences: int
    eligibility_changes_count: int
    benefit_changes_count: int
    document_changes_count: int
    url_changes_count: int
    uncertain_flags_count: int


class RadarAnalyzeResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    source_title: str
    source_url: str
    diff_summary: RadarDiffSummary
    detected_changes: List[RadarChangeItem]
    uncertain_flags: List[str]
    published_record_snapshot: Dict[str, Any]


class RadarSubmitRequest(BaseModel):
    scheme_id: int
    source_url: str
    source_title: str
    source_version: Optional[str] = None
    source_publication_date: Optional[str] = None
    source_document_text: str
    detected_changes: List[Dict[str, Any]]
    diff_summary: Dict[str, Any]
    uncertain_flags: List[str] = Field(default_factory=list)


class RadarReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|request_revision|reject)$")
    review_notes: Optional[str] = None


class RadarRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    radar_code: str
    scheme_id: int
    source_url: str
    source_title: str
    source_version: Optional[str] = None
    source_publication_date: Optional[str] = None
    submitted_by_id: int
    status: str
    detected_changes: List[Dict[str, Any]]
    diff_summary: Dict[str, Any]
    uncertain_flags: List[str]
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ── Citizen Difficulty Heatmap Schemas ───────────────────────────────────────

class HeatmapFieldMetric(BaseModel):
    field_key: str
    field_label: str
    step_number: Optional[int] = 1
    total_interactions: int
    help_requests: int
    validation_errors: int
    retries: int
    confusion_rate: float
    common_error_types: List[str] = Field(default_factory=list)


class HeatmapStepMetric(BaseModel):
    step_number: int
    step_title: str
    abandonment_count: int
    abandonment_rate: float


class HeatmapLanguageMetric(BaseModel):
    language_code: str
    language_name: str
    difficulty_reports: int
    help_requests: int


class CitizenDifficultyHeatmapResponse(BaseModel):
    department_name: Optional[str] = None
    scheme_id: Optional[int] = None
    total_sessions_analyzed: int
    is_insufficient_data: bool = False
    insufficient_data_notice: Optional[str] = None
    median_resolution_time_minutes: float = 0.0
    issue_resolution_rate: float = 0.0
    top_confusing_fields: List[HeatmapFieldMetric] = Field(default_factory=list)
    step_abandonment: List[HeatmapStepMetric] = Field(default_factory=list)
    language_difficulties: List[HeatmapLanguageMetric] = Field(default_factory=list)
    barrier_distribution: Dict[str, int] = Field(default_factory=dict)


# ── Evidence-Linked Scheme Editor Schemas ────────────────────────────────────

class SchemeFieldEvidenceCreate(BaseModel):
    scheme_id: int
    field_category: str = Field(..., pattern="^(eligibility|benefit|exclusion|document|application_step|official_url)$")
    field_key: str = Field(..., min_length=2, max_length=100)
    field_label: str = Field(..., min_length=2, max_length=200)
    claim_value: str = Field(..., min_length=1)
    official_source_url: str = Field(..., min_length=5, max_length=500)
    source_title: str = Field(..., min_length=3, max_length=250)
    responsible_department: str = Field(..., min_length=2, max_length=250)
    supporting_quotation: str = Field(..., min_length=10)
    document_page_section: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class SchemeFieldEvidenceUpdate(BaseModel):
    claim_value: Optional[str] = None
    official_source_url: Optional[str] = None
    source_title: Optional[str] = None
    supporting_quotation: Optional[str] = None
    document_page_section: Optional[str] = None
    verification_status: Optional[str] = None
    notes: Optional[str] = None


class SchemeFieldEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    field_category: str
    field_key: str
    field_label: str
    claim_value: str
    official_source_url: str
    source_title: str
    responsible_department: str
    supporting_quotation: str
    document_page_section: Optional[str] = None
    verification_status: str
    reviewer_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    last_source_review_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SchemeEvidenceHealthSummary(BaseModel):
    total_evidence_records: int
    verified_count: int
    pending_review_count: int
    broken_url_count: int
    outdated_review_count: int
    unverified_claims_count: int
    conflicting_count: int


# ── Translation Drift Monitor Schemas ────────────────────────────────────────

class TranslationDriftAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    scheme_name: Optional[str] = None
    field_key: str
    field_name: str
    source_language: str
    target_language: str
    previous_source_text: Optional[str] = None
    current_source_text: str
    existing_translated_text: Optional[str] = None
    candidate_translated_text: Optional[str] = None
    drift_status: str
    translation_mode: str
    reviewer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TranslationDriftComparisonResponse(BaseModel):
    alert_id: int
    scheme_id: int
    scheme_name: str
    field_name: str
    source_language: str
    target_language: str
    current_source_text: str
    previous_source_text: Optional[str] = None
    existing_translation: Optional[str] = None
    candidate_translation: Optional[str] = None
    drift_status: str
    translation_mode: str


class TranslationDriftApproveRequest(BaseModel):
    approved: bool
    verified_translation_text: Optional[str] = None
    reviewer_notes: Optional[str] = None

