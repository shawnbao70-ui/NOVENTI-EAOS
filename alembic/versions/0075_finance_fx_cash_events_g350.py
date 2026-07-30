"""Persist FX values for AR receipts and AP payments (PHX-G350).

Revision ID: 0075_finance_fx_cash_events_g350
Revises: 0074_crm_fulfillment_qty_g349
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0075_finance_fx_cash_events_g350"
down_revision: Union[str, Sequence[str], None] = (
    "0074_crm_fulfillment_qty_g349"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CASH_EVENT_COLUMNS = (
    sa.Column("functional_currency", sa.String(length=3), nullable=True),
    sa.Column("fx_rate", sa.Numeric(18, 8), nullable=True),
    sa.Column("functional_amount", sa.Numeric(18, 2), nullable=True),
)


def _upgrade_table(schema: str, table: str) -> None:
    for column in _CASH_EVENT_COLUMNS:
        op.add_column(table, column.copy(), schema=schema)
    op.execute(
        f"UPDATE {schema}.{table} "
        "SET functional_currency = currency, fx_rate = 1, functional_amount = amount"
    )
    op.alter_column(
        table, "functional_currency", existing_type=sa.String(length=3),
        nullable=False, schema=schema
    )
    op.alter_column(
        table, "fx_rate", existing_type=sa.Numeric(18, 8),
        nullable=False, schema=schema
    )
    op.alter_column(
        table, "functional_amount", existing_type=sa.Numeric(18, 2),
        nullable=False, schema=schema
    )


def upgrade() -> None:
    _upgrade_table("finance", "ar_receipts")
    _upgrade_table("purchase", "ap_payments")


def downgrade() -> None:
    for schema, table in (
        ("purchase", "ap_payments"),
        ("finance", "ar_receipts"),
    ):
        op.drop_column(table, "functional_amount", schema=schema)
        op.drop_column(table, "fx_rate", schema=schema)
        op.drop_column(table, "functional_currency", schema=schema)
