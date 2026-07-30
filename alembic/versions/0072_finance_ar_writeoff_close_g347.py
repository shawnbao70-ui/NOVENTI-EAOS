"""Persist AR write-offs and enable AR invoice close (PHX-G347).

Revision ID: 0072_finance_ar_writeoff_close_g347
Revises: 0071_finance_tax_credit_link_g344
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0072_finance_ar_writeoff_close_g347"
down_revision: Union[str, Sequence[str], None] = (
    "0071_finance_tax_credit_link_g344"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ar_write_offs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("amount > 0", name="ck_ar_write_offs_amount_positive"),
        sa.CheckConstraint("version > 0", name="ck_ar_write_offs_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["kernel.tenants.id"],
            name="fk_ar_write_offs_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_ar_write_offs_invoice_tenant", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_ar_write_offs_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key",
            name="uq_ar_write_offs_tenant_idempotency_key",
        ),
        schema="finance",
    )
    op.create_index(
        "ix_finance_ar_write_offs_tenant_invoice", "ar_write_offs",
        ["tenant_id", "ar_invoice_id"], schema="finance",
    )
    op.drop_constraint(
        "ck_ar_invoices_status_valid", "ar_invoices", schema="crm", type_="check"
    )
    op.create_check_constraint(
        "ck_ar_invoices_status_valid", "ar_invoices",
        "status IN ('draft','issued','closed','voided')", schema="crm",
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.ar_invoices SET status = 'issued' WHERE status = 'closed'"
        )
    )
    op.drop_constraint(
        "ck_ar_invoices_status_valid", "ar_invoices", schema="crm", type_="check"
    )
    op.create_check_constraint(
        "ck_ar_invoices_status_valid", "ar_invoices",
        "status IN ('draft','issued','voided')", schema="crm",
    )
    op.drop_index(
        "ix_finance_ar_write_offs_tenant_invoice",
        table_name="ar_write_offs", schema="finance",
    )
    op.drop_table("ar_write_offs", schema="finance")
