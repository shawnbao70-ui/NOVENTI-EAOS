"""Persist Sales Order FX snapshots on AR invoices (PHX-G358).

Revision ID: 0081_crm_ar_invoice_fx_g358
Revises: 0080_finance_commission_status_g356
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0081_crm_ar_invoice_fx_g358"
down_revision: Union[str, Sequence[str], None] = "0080_finance_commission_status_g356"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ar_invoices",
        sa.Column("functional_currency", sa.String(length=3), nullable=True),
        schema="crm",
    )
    op.add_column(
        "ar_invoices",
        sa.Column("fx_rate", sa.Numeric(18, 8), nullable=True),
        schema="crm",
    )
    op.add_column(
        "ar_invoices",
        sa.Column("functional_total", sa.Numeric(18, 2), nullable=True),
        schema="crm",
    )
    op.execute(
        "UPDATE crm.ar_invoices "
        "SET functional_currency = currency, fx_rate = 1, functional_total = total_amount"
    )
    for name, column_type in (
        ("functional_currency", sa.String(length=3)),
        ("fx_rate", sa.Numeric(18, 8)),
        ("functional_total", sa.Numeric(18, 2)),
    ):
        op.alter_column(
            "ar_invoices",
            name,
            existing_type=column_type,
            nullable=False,
            schema="crm",
        )
    op.create_check_constraint(
        "ck_ar_invoices_functional_total_non_negative",
        "ar_invoices",
        "functional_total >= 0",
        schema="crm",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ar_invoices_functional_total_non_negative",
        "ar_invoices",
        schema="crm",
        type_="check",
    )
    op.drop_column("ar_invoices", "functional_total", schema="crm")
    op.drop_column("ar_invoices", "fx_rate", schema="crm")
    op.drop_column("ar_invoices", "functional_currency", schema="crm")
