"""Create Finance Tax Invoice shell Tax1 (PHX-G316).

Revision ID: 0051_finance_tax_invoice_shell_g316
Revises: 0050_finance_receipt_psp_port_g315
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0051_finance_tax_invoice_shell_g316"
down_revision: Union[str, Sequence[str], None] = (
    "0050_finance_receipt_psp_port_g315"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "tax_invoices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_version", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issue_key", sa.Uuid(), nullable=True),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("void_key", sa.Uuid(), nullable=True),
        sa.Column("void_reason", sa.String(length=500), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "amount > 0", name="ck_tax_invoices_amount_positive"
        ),
        sa.CheckConstraint(
            "status IN ('draft','issued','voided')",
            name="ck_tax_invoices_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_tax_invoices_version_positive"
        ),
        sa.CheckConstraint(
            "ar_invoice_version > 0",
            name="ck_tax_invoices_invoice_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tax_invoices_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_tax_invoices_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_tax_invoices_ar_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_tax_invoices_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_tax_invoices_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_tax_invoices_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "issue_key",
            name="uq_tax_invoices_tenant_issue_key",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "void_key",
            name="uq_tax_invoices_tenant_void_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_invoices_tenant_status",
        "tax_invoices",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_invoices_tenant_customer",
        "tax_invoices",
        ["tenant_id", "customer_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_invoices_tenant_ar_invoice",
        "tax_invoices",
        ["tenant_id", "ar_invoice_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_tax_invoices_tenant_ar_invoice",
        table_name="tax_invoices",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_tax_invoices_tenant_customer",
        table_name="tax_invoices",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_tax_invoices_tenant_status",
        table_name="tax_invoices",
        schema=SCHEMA,
    )
    op.drop_table("tax_invoices", schema=SCHEMA)
