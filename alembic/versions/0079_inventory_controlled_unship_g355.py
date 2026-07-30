"""Track controlled delivery-order unship reversals (PHX-G355).

Revision ID: 0079_inventory_controlled_unship_g355
Revises: 0078_inventory_do_ship_approval_g354
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0079_inventory_controlled_unship_g355"
down_revision: Union[str, Sequence[str], None] = (
    "0078_inventory_do_ship_approval_g354"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "delivery_ship_postings",
        sa.Column("unshipped_at", sa.DateTime(timezone=True), nullable=True),
        schema="inventory",
    )
    op.add_column(
        "delivery_ship_postings",
        sa.Column("unship_key", sa.Uuid(), nullable=True),
        schema="inventory",
    )
    op.drop_constraint(
        "ck_delivery_ship_postings_status_valid",
        "delivery_ship_postings",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_delivery_ship_postings_status_valid",
        "delivery_ship_postings",
        "status IN ('shipped','unshipped')",
        schema="inventory",
    )
    op.drop_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        "entry_type IN ('adjustment','do_ship','do_unship','rma_restock','po_receive')",
        schema="inventory",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        "entry_type IN ('adjustment','do_ship','rma_restock','po_receive')",
        schema="inventory",
    )
    op.drop_constraint(
        "ck_delivery_ship_postings_status_valid",
        "delivery_ship_postings",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_delivery_ship_postings_status_valid",
        "delivery_ship_postings",
        "status = 'shipped'",
        schema="inventory",
    )
    op.drop_column("delivery_ship_postings", "unship_key", schema="inventory")
    op.drop_column("delivery_ship_postings", "unshipped_at", schema="inventory")
