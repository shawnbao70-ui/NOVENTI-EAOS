"""Create Finance AR Receipt shell F1 (PHX-G310).

Revision ID: 0046_finance_ar_receipt_g310
Revises: 0045_crm_ar_invoice_void_g309
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0046_finance_ar_receipt_g310"
down_revision: Union[str, Sequence[str], None] = (
    "0045_crm_ar_invoice_void_g309"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.create_table(
        "ar_receipts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ar_invoice_id", sa.Uuid(), nullable=True),
        sa.Column("ar_invoice_version", sa.Integer(), nullable=True),
        sa.Column("apply_key", sa.Uuid(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "amount > 0", name="ck_ar_receipts_amount_positive"
        ),
        sa.CheckConstraint(
            "status IN ('draft','applied')",
            name="ck_ar_receipts_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ar_receipts_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ar_receipts_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_ar_receipts_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_ar_receipts_ar_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ar_receipts_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_ar_receipts_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ar_receipts_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id", "apply_key", name="uq_ar_receipts_tenant_apply_key"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_receipts_tenant_status",
        "ar_receipts",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_receipts_tenant_customer",
        "ar_receipts",
        ["tenant_id", "customer_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_ar_receipts_tenant_customer",
        table_name="ar_receipts",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_ar_receipts_tenant_status",
        table_name="ar_receipts",
        schema=SCHEMA,
    )
    op.drop_table("ar_receipts", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
