"""Deepen Finance commission status transitions (PHX-G356).

Revision ID: 0080_finance_commission_status_g356
Revises: 0079_inventory_controlled_unship_g355
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0080_finance_commission_status_g356"
down_revision: Union[str, Sequence[str], None] = (
    "0079_inventory_controlled_unship_g355"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_commission_entries_status_valid",
        "commission_entries",
        schema="finance",
        type_="check",
    )
    op.create_check_constraint(
        "ck_commission_entries_status_valid",
        "commission_entries",
        "status IN ('accrued','payable','paid')",
        schema="finance",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_commission_entries_status_valid",
        "commission_entries",
        schema="finance",
        type_="check",
    )
    op.create_check_constraint(
        "ck_commission_entries_status_valid",
        "commission_entries",
        "status = 'accrued'",
        schema="finance",
    )
