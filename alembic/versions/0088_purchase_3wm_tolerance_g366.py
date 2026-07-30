"""Add Purchase three-way match tolerance policy (PHX-G366).

Revision ID: 0088_purchase_3wm_tolerance_g366
Revises: 0087_crm_do_release_approval_g365
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0088_purchase_3wm_tolerance_g366"
down_revision: Union[str, Sequence[str], None] = (
    "0087_crm_do_release_approval_g365"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.create_table(
        "tenant_three_way_match_policies",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "amount_tolerance_abs",
            sa.Numeric(18, 2),
            server_default="0",
            nullable=True,
        ),
        sa.Column(
            "amount_tolerance_pct",
            sa.Numeric(9, 4),
            server_default="0",
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_tenant_three_way_match_policies_version_positive",
        ),
        sa.CheckConstraint(
            "amount_tolerance_abs IS NULL OR amount_tolerance_abs >= 0",
            name="ck_tenant_three_way_match_policies_abs_nonneg",
        ),
        sa.CheckConstraint(
            "amount_tolerance_pct IS NULL OR amount_tolerance_pct >= 0",
            name="ck_tenant_three_way_match_policies_pct_nonneg",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tenant_three_way_match_policies_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("tenant_three_way_match_policies", schema=SCHEMA)
