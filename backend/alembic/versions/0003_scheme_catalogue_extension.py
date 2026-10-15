"""Add scheme catalogue extension fields

Revision ID: 0003_scheme_catalogue
Revises: 0002_guided_self_application
Create Date: 2026-10-12

Adds catalogue-level classification fields to government_schemes table:
- government_level, state_code, category, beneficiary_groups
- application_method, portal_capability, keywords
- scheme_status, is_candidate, min_age, max_age
All new columns have safe defaults so existing rows are unaffected.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0003_scheme_catalogue"
down_revision = "0002_guided_self_application"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("government_schemes") as batch_op:
        batch_op.add_column(
            sa.Column("government_level", sa.String(20), nullable=False, server_default="central")
        )
        batch_op.add_column(
            sa.Column("state_code", sa.String(10), nullable=True)
        )
        batch_op.add_column(
            sa.Column("category", sa.String(40), nullable=False, server_default="other")
        )
        batch_op.add_column(
            sa.Column("beneficiary_groups", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("application_method", sa.String(20), nullable=False, server_default="unknown")
        )
        batch_op.add_column(
            sa.Column("portal_capability", sa.String(40), nullable=False, server_default="GUIDED_PREPARATION")
        )
        batch_op.add_column(
            sa.Column("keywords", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("scheme_status", sa.String(20), nullable=False, server_default="active")
        )
        batch_op.add_column(
            sa.Column("is_candidate", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column("min_age", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("max_age", sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("government_schemes") as batch_op:
        for col in [
            "max_age", "min_age", "is_candidate", "scheme_status",
            "keywords", "portal_capability", "application_method",
            "beneficiary_groups", "category", "state_code", "government_level",
        ]:
            batch_op.drop_column(col)
