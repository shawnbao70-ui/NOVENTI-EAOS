"""Add Finance receipt PSP policy and receipt PSP state (PHX-G315 / F2).

Revision ID: 0050_finance_receipt_psp_port_g315
Revises: 0049_finance_commission_ledger_g314
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0050_finance_receipt_psp_port_g315"
down_revision: Union[str, Sequence[str], None] = (
    "0049_finance_commission_ledger_g314"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.add_column(
        "ar_receipts", sa.Column("psp_ref", sa.String(length=128), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "ar_receipts",
        sa.Column("psp_status", sa.String(length=32), nullable=True),
        schema=SCHEMA,
    )
    op.create_table(
        "tenant_receipt_policies",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "receipt_psp_required",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0", name="ck_tenant_receipt_policies_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tenant_receipt_policies_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("tenant_receipt_policies", schema=SCHEMA)
    op.drop_column("ar_receipts", "psp_status", schema=SCHEMA)
    op.drop_column("ar_receipts", "psp_ref", schema=SCHEMA)
