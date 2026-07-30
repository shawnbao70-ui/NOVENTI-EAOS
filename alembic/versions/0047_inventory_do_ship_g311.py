"""Create Inventory DO Ship ledger I1 (PHX-G311).

Revision ID: 0047_inventory_do_ship_g311
Revises: 0046_finance_ar_receipt_g310
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0047_inventory_do_ship_g311"
down_revision: Union[str, Sequence[str], None] = (
    "0046_finance_ar_receipt_g310"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "inventory"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.create_table(
        "stock_balances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_line_id", sa.Uuid(), nullable=False),
        sa.Column("on_hand", sa.Numeric(18, 4), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "version > 0", name="ck_stock_balances_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_stock_balances_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "sales_order_line_id",
            name="uq_stock_balances_tenant_line",
        ),
        schema=SCHEMA,
    )
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_line_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_id", sa.Uuid(), nullable=True),
        sa.Column("entry_type", sa.String(length=32), nullable=False),
        sa.Column("quantity_delta", sa.Numeric(18, 4), nullable=False),
        sa.Column("balance_after", sa.Numeric(18, 4), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "entry_type IN ('adjustment','do_ship')",
            name="ck_ledger_entries_entry_type_valid",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ledger_entries_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            "sales_order_line_id",
            name="uq_ledger_entries_tenant_key_line",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_inventory_ledger_tenant_line",
        "ledger_entries",
        ["tenant_id", "sales_order_line_id"],
        schema=SCHEMA,
    )
    op.create_table(
        "delivery_ship_postings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status = 'shipped'", name="ck_delivery_ship_postings_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_delivery_ship_postings_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_delivery_ship_postings_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "delivery_order_id",
            name="uq_delivery_ship_postings_tenant_do",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_delivery_ship_postings_tenant_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_inventory_ship_postings_tenant_do",
        "delivery_ship_postings",
        ["tenant_id", "delivery_order_id"],
        schema=SCHEMA,
    )
    op.drop_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        "status IN ('draft','released','shipped')",
        schema="crm",
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.delivery_orders SET status = 'released' "
            "WHERE status = 'shipped'"
        )
    )
    op.drop_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        schema="crm",
        type_="check",
    )
    op.create_check_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        "status IN ('draft','released')",
        schema="crm",
    )
    op.drop_index(
        "ix_inventory_ship_postings_tenant_do",
        table_name="delivery_ship_postings",
        schema=SCHEMA,
    )
    op.drop_table("delivery_ship_postings", schema=SCHEMA)
    op.drop_index(
        "ix_inventory_ledger_tenant_line",
        table_name="ledger_entries",
        schema=SCHEMA,
    )
    op.drop_table("ledger_entries", schema=SCHEMA)
    op.drop_table("stock_balances", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
