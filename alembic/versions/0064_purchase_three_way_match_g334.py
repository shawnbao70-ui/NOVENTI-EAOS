"""Create Purchase Three-Way Match shell AP5 (PHX-G334).

Revision ID: 0064_purchase_three_way_match_g334
Revises: 0063_purchase_goods_receipt_inventory_g333
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0064_purchase_three_way_match_g334"
down_revision: Union[str, Sequence[str], None] = (
    "0063_purchase_goods_receipt_inventory_g333"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.create_table(
        "three_way_matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("purchase_order_id", sa.Uuid(), nullable=False),
        sa.Column("goods_receipt_id", sa.Uuid(), nullable=False),
        sa.Column("ap_bill_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('matched','mismatch')",
            name="ck_three_way_matches_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_three_way_matches_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_three_way_matches_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_id", "tenant_id"],
            ["purchase.purchase_orders.id", "purchase.purchase_orders.tenant_id"],
            name="fk_three_way_matches_po_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["goods_receipt_id", "tenant_id"],
            ["purchase.goods_receipts.id", "purchase.goods_receipts.tenant_id"],
            name="fk_three_way_matches_grn_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            name="fk_three_way_matches_bill_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_three_way_matches_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "purchase_order_id",
            name="uq_three_way_matches_tenant_po",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_three_way_matches_tenant_idempotency",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_three_way_matches_tenant_po",
        "three_way_matches",
        ["tenant_id", "purchase_order_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_three_way_matches_tenant_po",
        table_name="three_way_matches",
        schema=SCHEMA,
    )
    op.drop_table("three_way_matches", schema=SCHEMA)
