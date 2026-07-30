"""Add tax red-credit lineage (PHX-G360).

Revision ID: 0083_finance_tax_red_credit_g360
Revises: 0082_finance_realized_fx_allocation_g359
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0083_finance_tax_red_credit_g360"
down_revision: Union[str, Sequence[str], None] = (
    "0082_finance_realized_fx_allocation_g359"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.add_column(
        "tax_invoices",
        sa.Column("original_tax_invoice_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "tax_invoices",
        sa.Column(
            "is_red_credit",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_tax_invoices_original_tenant",
        "tax_invoices",
        "tax_invoices",
        ["original_tax_invoice_id", "tenant_id"],
        ["id", "tenant_id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_tax_invoices_tenant_original",
        "tax_invoices",
        ["tenant_id", "original_tax_invoice_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_invoices_tenant_original",
        "tax_invoices",
        ["tenant_id", "original_tax_invoice_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_tax_invoices_tenant_original",
        table_name="tax_invoices",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "uq_tax_invoices_tenant_original",
        "tax_invoices",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_constraint(
        "fk_tax_invoices_original_tenant",
        "tax_invoices",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("tax_invoices", "is_red_credit", schema=SCHEMA)
    op.drop_column("tax_invoices", "original_tax_invoice_id", schema=SCHEMA)
