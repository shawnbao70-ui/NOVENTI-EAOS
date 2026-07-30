"""Persist AR receipt allocations (PHX-G342).

Revision ID: 0069_finance_ar_allocation_g342
Revises: 0068_purchase_ap_partial_payment_g341
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0069_finance_ar_allocation_g342"
down_revision: Union[str, Sequence[str], None] = (
    "0068_purchase_ap_partial_payment_g341"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.add_column(
        "ar_receipts",
        sa.Column(
            "allocated_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        schema=SCHEMA,
    )
    op.execute(
        """
        UPDATE finance.ar_receipts
        SET allocated_amount = amount
        WHERE ar_invoice_id IS NOT NULL
        """
    )
    op.create_check_constraint(
        "ck_ar_receipts_allocated_amount_non_negative",
        "ar_receipts",
        "allocated_amount >= 0 AND allocated_amount <= amount",
        schema=SCHEMA,
    )
    op.create_table(
        "ar_receipt_allocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("receipt_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("allocation_key", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("amount > 0", name="ck_ar_receipt_allocations_amount_positive"),
        sa.CheckConstraint("version > 0", name="ck_ar_receipt_allocations_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["kernel.tenants.id"],
            name="fk_ar_receipt_allocations_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["finance.ar_receipts.id", "finance.ar_receipts.tenant_id"],
            name="fk_ar_receipt_allocations_receipt_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_ar_receipt_allocations_invoice_tenant", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_ar_receipt_allocations_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id", "allocation_key",
            name="uq_ar_receipt_allocations_tenant_allocation_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_receipt_allocations_tenant_receipt",
        "ar_receipt_allocations",
        ["tenant_id", "receipt_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_ar_receipt_allocations_tenant_receipt",
        table_name="ar_receipt_allocations", schema=SCHEMA,
    )
    op.drop_table("ar_receipt_allocations", schema=SCHEMA)
    op.drop_constraint(
        "ck_ar_receipts_allocated_amount_non_negative",
        "ar_receipts", schema=SCHEMA, type_="check",
    )
    op.drop_column("ar_receipts", "allocated_amount", schema=SCHEMA)
