"""CRM Return Authorization restock RET2 (PHX-G330).

Revision ID: 0061_crm_return_restock_g330
Revises: 0060_purchase_ap_bill_line_g329
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0061_crm_return_restock_g330"
down_revision: Union[str, Sequence[str], None] = (
    "0060_purchase_ap_bill_line_g329"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "return_authorizations",
        sa.Column("restocked_at", sa.DateTime(timezone=True), nullable=True),
        schema="crm",
    )
    op.add_column(
        "return_authorizations",
        sa.Column("restock_key", sa.Uuid(), nullable=True),
        schema="crm",
    )
    op.drop_constraint(
        "ck_return_authorizations_status_valid",
        "return_authorizations",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_return_authorizations_status_valid",
        "return_authorizations",
        "status IN ('draft','restocked')",
        schema="crm",
    )
    op.create_index(
        "uq_crm_return_authorizations_tenant_restock_key",
        "return_authorizations",
        ["tenant_id", "restock_key"],
        unique=True,
        schema="crm",
        postgresql_where=sa.text("restock_key IS NOT NULL"),
    )

    op.add_column(
        "ledger_entries",
        sa.Column("return_authorization_id", sa.Uuid(), nullable=True),
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
        "entry_type IN ('adjustment','do_ship','rma_restock')",
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
        "entry_type IN ('adjustment','do_ship')",
        schema="inventory",
    )
    op.drop_column(
        "ledger_entries", "return_authorization_id", schema="inventory"
    )

    op.drop_index(
        "uq_crm_return_authorizations_tenant_restock_key",
        table_name="return_authorizations",
        schema="crm",
    )
    op.execute(
        sa.text(
            "UPDATE crm.return_authorizations SET status = 'draft' "
            "WHERE status = 'restocked'"
        )
    )
    op.drop_constraint(
        "ck_return_authorizations_status_valid",
        "return_authorizations",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_return_authorizations_status_valid",
        "return_authorizations",
        "status = 'draft'",
        schema="crm",
    )
    op.drop_column("return_authorizations", "restock_key", schema="crm")
    op.drop_column("return_authorizations", "restocked_at", schema="crm")
