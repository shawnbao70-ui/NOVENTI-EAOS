"""Create finance treasury transfers with FX (PHX-G371).

Revision ID: 0091_finance_treasury_transfer_g371
Revises: 0090_inventory_controlled_reship_g370
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0091_finance_treasury_transfer_g371"
down_revision: Union[str, Sequence[str], None] = (
    "0090_inventory_controlled_reship_g370"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "treasury_transfers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("from_account_ref", sa.String(length=128), nullable=False),
        sa.Column("to_account_ref", sa.String(length=128), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("functional_currency", sa.String(length=3), nullable=False),
        sa.Column("fx_rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("functional_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "amount > 0", name="ck_treasury_transfers_amount_positive"
        ),
        sa.CheckConstraint(
            "functional_amount > 0",
            name="ck_treasury_transfers_functional_amount_positive",
        ),
        sa.CheckConstraint(
            "fx_rate > 0", name="ck_treasury_transfers_fx_rate_positive"
        ),
        sa.CheckConstraint(
            "from_account_ref <> to_account_ref",
            name="ck_treasury_transfers_accounts_distinct",
        ),
        sa.CheckConstraint(
            "status IN ('draft','posted')",
            name="ck_treasury_transfers_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_treasury_transfers_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_treasury_transfers_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_treasury_transfers_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_treasury_transfers_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "post_key",
            name="uq_treasury_transfers_tenant_post_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_treasury_transfers_tenant_status",
        "treasury_transfers",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_treasury_transfers_tenant_status",
        table_name="treasury_transfers",
        schema=SCHEMA,
    )
    op.drop_table("treasury_transfers", schema=SCHEMA)
