"""Persist tax invoice to AR credit note links (PHX-G344).

Revision ID: 0071_finance_tax_credit_link_g344
Revises: 0070_crm_cn_rma_issue_link_g343
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0071_finance_tax_credit_link_g344"
down_revision: Union[str, Sequence[str], None] = (
    "0070_crm_cn_rma_issue_link_g343"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "tax_credit_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("tax_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("credit_note_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("status IN ('linked')", name="ck_tax_credit_links_status_valid"),
        sa.CheckConstraint("version > 0", name="ck_tax_credit_links_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tax_credit_links_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tax_invoice_id", "tenant_id"],
            ["finance.tax_invoices.id", "finance.tax_invoices.tenant_id"],
            name="fk_tax_credit_links_tax_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["credit_note_id", "tenant_id"],
            ["finance.ar_credit_notes.id", "finance.ar_credit_notes.tenant_id"],
            name="fk_tax_credit_links_credit_note_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_tax_credit_links_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id",
            "tax_invoice_id",
            "credit_note_id",
            name="uq_tax_credit_links_tenant_tax_invoice_credit_note",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_tax_credit_links_tenant_idempotency_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_credit_links_tenant_tax_invoice",
        "tax_credit_links",
        ["tenant_id", "tax_invoice_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_credit_links_tenant_credit_note",
        "tax_credit_links",
        ["tenant_id", "credit_note_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_tax_credit_links_tenant_credit_note",
        table_name="tax_credit_links",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_tax_credit_links_tenant_tax_invoice",
        table_name="tax_credit_links",
        schema=SCHEMA,
    )
    op.drop_table("tax_credit_links", schema=SCHEMA)
