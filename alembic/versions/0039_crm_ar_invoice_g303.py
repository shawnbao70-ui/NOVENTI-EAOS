"""Create CRM AR Invoice shell C10 (PHX-G303).

Revision ID: 0039_crm_ar_invoice_g303
Revises: 0038_crm_delivery_order_g302
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0039_crm_ar_invoice_g303"
down_revision: Union[str, Sequence[str], None] = "0038_crm_delivery_order_g302"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ar_invoices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_version", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_version", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "delivery_order_version > 0",
            name="ck_ar_invoices_do_version_positive",
        ),
        sa.CheckConstraint(
            "sales_order_version > 0",
            name="ck_ar_invoices_so_version_positive",
        ),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_ar_invoices_total_amount_non_negative",
        ),
        sa.CheckConstraint(
            "status = 'draft'", name="ck_ar_invoices_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ar_invoices_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ar_invoices_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            name="fk_ar_invoices_delivery_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            name="fk_ar_invoices_sales_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_ar_invoices_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ar_invoices_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "delivery_order_id",
            name="uq_ar_invoices_tenant_delivery_order",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "sales_order_id",
            name="uq_ar_invoices_tenant_sales_order",
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_ar_invoices_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ar_invoices_tenant_idempotency",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_ar_invoices_tenant_status",
        "ar_invoices",
        ["tenant_id", "status"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_ar_invoices_tenant_status",
        table_name="ar_invoices",
        schema="crm",
    )
    op.drop_table("ar_invoices", schema="crm")
