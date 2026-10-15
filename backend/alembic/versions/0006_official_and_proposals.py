"""Add department official management, scheme proposals, and admin audit logs

Revision ID: 0006_official_and_proposals
Revises: 0005_requests_and_tickets
Create Date: 2026-10-14

Adds:
- users table extension: state_scope, designation, assigned_by_id
- departments table
- scheme_proposals table with full multi-stage lifecycle (draft -> submitted -> under_review -> revision_required -> approved -> rejected)
- admin_audit_logs table for administrative accountability
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "0006_official_and_proposals"
down_revision = "0005_requests_and_tickets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extend users table
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("state_scope", sa.String(10), nullable=True))
        batch_op.add_column(sa.Column("designation", sa.String(120), nullable=True))
        batch_op.add_column(sa.Column("assigned_by_id", sa.Integer(), nullable=True))

    # 2. Create departments table
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(250), unique=True, index=True, nullable=False),
        sa.Column("ministry_name", sa.String(250), nullable=True),
        sa.Column("government_level", sa.String(20), nullable=False, server_default="central"),
        sa.Column("state_code", sa.String(10), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 3. Create scheme_proposals table
    op.create_table(
        "scheme_proposals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("proposal_number", sa.String(40), unique=True, index=True, nullable=False),
        sa.Column("proposal_type", sa.String(30), nullable=False, server_default="new_scheme"),
        sa.Column("scheme_id", sa.Integer(), sa.ForeignKey("government_schemes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("official_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_name", sa.String(250), nullable=False),
        sa.Column("state_code", sa.String(10), nullable=True),
        sa.Column("government_level", sa.String(20), nullable=False, server_default="central"),
        sa.Column("scheme_name", sa.String(250), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(40), nullable=False, server_default="welfare"),
        sa.Column("benefit_summary", sa.Text(), nullable=True),
        sa.Column("benefit_details", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("eligibility_criteria", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("document_requirements", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("application_instructions", sa.Text(), nullable=True),
        sa.Column("official_source_url", sa.String(500), nullable=True),
        sa.Column("official_application_url", sa.String(500), nullable=True),
        sa.Column("source_evidence", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="submitted"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("revision_requested_notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Create admin_audit_logs table
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_identifier", sa.String(120), nullable=False),
        sa.Column("user_role", sa.String(20), nullable=False),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("resource_type", sa.String(60), nullable=False),
        sa.Column("resource_id", sa.String(60), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("scheme_proposals")
    op.drop_table("departments")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("assigned_by_id")
        batch_op.drop_column("designation")
        batch_op.drop_column("state_scope")
