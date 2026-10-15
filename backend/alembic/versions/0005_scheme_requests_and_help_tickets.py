"""Add scheme_requests, help_tickets tables and benefit_details, user preferences

Revision ID: 0005_requests_and_tickets
Revises: 0004_nationwide_ingestion
Create Date: 2026-10-14

Adds:
- benefit_details JSON column to government_schemes
- preferred_language & accessibility_settings to users
- scheme_requests table with tracking IDs and full review lifecycle
- help_tickets table with ticket numbers, resolution and feedback loop
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0005_requests_and_tickets"
down_revision = "0004_nationwide_ingestion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extend government_schemes with benefit_details
    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.add_column(
            sa.Column("benefit_details", sa.JSON(), nullable=False, server_default="{}")
        )

    # 2. Extend users with preferred_language and accessibility_settings
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("preferred_language", sa.String(10), nullable=True, server_default="en")
        )
        batch_op.add_column(
            sa.Column("accessibility_settings", sa.JSON(), nullable=False, server_default='{"fontScale": 1, "highContrast": false}')
        )

    # 3. Create scheme_requests table
    op.create_table(
        "scheme_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tracking_id", sa.String(40), unique=True, index=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citizen_contact", sa.String(120), nullable=True),
        sa.Column("scheme_name", sa.String(250), nullable=False),
        sa.Column("government_level", sa.String(20), nullable=False, server_default="central"),
        sa.Column("state_code", sa.String(10), nullable=True),
        sa.Column("department_name", sa.String(250), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("official_portal_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(40), nullable=False, server_default="Request Received"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("linked_scheme_id", sa.Integer(), sa.ForeignKey("government_schemes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Create help_tickets table
    op.create_table(
        "help_tickets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ticket_number", sa.String(40), unique=True, index=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citizen_name", sa.String(120), nullable=True),
        sa.Column("citizen_contact", sa.String(120), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(250), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("page_or_scheme_ref", sa.String(250), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="Received"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("resolution_message", sa.Text(), nullable=True),
        sa.Column("satisfaction_solved", sa.Boolean(), nullable=True),
        sa.Column("feedback_notes", sa.Text(), nullable=True),
        sa.Column("reopen_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("history", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("help_tickets")
    op.drop_table("scheme_requests")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("accessibility_settings")
        batch_op.drop_column("preferred_language")
    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.drop_column("benefit_details")
