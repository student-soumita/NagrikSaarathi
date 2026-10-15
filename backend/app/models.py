"""
NagrikSaarathi — SQLAlchemy ORM Models (canonical schema)

Privacy invariants
------------------
* **AssistedSession** and **SessionEvent** never store citizen form
  answers, uploaded documents, names, phone numbers, addresses,
  identity numbers, bank details, passwords, or raw voice recordings.
* Analytics records are created only after explicit consent.
* Every demo row carries ``is_demo=True`` so it can never be confused
  with real public-sector data.
* Guided Self-Application mode runs completely client-side in browser memory
  without persisting citizen responses or requiring mandatory account registration.

Model hierarchy
---------------
Language
GovernmentScheme ──▸ FormField
                 ──▸ SchemeEligibilityRequirement
                 ──▸ SchemeDocumentRequirement
                 ──▸ SchemeApplicationStep
AssistedSession  ──▸ SessionEvent
TranslationReview
User
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ── Base ────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Shared declarative base for every model."""
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums & Constants ───────────────────────────────────────────────────

SESSION_STATUSES = ("in_progress", "completed", "abandoned", "needs_human_help")
CHANNELS = ("web", "assisted_desk")
DIRECTIONS = ("ltr", "rtl")
TRANSLATION_STATUSES = ("draft", "reviewed", "approved")
VERIFICATION_STATUSES = ("verified", "pending_review", "outdated")

CRITERION_TYPES = (
    "age",
    "annual_income",
    "academic_qualification",
    "domicile_residency",
    "social_category",
    "gender",
    "institutional_enrollment",
    "other",
)

DOCUMENT_REQUIREMENT_TYPES = ("always_required", "conditional", "optional")

EVENT_TYPES = (
    "help_requested",
    "voice_used",
    "validation_failed",
    "field_completed",
    "issue_resolved",
    "issue_unresolved",
    "application_completed",
    "abandoned",
    "human_help_requested",
)
BARRIER_CATEGORIES = (
    "confusing_question",
    "missing_document",
    "language_difficulty",
    "validation_error",
    "technical_failure",
    "other",
)
RESOLUTION_STATUSES = ("resolved", "unresolved", "escalated")

SCHEDULED_LANGUAGES_22 = (
    "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok",
    "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
    "sd", "ta", "te", "ur"
)

SCHEME_REQUEST_STATUSES = (
    "Request Received",
    "Under Review",
    "Information Needed",
    "Verified",
    "Added to Catalogue",
    "Already Exists",
    "Rejected",
    "Unable to Verify",
)

HELP_TICKET_STATUSES = (
    "Received",
    "Open",
    "In Progress",
    "Waiting for Citizen",
    "Resolved",
    "Closed",
)

HELP_TICKET_CATEGORIES = (
    "translation",
    "guided_form_difficulty",
    "eligibility_confusion",
    "missing_scheme",
    "incorrect_official_link",
    "technical_error",
    "other",
)


# ── Language ────────────────────────────────────────────────────────────

class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    english_name: Mapped[str] = mapped_column(String(60), nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), nullable=False)
    writing_system: Mapped[str] = mapped_column(String(40), nullable=False)
    direction: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("direction IN ('ltr', 'rtl')", name="ck_language_direction"),
        nullable=False,
        default="ltr",
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    supports_text: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    supports_speech_recognition: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_text_to_speech: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<Language {self.language_code!r} ({self.english_name})>"


# ── GovernmentScheme ────────────────────────────────────────────────────

