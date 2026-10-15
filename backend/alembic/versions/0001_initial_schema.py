"""Initial schema — all six NagrikSaarathi tables

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-10-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── languages ───────────────────────────────────────────────────
    op.create_table(
        "languages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("language_code", sa.String(10), unique=True, nullable=False),
        sa.Column("english_name", sa.String(60), nullable=False),
        sa.Column("native_name", sa.String(100), nullable=False),
        sa.Column("writing_system", sa.String(40), nullable=False),
        sa.Column("direction", sa.String(3), nullable=False, server_default="ltr"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("supports_text", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("supports_speech_recognition", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("supports_text_to_speech", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.CheckConstraint("direction IN ('ltr', 'rtl')", name="ck_language_direction"),
    )

    # ── government_schemes ──────────────────────────────────────────
    op.create_table(
        "government_schemes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(120), unique=True, nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("department_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("official_source_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("source_document_reference", sa.String(500), nullable=True),
        sa.Column("is_demo", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── form_fields ─────────────────────────────────────────────────
    op.create_table(
        "form_fields",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("scheme_id", sa.Integer, sa.ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_key", sa.String(120), nullable=False),
        sa.Column("field_type", sa.String(40), nullable=False, server_default="text"),
        sa.Column("required", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("labels_by_language", sa.JSON, nullable=False),
        sa.Column("explanations_by_language", sa.JSON, nullable=False),
        sa.Column("instructions_by_language", sa.JSON, nullable=False),
        sa.Column("validation_rules", sa.JSON, nullable=False),
        sa.Column("source_reference", sa.String(500), nullable=True),
        sa.UniqueConstraint("scheme_id", "field_key", name="uq_formfield_scheme_field_key"),
    )

    # ── assisted_sessions ───────────────────────────────────────────
    op.create_table(
        "assisted_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scheme_id", sa.Integer, sa.ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_language", sa.String(10), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False, server_default="web"),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("analytics_consent", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("is_demo", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("channel IN ('web', 'assisted_desk')", name="ck_session_channel"),
        sa.CheckConstraint("status IN ('in_progress', 'completed', 'abandoned', 'needs_human_help')", name="ck_session_status"),
    )

    # ── session_events ──────────────────────────────────────────────
    op.create_table(
        "session_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("assisted_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_key", sa.String(120), nullable=True),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("barrier_category", sa.String(40), nullable=True),
        sa.Column("resolution_status", sa.String(20), nullable=True),
        sa.Column("language_code", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "event_type IN ('help_requested','voice_used','validation_failed',"
            "'field_completed','issue_resolved','issue_unresolved',"
            "'application_completed','abandoned','human_help_requested')",
            name="ck_event_type",
        ),
        sa.CheckConstraint(
            "barrier_category IS NULL OR barrier_category IN ("
            "'confusing_question','missing_document','language_difficulty',"
            "'validation_error','technical_failure','other')",
            name="ck_barrier_category",
        ),
        sa.CheckConstraint(
            "resolution_status IS NULL OR resolution_status IN ("
            "'resolved','unresolved','escalated')",
            name="ck_resolution_status",
        ),
    )

    # ── translation_reviews ─────────────────────────────────────────
    op.create_table(
        "translation_reviews",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resource_type", sa.String(60), nullable=False),
        sa.Column("resource_key", sa.String(200), nullable=False),
        sa.Column("language_code", sa.String(10), nullable=False),
        sa.Column("translation_status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("reviewer_note", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("resource_type", "resource_key", "language_code", name="uq_translation_review_resource_lang"),
        sa.CheckConstraint("translation_status IN ('draft', 'reviewed', 'approved')", name="ck_translation_status"),
    )


def downgrade() -> None:
    op.drop_table("translation_reviews")
    op.drop_table("session_events")
    op.drop_table("assisted_sessions")
    op.drop_table("form_fields")
    op.drop_table("government_schemes")
    op.drop_table("languages")
