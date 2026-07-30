"""Add CRM AR Invoice Issue status gate C15 (PHX-G308).

Revision ID: 0044_crm_ar_invoice_issue_g308
Revises: 0043_crm_delivery_order_release_g307
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0044_crm_ar_invoice_issue_g308"
down_revision: Union[str, Sequence[str], None] = (
    "0043_crm_delivery_order_release_g307"
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
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "ar_invoices",
        sa.Column("issue_key", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        "status IN ('draft','issued')",
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_ar_invoices_tenant_issue_key",
        "ar_invoices",
        ["tenant_id", "issue_key"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.ar_invoices SET status = 'draft', "
            "issued_at = NULL, issue_key = NULL WHERE status = 'issued'"
        )
    )
    op.drop_constraint(
        "uq_ar_invoices_tenant_issue_key",
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
    op.drop_column("ar_invoices", "issue_key", schema=SCHEMA)
    op.drop_column("ar_invoices", "issued_at", schema=SCHEMA)
    op.create_check_constraint(
        "ck_ar_invoices_status_valid",
        "ar_invoices",
        "status = 'draft'",
        schema=SCHEMA,
    )