class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    department_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    official_source_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    source_document_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Catalogue / Classification Fields ─────────────────────────────────
    # Government level: central, state, ut (Union Territory), local
    government_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="central"
    )
    # ISO 3166-2:IN state/UT code, e.g. "MH", "WB", "DL" (null for central)
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    # Scheme category
    category: Mapped[str] = mapped_column(
        String(40), nullable=False, default="other"
    )
    # Intended beneficiary groups as a JSON list, e.g. ["women", "students", "farmers"]
    beneficiary_groups: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # How the application is submitted
    application_method: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unknown"
    )
    # What NagrikSaarathi can actually do for this scheme
    # DISCOVERY_ONLY | GUIDED_PREPARATION | DRAFT_EXPORT | AUTHORISED_PREFILL | AUTHORISED_SUBMISSION
    portal_capability: Mapped[str] = mapped_column(
        String(40), nullable=False, default="GUIDED_PREPARATION"
    )
    # Search keywords as a JSON list for full-text-style search
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Scheme lifecycle status: active, inactive, expired, unknown
    scheme_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    # True for citizen-uploaded / machine-extracted candidate forms (unverified)
    is_candidate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Minimum age / max age (nullable, for eligibility pre-check hints)
    min_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Nationwide Ingestion & Canonical Identification ───────────────────
    # Canonical nationwide identifier e.g. "IN-CEN-AGRI-PMKISAN"
    canonical_id: Mapped[Optional[str]] = mapped_column(String(120), unique=True, nullable=True, index=True)
    # Alternative names, aliases, vernacular names, and acronyms as a JSON list
    alternate_names: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Ministry / Parent administrative entity
    ministry_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Implementing nodal agency / directorate / board / mission
    nodal_agency: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Source feed classification
    # MYSCHEME_DATASET | INDIA_GOV_PORTAL | STATE_PORTAL | ADMIN_IMPORT | CITIZEN_SUBMISSION | MANUAL_VERIFIED
    source_feed_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="OFFICIAL_PORTAL"
    )
    # Availability status of application form schema
    # VERIFIED_SCHEMA | EXTRACTED_DRAFT | EXTERNAL_LINK_ONLY | NO_FORM
    form_status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="VERIFIED_SCHEMA"
    )
    # Date when details were last re-checked from official notification
    last_reverified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reverification_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Raw extracted form text / schema definitions for uncatalogued/extracted forms
    extracted_form_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Guided Self-Application Capabilities
    official_application_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated')",
            name="ck_scheme_verification_status",
        ),
        nullable=False,
        default="verified",
    )
    verification_source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    descriptions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    application_instructions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    benefit_details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Relationships
    fields: Mapped[list["FormField"]] = relationship(
        back_populates="scheme",
        cascade="all, delete-orphan",
        order_by="FormField.sort_order",
    )
    eligibility_requirements: Mapped[list["SchemeEligibilityRequirement"]] = relationship(
        back_populates="scheme",
        cascade="all, delete-orphan",
        order_by="SchemeEligibilityRequirement.sort_order",
    )
    document_requirements: Mapped[list["SchemeDocumentRequirement"]] = relationship(
        back_populates="scheme",
        cascade="all, delete-orphan",
        order_by="SchemeDocumentRequirement.sort_order",
    )
    application_steps: Mapped[list["SchemeApplicationStep"]] = relationship(
        back_populates="scheme",
        cascade="all, delete-orphan",
        order_by="SchemeApplicationStep.step_number",
    )

    @property
    def is_verified(self) -> bool:
        """Returns True if this scheme has verified official information."""
        return self.verification_status == "verified"

    def missing_languages(self, expected_languages: Sequence[str] = SCHEDULED_LANGUAGES_22) -> list[str]:
        """Detect missing translations in scheme description/instructions."""
        missing = []
        for code in expected_languages:
            has_desc = bool(self.descriptions_by_language.get(code))
            if not has_desc:
                missing.append(code)
        return missing

    def __repr__(self) -> str:
        return f"<GovernmentScheme {self.slug!r} level={self.government_level!r} category={self.category!r}>"



# ── FormField ───────────────────────────────────────────────────────────

