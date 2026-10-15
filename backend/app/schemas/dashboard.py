"""
Dashboard analytics schemas for NagrikSaarathi API.

Metric transparency:
Explicit numerator and denominator definitions with demo-data separation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SummaryMetricsResponse(BaseModel):
    total_consented_sessions: int = Field(
        ..., description="Total assistance sessions with explicit citizen consent"
    )
    completed_sessions: int = Field(..., description="Sessions that reached application completion")
    abandoned_sessions: int = Field(..., description="Sessions that were abandoned before completion")
    needs_human_help_sessions: int = Field(
        ..., description="Sessions where citizen or desk operator escalated to human help"
    )
    completion_rate_pct: float = Field(
        ..., description="Numerator: completed_sessions / Denominator: total_consented_sessions (if > 0)"
    )
    abandonment_rate_pct: float = Field(
        ..., description="Numerator: abandoned_sessions / Denominator: total_consented_sessions (if > 0)"
    )
    is_demo_data: bool = Field(
        ..., description="True if simulated test data is included; False for strictly real observations"
    )
    data_source_note: str = Field(
        default="Observed barriers represent assisted sessions within NagrikSaarathi and do not reflect total population-level public service barrier statistics."
    )


class BarrierItem(BaseModel):
    barrier_category: str
    count: int
    percentage_of_barriers: float


class BarrierMetricsResponse(BaseModel):
    total_barrier_events: int
    items: List[BarrierItem]
    is_demo_data: bool
    data_source_note: str


class LanguageMetricItem(BaseModel):
    language_code: str
    language_name: str
    native_name: str
    session_count: int
    barrier_event_count: int


class LanguageMetricsResponse(BaseModel):
    total_languages_represented: int
    items: List[LanguageMetricItem]
    is_demo_data: bool


class FieldMetricItem(BaseModel):
    field_key: str
    scheme_id: int
    scheme_name: str
    issue_count: int
    barrier_breakdown: Dict[str, int]


class FieldMetricsResponse(BaseModel):
    total_problematic_fields: int
    items: List[FieldMetricItem]
    is_demo_data: bool


class RecoveryMetricsResponse(BaseModel):
    total_resolution_attempts: int = Field(
        ..., description="Events where issue_resolved or issue_unresolved was logged"
    )
    resolved_count: int
    unresolved_count: int
    escalated_count: int
    resolution_rate_pct: float = Field(
        ..., description="Numerator: resolved_count / Denominator: total_resolution_attempts (if > 0)"
    )
    is_demo_data: bool
    data_source_note: str


class TranslationLanguageStatus(BaseModel):
    language_code: str
    native_name: str
    approved_count: int
    reviewed_count: int
    draft_count: int
    missing_count: int
    coverage_pct: float


class TranslationQualityResponse(BaseModel):
    total_configured_languages: int
    total_registered_fields: int
    overall_approved_count: int
    overall_reviewed_count: int
    overall_draft_count: int
    overall_missing_count: int
    languages: List[TranslationLanguageStatus]


class StateCoverageItem(BaseModel):
    state_code: str
    state_name: str
    is_ut: bool
    total_schemes: int
    verified_sources: int
    missing_urls: int
    form_available: int
    needs_reverification: int
    official_portal_url: Optional[str] = None
    official_services_url: Optional[str] = None


class NationwideCoverageResponse(BaseModel):
    total_schemes_discovered: int
    central_schemes_count: int
    state_schemes_count: int
    ut_schemes_count: int
    states_represented: int
    uts_represented: int
    all_28_states_covered: bool
    all_8_uts_covered: bool
    verified_sources_count: int
    missing_sources_count: int
    needs_reverification_count: int
    form_status_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    level_breakdown: Dict[str, int]
    state_ut_coverage: List[StateCoverageItem]
    source_feeds_breakdown: Dict[str, int]
    coverage_methodology_disclaimer: str
    summary_note: Optional[str] = None
