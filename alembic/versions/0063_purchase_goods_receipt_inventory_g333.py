"""Purchase PO lines + Goods Receipt + item inventory AP4 (PHX-G333).

Revision ID: 0063_purchase_goods_receipt_inventory_g333
Revises: 0062_purchase_order_shell_g332
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0063_purchase_goods_receipt_inventory_g333"
down_revision: Union[str, Sequence[str], None] = "0062_purchase_order_shell_g332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "purchase_order_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("purchase_order_id", sa.Uuid(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("inventory_item_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active')",
            name="ck_purchase_order_lines_status_valid",
        ),
        sa.CheckConstraint(
            "line_number > 0",
            name="ck_purchase_order_lines_line_number_positive",
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_purchase_order_lines_quantity_positive"
        ),
        sa.CheckConstraint(
            "unit_price IS NULL OR unit_price >= 0",
            name="ck_purchase_order_lines_unit_price_non_negative",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_purchase_order_lines_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_purchase_order_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_id", "tenant_id"],
            ["purchase.purchase_orders.id", "purchase.purchase_orders.tenant_id"],
            name="fk_purchase_order_lines_po_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_purchase_order_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "purchase_order_id",
            "line_number",
            name="uq_purchase_order_lines_tenant_po_line",
        ),
        schema="purchase",
    )
    op.create_index(
        "ix_purchase_po_lines_tenant_po",
        "purchase_order_lines",
        ["tenant_id", "purchase_order_id"],
        schema="purchase",
    )

    op.create_table(
        "goods_receipts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("purchase_order_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('received')",
            name="ck_goods_receipts_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_goods_receipts_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_goods_receipts_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_id", "tenant_id"],
            ["purchase.purchase_orders.id", "purchase.purchase_orders.tenant_id"],
            name="fk_goods_receipts_po_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_goods_receipts_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "purchase_order_id",
            name="uq_goods_receipts_tenant_po",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_goods_receipts_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_goods_receipts_tenant_code"
        ),
        schema="purchase",
    )
    op.create_index(
        "ix_purchase_goods_receipts_tenant_po",
        "goods_receipts",
        ["tenant_id", "purchase_order_id"],
        schema="purchase",
    )

    op.create_table(
        "item_stock_balances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("inventory_item_id", sa.Uuid(), nullable=False),
        sa.Column("on_hand", sa.Numeric(18, 4), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "version > 0", name="ck_item_stock_balances_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_item_stock_balances_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "inventory_item_id",
            name="uq_item_stock_balances_tenant_item",
        ),
        schema="inventory",
    )

    op.alter_column(
        "ledger_entries",
        "sales_order_line_id",
        existing_type=sa.Uuid(),
        nullable=True,
        schema="inventory",
    )
    op.add_column(
        "ledger_entries",
        sa.Column("inventory_item_id", sa.Uuid(), nullable=True),
        schema="inventory",
    )
    op.add_column(
        "ledger_entries",
        sa.Column("purchase_order_id", sa.Uuid(), nullable=True),
        schema="inventory",
    )
    op.add_column(
        "ledger_entries",
        sa.Column("goods_receipt_id", sa.Uuid(), nullable=True),
        schema="inventory",
    )
    op.drop_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        "entry_type IN ('adjustment','do_ship','rma_restock','po_receive')",
        schema="inventory",
    )
    op.create_index(
        "ix_inventory_ledger_tenant_item",
        "ledger_entries",
        ["tenant_id", "inventory_item_id"],
        schema="inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_ledger_tenant_item",
        table_name="ledger_entries",
        schema="inventory",
    )
    op.drop_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        schema="inventory",
        type_="check",
    )
    op.create_check_constraint(
        "ck_ledger_entries_entry_type_valid",
        "ledger_entries",
        "entry_type IN ('adjustment','do_ship','rma_restock')",
        schema="inventory",
    )
    op.drop_column("ledger_entries", "goods_receipt_id", schema="inventory")
    op.drop_column("ledger_entries", "purchase_order_id", schema="inventory")
    op.drop_column("ledger_entries", "inventory_item_id", schema="inventory")
    op.execute(
        sa.text(
            "DELETE FROM inventory.ledger_entries WHERE sales_order_line_id IS NULL"
        )
    )
    op.alter_column(
        "ledger_entries",
        "sales_order_line_id",
        existing_type=sa.Uuid(),
        nullable=False,
        schema="inventory",
    )
    op.drop_table("item_stock_balances", schema="inventory")
    op.drop_index(
        "ix_purchase_goods_receipts_tenant_po",
        table_name="goods_receipts",
        schema="purchase",
    )
    op.drop_table("goods_receipts", schema="purchase")
    op.drop_index(
        "ix_purchase_po_lines_tenant_po",
        table_name="purchase_order_lines",
        schema="purchase",
    )
    op.drop_table("purchase_order_lines", schema="purchase")
