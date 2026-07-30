"""Persist delivery quantities and SO fulfillment aggregates (PHX-G349).

Revision ID: 0074_crm_fulfillment_qty_g349
Revises: 0073_crm_quote_issue_approval_g348
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0074_crm_fulfillment_qty_g349"
down_revision: Union[str, Sequence[str], None] = (
    "0073_crm_quote_issue_approval_g348"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sales_orders",
        sa.Column("ordered_quantity", sa.Numeric(18, 3), server_default="0", nullable=False),
        schema="crm",
    )
    op.add_column(
        "sales_orders",
        sa.Column("shipped_quantity", sa.Numeric(18, 3), server_default="0", nullable=False),
        schema="crm",
    )
    op.drop_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        "status IN ('created','confirmed','partially_shipped','shipped')",
        schema="crm",
    )
    op.drop_constraint(
        "uq_delivery_orders_tenant_sales_order",
        "delivery_orders",
        schema="crm",
        type_="unique",
    )
    op.create_table(
        "delivery_order_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_line_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_delivery_order_lines_quantity_positive"),
        sa.CheckConstraint(
            "status IN ('open','shipped')",
            name="ck_delivery_order_lines_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            name="fk_delivery_order_lines_delivery_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_line_id", "tenant_id"],
            ["crm.sales_order_lines.id", "crm.sales_order_lines.tenant_id"],
            name="fk_delivery_order_lines_sales_order_line_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_delivery_order_lines_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id",
            "delivery_order_id",
            "sales_order_line_id",
            name="uq_delivery_order_lines_tenant_do_so_line",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_delivery_order_lines_tenant_do",
        "delivery_order_lines",
        ["tenant_id", "delivery_order_id"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_delivery_order_lines_tenant_do",
        table_name="delivery_order_lines",
        schema="crm",
    )
    op.drop_table("delivery_order_lines", schema="crm")
    op.create_unique_constraint(
        "uq_delivery_orders_tenant_sales_order",
        "delivery_orders",
        ["tenant_id", "sales_order_id"],
        schema="crm",
    )
    op.drop_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        "status IN ('created','confirmed')",
        schema="crm",
    )
    op.drop_column("sales_orders", "shipped_quantity", schema="crm")
    op.drop_column("sales_orders", "ordered_quantity", schema="crm")
