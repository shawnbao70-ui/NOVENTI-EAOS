"""Extend GL bridge source types with realized_fx (PHX-G372).

Revision ID: 0092_finance_realized_fx_gl_bridge_g372
Revises: 0091_finance_treasury_transfer_g371
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0092_finance_realized_fx_gl_bridge_g372"
down_revision: Union[str, Sequence[str], None] = (
    "0091_finance_treasury_transfer_g371"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.drop_constraint(
        "ck_gl_bridge_postings_source_type_valid",
        "gl_bridge_postings",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_gl_bridge_postings_source_type_valid",
        "gl_bridge_postings",
        (
            "source_type IN ('ar_invoice','ar_receipt','tax_invoice',"
            "'commission','ap_bill','ap_payment','realized_fx')"
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_gl_bridge_postings_source_type_valid",
        "gl_bridge_postings",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_gl_bridge_postings_source_type_valid",
        "gl_bridge_postings",
        (
            "source_type IN ('ar_invoice','ar_receipt','tax_invoice',"
            "'commission','ap_bill','ap_payment')"
        ),
        schema=SCHEMA,
    )
