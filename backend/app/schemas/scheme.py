"""
GovernmentScheme, FormField, and Guided Self-Application schemas for NagrikSaarathi API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SchemeEligibilityRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    criterion_key: str
    criterion_type: str
    operator: Optional[str] = None
    threshold_value: Optional[Dict[str, Any]] = None
    is_mandatory: bool
    sort_order: int
    titles_by_language: Dict[str, str] = Field(default_factory=dict)
    descriptions_by_language: Dict[str, str] = Field(default_factory=dict)
    official_source_reference: Optional[str] = None
    verification_status: str
    last_verified_at: Optional[datetime] = None


class SchemeDocumentRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    document_code: str
    requirement_type: str
    condition_rule: Optional[Dict[str, Any]] = None
    is_mandatory: bool
    sort_order: int
    titles_by_language: Dict[str, str] = Field(default_factory=dict)
    descriptions_by_language: Dict[str, str] = Field(default_factory=dict)
    issuing_authority: Optional[str] = None
    validity_period_info: Optional[str] = None
    official_source_url: Optional[str] = None
    source_reference: Optional[str] = None
    verification_status: str
    last_verified_at: Optional[datetime] = None


class SchemeApplicationStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    step_number: int
    step_key: str
    titles_by_language: Dict[str, str] = Field(default_factory=dict)
    instructions_by_language: Dict[str, str] = Field(default_factory=dict)
    official_action_url: Optional[str] = None
    source_reference: Optional[str] = None
    verification_status: str
    last_verified_at: Optional[datetime] = None


class FormFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: int
    field_key: str
    field_type: str
    required: bool
    sort_order: int
    labels_by_language: Dict[str, str] = Field(default_factory=dict)
    explanations_by_language: Dict[str, str] = Field(default_factory=dict)
    instructions_by_language: Dict[str, str] = Field(default_factory=dict)
    examples_by_language: Dict[str, str] = Field(default_factory=dict)
    validation_guidance_by_language: Dict[str, str] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    source_reference: Optional[str] = None
    verification_status: str = "verified"
    last_verified_at: Optional[datetime] = None


class GovernmentSchemeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    display_name: str
    description: str
    department_name: str
    official_source_url: str
    source_document_reference: Optional[str] = None
    is_demo: bool
    is_active: bool
    # Catalogue / Classification Fields
    canonical_id: Optional[str] = None
    alternate_names: List[str] = Field(default_factory=list)
    ministry_name: Optional[str] = None
    nodal_agency: Optional[str] = None
    source_feed_type: str = "OFFICIAL_PORTAL"
    form_status: str = "VERIFIED_SCHEMA"
    last_reverified_at: Optional[datetime] = None
    reverification_notes: Optional[str] = None

    government_level: str = "central"
    state_code: Optional[str] = None
    category: str = "other"
    beneficiary_groups: List[str] = Field(default_factory=list)
    application_method: str = "unknown"
    portal_capability: str = "GUIDED_PREPARATION"
    keywords: List[str] = Field(default_factory=list)
    scheme_status: str = "active"
    is_candidate: bool = False
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    official_application_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    verification_status: str = "verified"
    verification_source_reference: Optional[str] = None
    descriptions_by_language: Dict[str, str] = Field(default_factory=dict)
    application_instructions_by_language: Dict[str, str] = Field(default_factory=dict)
    benefit_details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    # URL Authority & Classification metadata
    official_source_label: Optional[str] = "Official Government Portal"
    official_application_label: Optional[str] = None
    application_portal_type: Optional[str] = None
    official_source_is_fallback: bool = False
    official_application_is_fallback: bool = False

    @model_validator(mode="after")
    def populate_url_authority_metadata(self) -> "GovernmentSchemeSummary":
        from backend.app.services.url_authority_service import UrlAuthorityService
        from backend.app.services.benefit_service import SchemeBenefitService

        resolved = UrlAuthorityService.resolve_scheme_urls(
            official_source_url=self.official_source_url,
            official_application_url=self.official_application_url,
            state_code=self.state_code,
            application_method=self.application_method,
        )
        self.official_source_url = resolved["official_source_url"]
        self.official_source_label = resolved["official_source_label"]
        self.official_source_is_fallback = resolved["official_source_is_fallback"]

        self.official_application_url = resolved["official_application_url"]
        self.official_application_label = resolved["official_application_label"]
        self.official_application_is_fallback = resolved["official_application_is_fallback"]
        self.application_portal_type = resolved["portal_type"]

        if not self.benefit_details or not self.benefit_details.get("assistance_type"):
            self.benefit_details = SchemeBenefitService.resolve_benefit_details(self)

        return self


class PaginatedSchemesResponse(BaseModel):
    items: List[GovernmentSchemeSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class CandidateSchemeCreate(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=200)
    official_source_url: Optional[str] = Field(None, max_length=500)
    department_name: Optional[str] = Field(None, max_length=200)
    government_level: Optional[str] = Field("central")
    state_code: Optional[str] = Field(None, max_length=10)
    category: Optional[str] = Field("other", max_length=40)
    description: Optional[str] = Field(None)
    user_notes: Optional[str] = Field(None)


class FormExtractionRequest(BaseModel):
    scheme_name: str = Field(..., min_length=2, max_length=200)
    official_url: Optional[str] = Field(None, max_length=500)
    form_text_or_url: str = Field(..., min_length=10)
    state_code: Optional[str] = Field(None, max_length=10)
    category: Optional[str] = Field("other", max_length=40)
    user_notes: Optional[str] = Field(None)


class FormExtractionCandidateResponse(BaseModel):
    scheme: GovernmentSchemeSummary
    extracted_fields: List[FormFieldResponse]
    confidence_score: float
    extraction_summary: str


class SchemeIngestionItem(BaseModel):
    canonical_id: Optional[str] = None
    slug: Optional[str] = None
    display_name: str
    alternate_names: List[str] = Field(default_factory=list)
    description: Optional[str] = ""
    department_name: Optional[str] = ""
    ministry_name: Optional[str] = None
    nodal_agency: Optional[str] = None
    government_level: str = "central"
    state_code: Optional[str] = None
    category: str = "other"
    beneficiary_groups: List[str] = Field(default_factory=list)
    application_method: str = "online"
    portal_capability: str = "GUIDED_PREPARATION"
    official_source_url: Optional[str] = ""
    official_application_url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    source_feed_type: str = "ADMIN_IMPORT"
    form_status: str = "VERIFIED_SCHEMA"
    verification_status: str = "verified"


class IngestionResultResponse(BaseModel):
    source_name: str
    total_processed: int
    records_created: int
    records_updated: int
    records_duplicates: int
    records_rejected: int
    status: str
    summary_notes: str
    errors: List[str] = Field(default_factory=list)


class GovernmentSchemeDetail(GovernmentSchemeSummary):
    fields: List[FormFieldResponse] = Field(default_factory=list)
    eligibility_requirements: List[SchemeEligibilityRequirementResponse] = Field(default_factory=list)
    document_requirements: List[SchemeDocumentRequirementResponse] = Field(default_factory=list)
    application_steps: List[SchemeApplicationStepResponse] = Field(default_factory=list)


class SchemeGuidancePacket(BaseModel):
    """Consolidated package for Guided Self-Application."""
    scheme: GovernmentSchemeSummary
    eligibility_requirements: List[SchemeEligibilityRequirementResponse] = Field(default_factory=list)
    document_requirements: List[SchemeDocumentRequirementResponse] = Field(default_factory=list)
    application_steps: List[SchemeApplicationStepResponse] = Field(default_factory=list)
    fields: List[FormFieldResponse] = Field(default_factory=list)
    target_language: str
    is_translation_complete: bool
    missing_languages: List[str] = Field(default_factory=list)
    form_completeness: str = "complete"  # "complete" | "pending_verification" | "fallback_guidance"
    unverified_disclosures: List[str] = Field(default_factory=list)


class SchemeCoverageAuditItem(BaseModel):
    id: int
    canonical_id: Optional[str] = None
    slug: str
    display_name: str
    government_level: str
    state_code: Optional[str] = None
    category: str
    form_status: str
    verification_status: str
    has_fields: bool
    fields_count: int
    has_eligibility: bool
    has_documents: bool
    has_steps: bool
    is_fully_supported: bool


class SchemeCoverageAuditResponse(BaseModel):
    total_schemes: int
    fully_supported_schemes: int
    pending_verification_schemes: int
    unsupported_schemes: int
    coverage_percentage: float
    items: List[SchemeCoverageAuditItem]
    generated_at: datetime


# ── Benefit Combination Finder ───────────────────────────────────────────────

class BenefitCombinationRequest(BaseModel):
    """Citizen profile signals used to find compatible multi-scheme benefit stacks."""
    age: Optional[int] = Field(None, ge=0, le=120, description="Citizen age in years")
    state_code: Optional[str] = Field(None, max_length=10, description="State/UT code, e.g. MH, WB")
    gender: Optional[str] = Field(None, max_length=20, description="Gender identity, e.g. female, male, other")
    category_interests: List[str] = Field(
        default_factory=list,
        description="Scheme categories the citizen is interested in, e.g. ['healthcare', 'education']",
    )
    beneficiary_groups: List[str] = Field(
        default_factory=list,
        description="Self-identified beneficiary groups, e.g. ['students', 'farmers', 'women']",
    )
    max_results: int = Field(10, ge=1, le=30, description="Maximum number of compatible schemes to return")


class BenefitCombinationMatch(BaseModel):
    """A single scheme match in a benefit combination result set."""
    scheme: GovernmentSchemeSummary
    compatibility_score: float = Field(description="0.0–1.0 score indicating profile fit")
    match_reasons: List[str] = Field(default_factory=list, description="Human-readable reasons for this match")
    is_stackable: bool = Field(
        True,
        description="Whether this scheme is generally compatible with simultaneous enrolment in other schemes",
    )


class BenefitCombinationResponse(BaseModel):
    """Response for the Benefit Combination Finder endpoint."""
    matches: List[BenefitCombinationMatch]
    total_matched: int
    profile_summary: str = Field(description="Short human-readable summary of the profile signals used")
    disclaimer: str = Field(
        default=(
            "These results are indicative only. Eligibility is determined by the respective scheme authority. "
            "NagrikSaarathi does not guarantee entitlement to any benefit."
        )
    )


# ── Missing Scheme Radar ─────────────────────────────────────────────────────

class MissingSchemeRadarItem(BaseModel):
    """Describes a coverage gap or stale record flagged by the radar."""
    radar_type: str = Field(
        description="Gap type: 'zero_coverage' | 'low_coverage' | 'stale_record' | 'pending_candidate' | 'no_form_schema'"
    )
    jurisdiction: Optional[str] = None  # State/UT name or 'Central'
    jurisdiction_code: Optional[str] = None
    scheme_id: Optional[int] = None
    scheme_name: Optional[str] = None
    scheme_slug: Optional[str] = None
    detail: str = Field(description="Human-readable description of the gap or issue")
    severity: str = Field(default="medium", description="low | medium | high")
    suggested_action: Optional[str] = None


class MissingSchemeRadarResponse(BaseModel):
    """Aggregated Missing Scheme Radar report for administrators."""
    total_gaps: int
    zero_coverage_jurisdictions: int
    low_coverage_jurisdictions: int
    stale_records: int
    pending_candidates: int
    no_form_schema_schemes: int
    items: List[MissingSchemeRadarItem]
    generated_at: datetime
