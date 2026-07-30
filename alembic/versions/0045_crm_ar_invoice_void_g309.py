"""Add CRM AR Invoice Void status gate C16 (PHX-G309).

Revision ID: 0045_crm_ar_invoice_void_g309
Revises: 0044_crm_ar_invoice_issue_g308
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0045_crm_ar_invoice_void_g309"
down_revision: Union[str, Sequence[str], None] = (
    "0044_crm_ar_invoice_issue_g308"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.drop_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        schema=SCHEMA,
        type_="check",
    )
    op.add_column(
        "ar_invoices",
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "ar_invoices",
        sa.Column("void_key", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "ar_invoices",
        sa.Column("void_reason", sa.String(length=500), nullable=True),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        "status IN ('draft','issued','voided')",
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_ar_invoices_tenant_void_key",
        "ar_invoices",
        ["tenant_id", "void_key"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.ar_invoices SET status = 'issued', "
            "voided_at = NULL, void_key = NULL, void_reason = NULL "
            "WHERE status = 'voided'"
        )
    )
    op.drop_constraint(
        "uq_ar_invoices_tenant_void_key",
        "ar_invoices",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("ar_invoices", "void_reason", schema=SCHEMA)
    op.drop_column("ar_invoices", "void_key", schema=SCHEMA)
    op.drop_column("ar_invoices", "voided_at", schema=SCHEMA)
    op.create_check_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        "status IN ('draft','issued')",
        schema=SCHEMA,
    )
