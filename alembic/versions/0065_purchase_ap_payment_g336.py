"""Create Purchase AP payment shell (PHX-G336).

Revision ID: 0065_purchase_ap_payment_g336
Revises: 0064_purchase_three_way_match_g334
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0065_purchase_ap_payment_g336"
down_revision: Union[str, Sequence[str], None] = (
    "0064_purchase_three_way_match_g334"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.drop_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        "status IN ('draft','posted','partially_paid','paid')",
        schema=SCHEMA,
    )
    op.create_table(
        "ap_payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ap_bill_id", sa.Uuid(), nullable=True),
        sa.Column("ap_bill_version", sa.Integer(), nullable=True),
        sa.Column("apply_key", sa.Uuid(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_ap_payments_amount_positive"),
        sa.CheckConstraint(
            "status IN ('draft','applied')", name="ck_ap_payments_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ap_payments_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ap_payments_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["purchase.suppliers.id", "purchase.suppliers.tenant_id"],
            name="fk_ap_payments_supplier_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            name="fk_ap_payments_bill_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ap_payments_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ap_payments_tenant_idempotency",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_ap_payments_tenant_bill",
        "ap_payments",
        ["tenant_id", "ap_bill_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_purchase_ap_payments_tenant_apply_key",
        "ap_payments",
        ["tenant_id", "apply_key"],
        unique=True,
        postgresql_where=sa.text("apply_key IS NOT NULL"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_purchase_ap_payments_tenant_apply_key",
        table_name="ap_payments",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_purchase_ap_payments_tenant_bill",
        table_name="ap_payments",
        schema=SCHEMA,
    )
    op.drop_table("ap_payments", schema=SCHEMA)
    op.drop_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        "status IN ('draft')",
        schema=SCHEMA,
    )