class FormField(Base):
    __tablename__ = "form_fields"
    __table_args__ = (
        UniqueConstraint("scheme_id", "field_key", name="uq_formfield_scheme_field_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("government_schemes.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_key: Mapped[str] = mapped_column(String(120), nullable=False)
    field_type: Mapped[str] = mapped_column(String(40), nullable=False, default="text")
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Localized content — JSON dicts keyed by language_code
    labels_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    explanations_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    instructions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Guided Self-Application Extensions
    examples_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    validation_guidance_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated')",
            name="ck_formfield_verification_status",
        ),
        nullable=False,
        default="verified",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    validation_rules: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    scheme: Mapped["GovernmentScheme"] = relationship(back_populates="fields")

    def missing_languages(self, expected_languages: Sequence[str] = SCHEDULED_LANGUAGES_22) -> list[str]:
        """Detect missing label or explanation translations."""
        missing = []
        for code in expected_languages:
            if not self.labels_by_language.get(code) or not self.explanations_by_language.get(code):
                missing.append(code)
        return missing

    def __repr__(self) -> str:
        return f"<FormField {self.field_key!r} (scheme_id={self.scheme_id})>"


# ── SchemeEligibilityRequirement ────────────────────────────────────────

class SchemeEligibilityRequirement(Base):
    """
    Structured eligibility requirement for a scheme.
    Not merely unstructured AI-generated text; captures typed criteria,
    operators, thresholds, source citations, and verification status.
    """
    __tablename__ = "scheme_eligibility_requirements"
    __table_args__ = (
        UniqueConstraint("scheme_id", "criterion_key", name="uq_eligibility_scheme_criterion"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("government_schemes.id", ondelete="CASCADE"),
        nullable=False,
    )
    criterion_key: Mapped[str] = mapped_column(String(100), nullable=False)
    criterion_type: Mapped[str] = mapped_column(
        String(40),
        CheckConstraint(
            "criterion_type IN ("
            "'age','annual_income','academic_qualification',"
            "'domicile_residency','social_category','gender','institutional_enrollment','other'"
            ")",
            name="ck_eligibility_criterion_type",
        ),
        nullable=False,
        default="other",
    )
    operator: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    threshold_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Localized summaries and explanations (22 scheduled Indian languages)
    titles_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    descriptions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    official_source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated')",
            name="ck_eligibility_verification_status",
        ),
        nullable=False,
        default="verified",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    scheme: Mapped["GovernmentScheme"] = relationship(back_populates="eligibility_requirements")

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"

    def missing_languages(self, expected_languages: Sequence[str] = SCHEDULED_LANGUAGES_22) -> list[str]:
        missing = []
        for code in expected_languages:
            if not self.titles_by_language.get(code):
                missing.append(code)
        return missing

    def __repr__(self) -> str:
        return f"<SchemeEligibilityRequirement {self.criterion_key!r} scheme_id={self.scheme_id}>"


# ── SchemeDocumentRequirement ───────────────────────────────────────────

class SchemeDocumentRequirement(Base):
    """
    Required or conditional document specification for a government scheme.
    Stores structured condition rules (e.g. required only if income or category meets condition),
    issuing authorities, validity info, and verification metadata.
    """
    __tablename__ = "scheme_document_requirements"
    __table_args__ = (
        UniqueConstraint("scheme_id", "document_code", name="uq_document_scheme_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("government_schemes.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_code: Mapped[str] = mapped_column(String(100), nullable=False)
    requirement_type: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint(
            "requirement_type IN ('always_required', 'conditional', 'optional')",
            name="ck_doc_requirement_type",
        ),
        nullable=False,
        default="always_required",
    )
    # Structured condition rule when requirement_type == 'conditional'
    condition_rule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Localized document names and explanations
    titles_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    descriptions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    issuing_authority: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    validity_period_info: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    official_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated')",
            name="ck_document_verification_status",
        ),
        nullable=False,
        default="verified",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    scheme: Mapped["GovernmentScheme"] = relationship(back_populates="document_requirements")

    @property
    def is_conditional(self) -> bool:
        return self.requirement_type == "conditional"

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"

    def missing_languages(self, expected_languages: Sequence[str] = SCHEDULED_LANGUAGES_22) -> list[str]:
        missing = []
        for code in expected_languages:
            if not self.titles_by_language.get(code):
                missing.append(code)
        return missing

    def __repr__(self) -> str:
        return f"<SchemeDocumentRequirement {self.document_code!r} ({self.requirement_type})>"


# ── SchemeApplicationStep ───────────────────────────────────────────────

class SchemeApplicationStep(Base):
    """
    Step-by-step application instructions for guided self-application.
    Numbered sequential steps with localized instructions and action URLs.
    """
    __tablename__ = "scheme_application_steps"
    __table_args__ = (
        UniqueConstraint("scheme_id", "step_number", name="uq_step_scheme_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("government_schemes.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_key: Mapped[str] = mapped_column(String(100), nullable=False)

    titles_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    instructions_by_language: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    official_action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated')",
            name="ck_step_verification_status",
        ),
        nullable=False,
        default="verified",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    scheme: Mapped["GovernmentScheme"] = relationship(back_populates="application_steps")

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"

    def missing_languages(self, expected_languages: Sequence[str] = SCHEDULED_LANGUAGES_22) -> list[str]:
        missing = []
        for code in expected_languages:
            if not self.titles_by_language.get(code):
                missing.append(code)
        return missing

    def __repr__(self) -> str:
        return f"<SchemeApplicationStep step {self.step_number} ({self.step_key!r})>"


# ── AssistedSession ────────────────────────────────────────────────────
# PRIVACY: This table intentionally has NO columns for citizen PII,
# form answers, or uploaded documents. Guided Self-Application answers
# stay strictly in client-side memory.

class AssistedSession(Base):
    __tablename__ = "assisted_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    scheme_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("government_schemes.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_language: Mapped[str] = mapped_column(String(10), nullable=False)
    channel: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "channel IN ('web', 'assisted_desk')",
            name="ck_session_channel",
        ),
        nullable=False,
        default="web",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned', 'needs_human_help')",
            name="ck_session_status",
        ),
        nullable=False,
        default="in_progress",
    )
    analytics_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    events: Mapped[list["SessionEvent"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionEvent.created_at",
    )

    def __repr__(self) -> str:
        return f"<AssistedSession {self.id} status={self.status!r}>"


# ── SessionEvent ────────────────────────────────────────────────────────
# PRIVACY: This table records structured event types only.
# It NEVER stores the actual values or documents a citizen inputs.

class SessionEvent(Base):
    __tablename__ = "session_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assisted_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_key: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    event_type: Mapped[str] = mapped_column(
        String(40),
        CheckConstraint(
            "event_type IN ("
            "'help_requested','voice_used','validation_failed',"
            "'field_completed','issue_resolved','issue_unresolved',"
            "'application_completed','abandoned','human_help_requested'"
            ")",
            name="ck_event_type",
        ),
        nullable=False,
    )
    barrier_category: Mapped[Optional[str]] = mapped_column(
        String(40),
        CheckConstraint(
            "barrier_category IS NULL OR barrier_category IN ("
            "'confusing_question','missing_document','language_difficulty',"
            "'validation_error','technical_failure','other'"
            ")",
            name="ck_barrier_category",
        ),
        nullable=True,
    )
    resolution_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        CheckConstraint(
            "resolution_status IS NULL OR resolution_status IN ("
            "'resolved','unresolved','escalated'"
            ")",
            name="ck_resolution_status",
        ),
        nullable=True,
    )
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    session: Mapped["AssistedSession"] = relationship(back_populates="events")

    def __repr__(self) -> str:
        return f"<SessionEvent {self.event_type!r} session={self.session_id}>"


