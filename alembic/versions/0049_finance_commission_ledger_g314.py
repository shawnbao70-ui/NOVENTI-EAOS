"""Create Finance commission ledger shell Z2 (PHX-G314).

Revision ID: 0049_finance_commission_ledger_g314
Revises: 0048_finance_ar_credit_note_g312
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0049_finance_commission_ledger_g314"
down_revision: Union[str, Sequence[str], None] = (
    "0048_finance_ar_credit_note_g312"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "commission_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("source_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("beneficiary_subject_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "amount > 0", name="ck_commission_entries_amount_positive"
        ),
        sa.CheckConstraint(
            "status = 'accrued'", name="ck_commission_entries_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_commission_entries_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_commission_entries_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_commission_entries_ar_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_commission_entries_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_commission_entries_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_commission_entries_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "source_invoice_id",
            "beneficiary_subject_id",
            name="uq_commission_entries_tenant_invoice_beneficiary",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_commission_entries_tenant_status",
        "commission_entries",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_commission_entries_tenant_status",
        table_name="commission_entries",
        schema=SCHEMA,
    )
    op.drop_table("commission_entries", schema=SCHEMA)
