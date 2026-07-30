"""Persist realized FX events for AR receipt allocations (PHX-G359).

Revision ID: 0082_finance_realized_fx_allocation_g359
Revises: 0081_crm_ar_invoice_fx_g358
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0082_finance_realized_fx_allocation_g359"
down_revision: Union[str, Sequence[str], None] = "0081_crm_ar_invoice_fx_g358"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "realized_fx_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("receipt_id", sa.Uuid(), nullable=False),
        sa.Column("invoice_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("source_type = 'allocation'", name="source_type_allocation"),
        sa.CheckConstraint("amount > 0", name="amount_positive"),
        sa.CheckConstraint("side IN ('gain', 'loss')", name="side_valid"),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["kernel.tenants.id"],
            name="fk_realized_fx_events_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["finance.ar_receipts.id", "finance.ar_receipts.tenant_id"],
            name="fk_realized_fx_events_receipt_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_realized_fx_events_invoice_tenant", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_id", "tenant_id"],
            [
                "finance.ar_receipt_allocations.id",
                "finance.ar_receipt_allocations.tenant_id",
            ],
            name="fk_realized_fx_events_allocation_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_realized_fx_events_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id", "source_type", "source_id",
            name="uq_realized_fx_events_tenant_source",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_realized_fx_events_tenant_receipt",
        "realized_fx_events",
        ["tenant_id", "receipt_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_realized_fx_events_tenant_receipt",
        table_name="realized_fx_events",
        schema=SCHEMA,
    )
    op.drop_table("realized_fx_events", schema=SCHEMA)
