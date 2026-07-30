"""Persist AP bill partial-payment balances (PHX-G341).

Revision ID: 0068_purchase_ap_partial_payment_g341
Revises: 0067_finance_gl_ap_bridges_g338
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0068_purchase_ap_partial_payment_g341"
down_revision: Union[str, Sequence[str], None] = (
    "0067_finance_gl_ap_bridges_g338"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.add_column(
        "ap_bills",
        sa.Column(
            "paid_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        schema=SCHEMA,
    )
    op.execute(
        """
        UPDATE purchase.ap_bills AS bill
        SET paid_amount = COALESCE(
            (
                SELECT SUM(payment.amount)
                FROM purchase.ap_payments AS payment
                WHERE payment.tenant_id = bill.tenant_id
                  AND payment.ap_bill_id = bill.id
                  AND payment.status = 'applied'
            ),
            0
        )
        """
    )
    op.create_check_constraint(
        "ck_ap_bills_paid_amount_non_negative",
        "ap_bills",
        "paid_amount >= 0",
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_ap_bills_paid_amount_not_over_total",
        "ap_bills",
        "paid_amount <= total_amount",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ap_bills_paid_amount_not_over_total",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_constraint(
        "ck_ap_bills_paid_amount_non_negative",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("ap_bills", "paid_amount", schema=SCHEMA)