# ── TranslationReview ──────────────────────────────────────────────────

class TranslationReview(Base):
    __tablename__ = "translation_reviews"
    __table_args__ = (
        UniqueConstraint(
            "resource_type", "resource_key", "language_code",
            name="uq_translation_review_resource_lang",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_type: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_key: Mapped[str] = mapped_column(String(200), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    translation_status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "translation_status IN ('draft', 'reviewed', 'approved')",
            name="ck_translation_status",
        ),
        nullable=False,
        default="draft",
    )
    reviewer_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<TranslationReview {self.resource_type}:{self.resource_key} "
            f"lang={self.language_code!r} status={self.translation_status!r}>"
        )


# ── TranslationCache ───────────────────────────────────────────────────

class TranslationCache(Base):
    """
    Persistent cache for dynamic translation of government scheme descriptions,
    benefits, eligibility criteria, document checklists, and application steps.
    Keyed by content hash and target language to guarantee idempotency, avoid repeat API
    costs/timeouts, and preserve exact translated versions.
    """
    __tablename__ = "translation_caches"
    __table_args__ = (
        UniqueConstraint(
            "content_hash", "target_language",
            name="uq_translation_cache_hash_lang",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    target_language: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    provider_used: Mapped[str] = mapped_column(String(40), nullable=False, default="dataset")
    is_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<TranslationCache {self.content_hash[:8]}... "
            f"{self.source_language}->{self.target_language} provider={self.provider_used}>"
        )


PROPOSAL_TYPES = ("new_scheme", "metadata_update", "url_correction", "eligibility_update")
PROPOSAL_STATUSES = ("draft", "submitted", "under_review", "revision_required", "approved", "rejected")


# ── Department ──────────────────────────────────────────────────────────

class Department(Base):
    """Canonical registry of government ministries, departments, and directorates."""
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, index=True, nullable=False)
    ministry_name: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    government_level: Mapped[str] = mapped_column(String(20), nullable=False, default="central")
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r} level={self.government_level!r}>"


