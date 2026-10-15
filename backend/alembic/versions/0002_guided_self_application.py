"""Guided Self-Application Mode — Database schema extensions

Revision ID: 0002_guided_self_application
Revises: 0001_initial_schema
Create Date: 2026-10-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_guided_self_application"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ── 1. users table (if not already created) ────────────────────────
    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("identifier", sa.String(120), unique=True, index=True, nullable=False),
            sa.Column("email", sa.String(120), nullable=True),
            sa.Column("mobile", sa.String(20), nullable=True),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column("role", sa.String(20), nullable=False, server_default="citizen"),
            sa.Column("full_name", sa.String(120), nullable=True),
            sa.Column("department", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("is_demo", sa.Boolean, nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
            sa.CheckConstraint("role IN ('citizen', 'official')", name="ck_user_role"),
        )

    # ── 2. Extend government_schemes ───────────────────────────────────
    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.add_column(
            sa.Column("official_application_url", sa.String(500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "verification_status",
                sa.String(20),
                nullable=False,
                server_default="verified",
            )
        )
        batch_op.add_column(
            sa.Column("verification_source_reference", sa.String(500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("descriptions_by_language", sa.JSON, nullable=False, server_default="{}")
        )
        batch_op.add_column(
            sa.Column("application_instructions_by_language", sa.JSON, nullable=False, server_default="{}")
        )

    # ── 3. Extend form_fields ──────────────────────────────────────────
    with op.batch_alter_table("form_fields") as batch_op:
        batch_op.add_column(
            sa.Column("examples_by_language", sa.JSON, nullable=False, server_default="{}")
        )
        batch_op.add_column(
            sa.Column("validation_guidance_by_language", sa.JSON, nullable=False, server_default="{}")
        )
        batch_op.add_column(
            sa.Column(
                "verification_status",
                sa.String(20),
                nullable=False,
                server_default="verified",
            )
        )
        batch_op.add_column(
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True)
        )

    # ── 4. scheme_eligibility_requirements ─────────────────────────────
    if "scheme_eligibility_requirements" not in existing_tables:
        op.create_table(
            "scheme_eligibility_requirements",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column(
                "scheme_id",
                sa.Integer,
                sa.ForeignKey("government_schemes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("criterion_key", sa.String(100), nullable=False),
            sa.Column("criterion_type", sa.String(40), nullable=False, server_default="other"),
            sa.Column("operator", sa.String(20), nullable=True),
            sa.Column("threshold_value", sa.JSON, nullable=True),
            sa.Column("is_mandatory", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
            sa.Column("titles_by_language", sa.JSON, nullable=False),
            sa.Column("descriptions_by_language", sa.JSON, nullable=False),
            sa.Column("official_source_reference", sa.String(500), nullable=True),
            sa.Column(
                "verification_status",
                sa.String(20),
                nullable=False,
                server_default="verified",
            ),
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("scheme_id", "criterion_key", name="uq_eligibility_scheme_criterion"),
            sa.CheckConstraint(
                "verification_status IN ('verified', 'pending_review', 'outdated')",
                name="ck_eligibility_verification_status",
            ),
        )

    # ── 5. scheme_document_requirements ────────────────────────────────
    if "scheme_document_requirements" not in existing_tables:
        op.create_table(
            "scheme_document_requirements",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column(
                "scheme_id",
                sa.Integer,
                sa.ForeignKey("government_schemes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("document_code", sa.String(100), nullable=False),
            sa.Column("requirement_type", sa.String(30), nullable=False, server_default="always_required"),
            sa.Column("condition_rule", sa.JSON, nullable=True),
            sa.Column("is_mandatory", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
            sa.Column("titles_by_language", sa.JSON, nullable=False),
            sa.Column("descriptions_by_language", sa.JSON, nullable=False),
            sa.Column("issuing_authority", sa.String(250), nullable=True),
            sa.Column("validity_period_info", sa.String(250), nullable=True),
            sa.Column("official_source_url", sa.String(500), nullable=True),
            sa.Column("source_reference", sa.String(500), nullable=True),
            sa.Column(
                "verification_status",
                sa.String(20),
                nullable=False,
                server_default="verified",
            ),
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("scheme_id", "document_code", name="uq_document_scheme_code"),
            sa.CheckConstraint(
                "requirement_type IN ('always_required', 'conditional', 'optional')",
                name="ck_doc_requirement_type",
            ),
            sa.CheckConstraint(
                "verification_status IN ('verified', 'pending_review', 'outdated')",
                name="ck_document_verification_status",
            ),
        )

    # ── 6. scheme_application_steps ────────────────────────────────────
    if "scheme_application_steps" not in existing_tables:
        op.create_table(
            "scheme_application_steps",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column(
                "scheme_id",
                sa.Integer,
                sa.ForeignKey("government_schemes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("step_number", sa.Integer, nullable=False),
            sa.Column("step_key", sa.String(100), nullable=False),
            sa.Column("titles_by_language", sa.JSON, nullable=False),
            sa.Column("instructions_by_language", sa.JSON, nullable=False),
            sa.Column("official_action_url", sa.String(500), nullable=True),
            sa.Column("source_reference", sa.String(500), nullable=True),
            sa.Column(
                "verification_status",
                sa.String(20),
                nullable=False,
                server_default="verified",
            ),
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("scheme_id", "step_number", name="uq_step_scheme_number"),
            sa.CheckConstraint(
                "verification_status IN ('verified', 'pending_review', 'outdated')",
                name="ck_step_verification_status",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "scheme_application_steps" in existing_tables:
        op.drop_table("scheme_application_steps")
    if "scheme_document_requirements" in existing_tables:
        op.drop_table("scheme_document_requirements")
    if "scheme_eligibility_requirements" in existing_tables:
        op.drop_table("scheme_eligibility_requirements")

    with op.batch_alter_table("form_fields") as batch_op:
        batch_op.drop_column("last_verified_at")
        batch_op.drop_column("verification_status")
        batch_op.drop_column("validation_guidance_by_language")
        batch_op.drop_column("examples_by_language")

    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.drop_column("application_instructions_by_language")
        batch_op.drop_column("descriptions_by_language")
        batch_op.drop_column("verification_source_reference")
        batch_op.drop_column("verification_status")
        batch_op.drop_column("last_verified_at")
        batch_op.drop_column("official_application_url")

    if "users" in existing_tables:
        op.drop_table("users")
