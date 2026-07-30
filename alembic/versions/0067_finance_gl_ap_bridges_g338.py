"""Extend Finance GL bridges with AP bill and payment sources (PHX-G338).

Revision ID: 0067_finance_gl_ap_bridges_g338
Revises: 0066_crm_return_credit_note_g337
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0067_finance_gl_ap_bridges_g338"
down_revision: Union[str, Sequence[str], None] = (
    "0066_crm_return_credit_note_g337"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.add_column(
        "gl_bridge_maps",
        sa.Column("ap_control", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "gl_bridge_maps",
        sa.Column("ap_expense", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_gl_bridge_maps_ap_control",
        "gl_bridge_maps",
        "gl_accounts",
        ["ap_control"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_gl_bridge_maps_ap_expense",
        "gl_bridge_maps",
        "gl_accounts",
        ["ap_expense"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
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
        "source_type IN ('ar_invoice','ar_receipt','tax_invoice','commission')",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "fk_gl_bridge_maps_ap_expense",
        "gl_bridge_maps",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_gl_bridge_maps_ap_control",
        "gl_bridge_maps",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("gl_bridge_maps", "ap_expense", schema=SCHEMA)
    op.drop_column("gl_bridge_maps", "ap_control", schema=SCHEMA)