# ── User (Authentication & Role-Based Access Control) ───────────────────

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('citizen', 'official', 'admin')", name="ck_user_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identifier: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="citizen")
    full_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    state_scope: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="en")
    accessibility_settings: Mapped[dict] = mapped_column(JSON, nullable=False, default=lambda: {"fontScale": 1, "highContrast": False})
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_by: Mapped[Optional["User"]] = relationship(remote_side="User.id")

    def __repr__(self) -> str:
        return f"<User id={self.id} identifier={self.identifier!r} role={self.role!r} dept={self.department!r}>"


# ── SchemeProposal (Department Official Change Proposals) ───────────────

class SchemeProposal(Base):
    """
    Structured proposals submitted by Department Officials for new schemes,
    metadata updates, eligibility rule modifications, or URL authority corrections.
    Undergoes Principal Administrator multi-stage review before publication.
    """
    __tablename__ = "scheme_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    proposal_type: Mapped[str] = mapped_column(String(30), nullable=False, default="new_scheme")
    scheme_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("government_schemes.id", ondelete="SET NULL"), nullable=True)
    official_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_name: Mapped[str] = mapped_column(String(250), nullable=False)
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    government_level: Mapped[str] = mapped_column(String(20), nullable=False, default="central")
    scheme_name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="welfare")
    benefit_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefit_details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    eligibility_criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    document_requirements: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    application_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    official_application_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="submitted")
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    revision_requested_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    official: Mapped["User"] = relationship(foreign_keys=[official_id])
    reviewed_by: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by_id])
    scheme: Mapped[Optional["GovernmentScheme"]] = relationship()

    def __repr__(self) -> str:
        return f"<SchemeProposal {self.proposal_number!r} status={self.status!r} dept={self.department_name!r}>"


# ── AdminAuditLog (Administrative Accountability & Governance) ──────────

class AdminAuditLog(Base):
    """
    Immutable audit log of all administrative actions, proposal reviews,
    scheme publications, and role assignments.
    """
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_identifier: Mapped[str] = mapped_column(String(120), nullable=False)
    user_role: Mapped[str] = mapped_column(String(20), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    user: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<AdminAuditLog actor={self.user_identifier!r} action={self.action!r} target={self.resource_type}:{self.resource_id}>"


# ── IngestionAuditLog (Nationwide Ingestion & Verification Tracking) ────

class IngestionAuditLog(Base):
    """
    Audit and provenance record of automated or administrative scheme imports.
    Tracks exact counts of new, updated, duplicate, and rejected records.
    """
    __tablename__ = "ingestion_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    records_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_duplicates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SUCCESS")
    summary_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<IngestionAuditLog id={self.id} source={self.source_name!r} status={self.status!r}>"


# ── SchemeRequest (Trackable Citizen Missing-Scheme Submissions) ──────────

class SchemeRequest(Base):
    __tablename__ = "scheme_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tracking_id: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    citizen_contact: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    scheme_name: Mapped[str] = mapped_column(String(250), nullable=False)
    government_level: Mapped[str] = mapped_column(String(20), nullable=False, default="central")
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    department_name: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_portal_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="Request Received")
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linked_scheme_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("government_schemes.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["User"]] = relationship()
    linked_scheme: Mapped[Optional["GovernmentScheme"]] = relationship()

    def __repr__(self) -> str:
        return f"<SchemeRequest {self.tracking_id!r} status={self.status!r}>"


# ── HelpTicket (Structured Citizen Help & Support Queue) ─────────────────

class HelpTicket(Base):
    __tablename__ = "help_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    citizen_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    citizen_contact: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    page_or_scheme_ref: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Received")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    satisfaction_solved: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    history: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<HelpTicket {self.ticket_number!r} status={self.status!r}>"


# ── OfficialInvitation (Controlled Official Onboarding) ──────────────────

