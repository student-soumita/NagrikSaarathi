"""Add nationwide ingestion and gap tracking fields and audit table

Revision ID: 0004_nationwide_ingestion
Revises: 0003_scheme_catalogue
Create Date: 2026-10-12

Adds canonical identifiers, alternate names, ministry, agency, form status,
reverification timestamps, and creates the ingestion_audit_logs table.
All new columns have safe defaults for backward compatibility.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0004_nationwide_ingestion"
down_revision = "0003_scheme_catalogue"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extend government_schemes
    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.add_column(
            sa.Column("canonical_id", sa.String(120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("alternate_names", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("ministry_name", sa.String(200), nullable=True)
        )
        batch_op.add_column(
            sa.Column("nodal_agency", sa.String(200), nullable=True)
        )
        batch_op.add_column(
            sa.Column("source_feed_type", sa.String(50), nullable=False, server_default="OFFICIAL_PORTAL")
        )
        batch_op.add_column(
            sa.Column("form_status", sa.String(40), nullable=False, server_default="VERIFIED_SCHEMA")
        )
        batch_op.add_column(
            sa.Column("last_reverified_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("reverification_notes", sa.String(500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("extracted_form_raw", sa.Text(), nullable=True)
        )

    # 2. Create ingestion_audit_logs table
    op.create_table(
        "ingestion_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_name", sa.String(120), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("records_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_duplicates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_rejected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="SUCCESS"),
        sa.Column("summary_notes", sa.Text(), nullable=True),
        sa.Column("error_log", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ingestion_audit_logs")
    with op.batch_alter_table("government_schemes") as batch_op:
        for col in [
            "extracted_form_raw",
            "reverification_notes",
            "last_reverified_at",
            "form_status",
            "source_feed_type",
            "nodal_agency",
            "ministry_name",
            "alternate_names",
            "canonical_id",
        ]:
            batch_op.drop_column(col)
