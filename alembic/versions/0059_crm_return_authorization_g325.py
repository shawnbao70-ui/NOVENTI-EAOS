"""Create CRM Return Authorization shell RET1 (PHX-G325).

Revision ID: 0059_crm_return_authorization_g325
Revises: 0058_purchase_supplier_ap_bill_g324
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0059_crm_return_authorization_g325"
down_revision: Union[str, Sequence[str], None] = (
    "0058_purchase_supplier_ap_bill_g324"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "return_authorizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_order_id", sa.Uuid(), nullable=False),
        sa.Column("invoice_id", sa.Uuid(), nullable=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status = 'draft'", name="ck_return_authorizations_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_return_authorizations_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_return_authorizations_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            name="fk_return_authorizations_delivery_order_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_return_authorizations_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_return_authorizations_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "delivery_order_id",
            name="uq_return_authorizations_tenant_delivery_order",
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_return_authorizations_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_return_authorizations_tenant_idempotency",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_return_authorizations_tenant_status",
        "return_authorizations",
        ["tenant_id", "status"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_return_authorizations_tenant_status",
        table_name="return_authorizations",
        schema="crm",
    )
    op.drop_table("return_authorizations", schema="crm")
