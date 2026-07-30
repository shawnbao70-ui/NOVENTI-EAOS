"""Create CRM Delivery Order shell C9 (PHX-G302).

Revision ID: 0038_crm_delivery_order_g302
Revises: 0037_crm_sales_order_confirm_g301
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0038_crm_delivery_order_g302"
down_revision: Union[str, Sequence[str], None] = (
    "0037_crm_sales_order_confirm_g301"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "delivery_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_version", sa.Integer(), nullable=False),
        sa.Column("quote_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "sales_order_version > 0",
            name="ck_delivery_orders_so_version_positive",
        ),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_delivery_orders_total_amount_non_negative",
        ),
        sa.CheckConstraint(
            "status = 'draft'", name="ck_delivery_orders_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_delivery_orders_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_delivery_orders_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            name="fk_delivery_orders_sales_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            name="fk_delivery_orders_quote_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            name="fk_delivery_orders_requirement_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_delivery_orders_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "sales_order_id",
            name="uq_delivery_orders_tenant_sales_order",
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_delivery_orders_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_delivery_orders_tenant_idempotency",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_delivery_orders_tenant_status",
        "delivery_orders",
        ["tenant_id", "status"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_delivery_orders_tenant_status",
        table_name="delivery_orders",
        schema="crm",
    )
    op.drop_table("delivery_orders", schema="crm")
