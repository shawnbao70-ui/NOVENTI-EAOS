"""Create CRM Sales Order Confirmation C8 persistence (PHX-G301).

Revision ID: 0037_crm_sales_order_confirm_g301
Revises: 0036_crm_quote_line_g300
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0037_crm_sales_order_confirm_g301"
down_revision: Union[str, Sequence[str], None] = "0036_crm_quote_line_g300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
    op.add_column(
        "sales_orders",
        sa.Column(
            "total_amount",
            sa.Numeric(18, 2),
            server_default="0",
            nullable=False,
        ),
        schema="crm",
    )
    op.add_column(
        "sales_orders",
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        schema="crm",
    )
    op.add_column(
        "sales_orders",
        sa.Column("confirmation_key", sa.Uuid(), nullable=True),
        schema="crm",
    )
    op.create_check_constraint(
        "ck_sales_orders_total_amount_non_negative",
        "sales_orders",
        "total_amount >= 0",
        schema="crm",
    )
    op.create_unique_constraint(
        "uq_sales_orders_tenant_confirmation_key",
        "sales_orders",
        ["tenant_id", "confirmation_key"],
        schema="crm",
    )
    op.create_table(
        "sales_order_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_id", sa.Uuid(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "line_number > 0",
            name="ck_sales_order_lines_line_number_positive",
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_sales_order_lines_quantity_positive"
        ),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_sales_order_lines_unit_price_non_negative",
        ),
        sa.CheckConstraint(
            "amount >= 0",
            name="ck_sales_order_lines_amount_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_sales_order_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            name="fk_sales_order_lines_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_sales_order_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "sales_order_id",
            "line_number",
            name="uq_sales_order_lines_tenant_order_line_number",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_sales_order_lines_tenant_order",
        "sales_order_lines",
        ["tenant_id", "sales_order_id"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_sales_order_lines_tenant_order",
        table_name="sales_order_lines",
        schema="crm",
    )
    op.drop_table("sales_order_lines", schema="crm")
    op.drop_constraint(
        "uq_sales_orders_tenant_confirmation_key",
        "sales_orders",
        schema="crm",
        type_="unique",
    )
    op.drop_constraint(
        "ck_sales_orders_total_amount_non_negative",
        "sales_orders",
        schema="crm",
        type_="check",
    )
    op.drop_column("sales_orders", "confirmation_key", schema="crm")
    op.drop_column("sales_orders", "confirmed_at", schema="crm")
    op.drop_column("sales_orders", "total_amount", schema="crm")
    op.drop_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        schema="crm",
        type_="check",
    )
    op.execute(
        "UPDATE crm.sales_orders SET status = 'created' "
        "WHERE status = 'confirmed'"
    )
    op.create_check_constraint(
        "ck_sales_orders_status_valid",
        "sales_orders",
        "status = 'created'",
        schema="crm",
    )
