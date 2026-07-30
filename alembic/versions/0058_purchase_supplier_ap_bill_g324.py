"""Create Purchase Supplier + AP Bill draft shell AP1 (PHX-G324).

Revision ID: 0058_purchase_supplier_ap_bill_g324
Revises: 0057_finance_gl_bank_recon_g323
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0058_purchase_supplier_ap_bill_g324"
down_revision: Union[str, Sequence[str], None] = (
    "0057_finance_gl_bank_recon_g323"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"
SUPPLIER_STATUSES = "'active','archived'"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({SUPPLIER_STATUSES})",
            name="ck_suppliers_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_suppliers_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_suppliers_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_suppliers_id_tenant_id"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_purchase_suppliers_tenant_code_ci",
        "suppliers",
        ["tenant_id", sa.text("lower(code)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_suppliers_tenant_status",
        "suppliers",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "ap_bills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_ap_bills_total_amount_non_negative",
        ),
        sa.CheckConstraint(
            "status IN ('draft')",
            name="ck_ap_bills_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ap_bills_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ap_bills_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["purchase.suppliers.id", "purchase.suppliers.tenant_id"],
            name="fk_ap_bills_supplier_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ap_bills_id_tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_ap_bills_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ap_bills_tenant_idempotency",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_ap_bills_tenant_status",
        "ap_bills",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_ap_bills_tenant_supplier",
        "ap_bills",
        ["tenant_id", "supplier_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_ap_bills_tenant_supplier",
        table_name="ap_bills",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_purchase_ap_bills_tenant_status",
        table_name="ap_bills",
        schema=SCHEMA,
    )
    op.drop_table("ap_bills", schema=SCHEMA)
    op.drop_index(
        "ix_purchase_suppliers_tenant_status",
        table_name="suppliers",
        schema=SCHEMA,
    )
    op.drop_index(
        "uq_purchase_suppliers_tenant_code_ci",
        table_name="suppliers",
        schema=SCHEMA,
    )
    op.drop_table("suppliers", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
