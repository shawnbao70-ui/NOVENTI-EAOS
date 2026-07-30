"""Persist Quote-to-Sales-Order FX snapshots (PHX-G352).

Revision ID: 0076_crm_convert_fx_snapshot_g352
Revises: 0075_finance_fx_cash_events_g350
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0076_crm_convert_fx_snapshot_g352"
down_revision: Union[str, Sequence[str], None] = "0075_finance_fx_cash_events_g350"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_quote_fx() -> None:
    op.add_column(
        "quotes", sa.Column("functional_currency", sa.String(length=3), nullable=True),
        schema="crm",
    )
    op.add_column(
        "quotes", sa.Column("fx_rate", sa.Numeric(18, 8), nullable=True), schema="crm"
    )
    op.execute(
        "UPDATE crm.quotes SET functional_currency = currency, fx_rate = 1"
    )
    op.alter_column(
        "quotes", "functional_currency", existing_type=sa.String(length=3),
        nullable=False, schema="crm"
    )
    op.alter_column(
        "quotes", "fx_rate", existing_type=sa.Numeric(18, 8), nullable=False, schema="crm"
    )


def _add_snapshot(table: str, total_column: str) -> None:
    op.add_column(
        table, sa.Column("functional_currency", sa.String(length=3), nullable=True),
        schema="crm",
    )
    op.add_column(
        table, sa.Column("fx_rate", sa.Numeric(18, 8), nullable=True), schema="crm"
    )
    op.add_column(
        table, sa.Column("functional_total", sa.Numeric(18, 2), nullable=True),
        schema="crm",
    )
    op.execute(
        f"UPDATE crm.{table} SET functional_currency = currency, "
        f"fx_rate = 1, functional_total = {total_column}"
    )
    for name, column_type in (
        ("functional_currency", sa.String(length=3)),
        ("fx_rate", sa.Numeric(18, 8)),
        ("functional_total", sa.Numeric(18, 2)),
    ):
        op.alter_column(
            table, name, existing_type=column_type, nullable=False, schema="crm"
        )


def upgrade() -> None:
    _add_quote_fx()
    _add_snapshot("quote_conversions", "0")
    _add_snapshot("sales_orders", "total_amount")
    op.create_check_constraint(
        "ck_sales_orders_functional_total_non_negative",
        "sales_orders",
        "functional_total >= 0",
        schema="crm",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_sales_orders_functional_total_non_negative",
        "sales_orders",
        schema="crm",
    )
    for table in ("sales_orders", "quote_conversions"):
        op.drop_column(table, "functional_total", schema="crm")
        op.drop_column(table, "fx_rate", schema="crm")
        op.drop_column(table, "functional_currency", schema="crm")
    op.drop_column("quotes", "fx_rate", schema="crm")
    op.drop_column("quotes", "functional_currency", schema="crm")