class OfficialInvitation(Base):
    """
    Principal Administrator-controlled invitation for prospective Department Officials.
    Enforces cryptographic single-use expiring tokens, department & geographic scope,
    permissions, and explicit administrative review/approval before activation.
    """
    __tablename__ = "official_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invitation_token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    department: Mapped[str] = mapped_column(String(200), nullable=False)
    state_scope: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    allowed_permissions: Mapped[list] = mapped_column(JSON, nullable=False, default=lambda: ["proposals", "evidence_review", "diff_radar"])
    invited_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint(
            "status IN ('pending_activation', 'pending_approval', 'activated', 'expired', 'revoked')",
            name="ck_invitation_status",
        ),
        nullable=False,
        default="pending_activation",
    )
    verification_method: Mapped[str] = mapped_column(String(60), nullable=False, default="MANUAL_ADMIN_REVIEW")
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    invited_by: Mapped["User"] = relationship(foreign_keys=[invited_by_id])
    approved_by: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by_id])
    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<OfficialInvitation {self.email!r} dept={self.department!r} status={self.status!r}>"


# ── SchemeChangeRadarRecord (Rule Change Radar) ──────────────────────────

class SchemeChangeRadarRecord(Base):
    """
    Scheme Rule Change Radar:
    Maintains official source document comparisons, diff extraction (eligibility, benefits,
    documents, exclusions, deadlines, official URLs), draft change sets, supporting citations,
    and review/publication lifecycle with version history snapshots.
    """
    __tablename__ = "scheme_change_radar_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    radar_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_title: Mapped[str] = mapped_column(String(250), nullable=False)
    source_version: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    source_document_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_publication_date: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    submitted_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'under_review', 'revision_required', 'approved', 'published', 'rejected')",
            name="ck_radar_status",
        ),
        nullable=False,
        default="draft",
    )
    detected_changes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    diff_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    uncertain_flags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    previous_scheme_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    scheme: Mapped["GovernmentScheme"] = relationship()
    submitted_by: Mapped["User"] = relationship(foreign_keys=[submitted_by_id])
    reviewed_by: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by_id])

    def __repr__(self) -> str:
        return f"<SchemeChangeRadarRecord {self.radar_code!r} scheme_id={self.scheme_id} status={self.status!r}>"


# ── SchemeFieldEvidence (Evidence-Linked Scheme Editor) ──────────────────

class SchemeFieldEvidence(Base):
    """
    Evidence-Linked Scheme Editor:
    Stores traceable official evidence for factual scheme fields:
    eligibility, benefits, exclusions, documents, application instructions, official URLs.
    Includes supporting quotations, page/section references, and verification status.
    """
    __tablename__ = "scheme_field_evidences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)
    field_category: Mapped[str] = mapped_column(
        String(40),
        CheckConstraint(
            "field_category IN ('eligibility', 'benefit', 'exclusion', 'document', 'application_step', 'official_url')",
            name="ck_evidence_category",
        ),
        nullable=False,
    )
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    field_label: Mapped[str] = mapped_column(String(200), nullable=False)
    claim_value: Mapped[str] = mapped_column(Text, nullable=False)
    official_source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_title: Mapped[str] = mapped_column(String(250), nullable=False)
    responsible_department: Mapped[str] = mapped_column(String(250), nullable=False)
    supporting_quotation: Mapped[str] = mapped_column(Text, nullable=False)
    document_page_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint(
            "verification_status IN ('verified', 'pending_review', 'outdated', 'broken_url', 'unverified', 'conflicting')",
            name="ck_field_evidence_status",
        ),
        nullable=False,
        default="pending_review",
    )
    reviewer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_source_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    scheme: Mapped["GovernmentScheme"] = relationship()
    reviewer: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<SchemeFieldEvidence id={self.id} field={self.field_key!r} status={self.verification_status!r}>"


# ── TranslationDriftAlert (Translation Drift Monitor) ────────────────────

class TranslationDriftAlert(Base):
    """
    Translation Drift Monitor:
    Tracks when approved scheme modifications cause translation drift across
    the 22 Eighth Schedule languages. Enables side-by-side comparison, machine/human review
    state separation, and approval tracking.
    """
    __tablename__ = "translation_drift_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    previous_source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_source_text: Mapped[str] = mapped_column(Text, nullable=False)
    existing_translated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_translated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    drift_status: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint(
            "drift_status IN ('drift_detected', 'in_review', 'verified_human', 'approved', 'dismissed')",
            name="ck_drift_status",
        ),
        nullable=False,
        default="drift_detected",
    )
    translation_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="machine_draft")
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    scheme: Mapped["GovernmentScheme"] = relationship()
    reviewed_by: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<TranslationDriftAlert id={self.id} scheme_id={self.scheme_id} lang={self.target_language} status={self.drift_status!r}>"

