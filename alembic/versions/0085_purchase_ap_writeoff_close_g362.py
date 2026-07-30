"""Persist AP write-offs and enable AP bill close (PHX-G362).

Revision ID: 0085_purchase_ap_writeoff_close_g362
Revises: 0084_finance_ar_refund_g361
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0085_purchase_ap_writeoff_close_g362"
down_revision: Union[str, Sequence[str], None] = (
    "0084_finance_ar_refund_g361"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.add_column(
        "ap_bills",
        sa.Column(
            "write_off_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_ap_bills_write_off_amount_non_negative",
        "ap_bills",
        "write_off_amount >= 0",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "ck_ap_bills_paid_amount_not_over_total",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_ap_bills_settlement_not_over_total",
        "ap_bills",
        "paid_amount + write_off_amount <= total_amount",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_ap_bills_status_valid",
        "ap_bills",
        "status IN ('draft','posted','partially_paid','paid','closed')",
        schema=SCHEMA,
    )
    op.create_table(
        "ap_write_offs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("ap_bill_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("amount > 0", name="ck_ap_write_offs_amount_positive"),
        sa.CheckConstraint("version > 0", name="ck_ap_write_offs_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ap_write_offs_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            name="fk_ap_write_offs_bill_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_ap_write_offs_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ap_write_offs_tenant_idempotency_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_ap_write_offs_tenant_bill",
        "ap_write_offs",
        ["tenant_id", "ap_bill_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE purchase.ap_bills SET status = 'posted' WHERE status = 'closed'"
        )
    )
    op.drop_index(
        "ix_purchase_ap_write_offs_tenant_bill",
        table_name="ap_write_offs",
        schema=SCHEMA,
    )
    op.drop_table("ap_write_offs", schema=SCHEMA)
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
    op.drop_constraint(
        "ck_ap_bills_settlement_not_over_total",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "ck_ap_bills_paid_amount_not_over_total",
        "ap_bills",
        "paid_amount <= total_amount",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "ck_ap_bills_write_off_amount_non_negative",
        "ap_bills",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("ap_bills", "write_off_amount", schema=SCHEMA)
