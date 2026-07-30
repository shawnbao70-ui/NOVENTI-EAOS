"""Create Purchase Order shell AP3 (PHX-G332).

Revision ID: 0062_purchase_order_shell_g332
Revises: 0061_crm_return_restock_g330
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0062_purchase_order_shell_g332"
down_revision: Union[str, Sequence[str], None] = "0061_crm_return_restock_g330"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"
PO_STATUSES = "'draft','archived','received'"


def upgrade() -> None:
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({PO_STATUSES})",
            name="ck_purchase_orders_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_purchase_orders_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_purchase_orders_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["purchase.suppliers.id", "purchase.suppliers.tenant_id"],
            name="fk_purchase_orders_supplier_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_purchase_orders_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_purchase_orders_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_purchase_orders_tenant_idempotency",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_purchase_orders_tenant_status",
        "purchase_orders",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_purchase_orders_tenant_supplier",
        "purchase_orders",
        ["tenant_id", "supplier_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_purchase_orders_tenant_supplier",
        table_name="purchase_orders",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_purchase_purchase_orders_tenant_status",
        table_name="purchase_orders",
        schema=SCHEMA,
    )
    op.drop_table("purchase_orders", schema=SCHEMA)
