"""Create Purchase AP Bill Line AP2 (PHX-G329).

Revision ID: 0060_purchase_ap_bill_line_g329
Revises: 0059_crm_return_authorization_g325
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0060_purchase_ap_bill_line_g329"
down_revision: Union[str, Sequence[str], None] = (
    "0059_crm_return_authorization_g325"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "purchase"


def upgrade() -> None:
    op.create_table(
        "ap_bill_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("ap_bill_id", sa.Uuid(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active','archived')",
            name="ck_ap_bill_lines_status_valid",
        ),
        sa.CheckConstraint(
            "line_number > 0", name="ck_ap_bill_lines_line_number_positive"
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_ap_bill_lines_quantity_positive"
        ),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_ap_bill_lines_unit_price_non_negative",
        ),
        sa.CheckConstraint(
            "amount >= 0", name="ck_ap_bill_lines_amount_non_negative"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ap_bill_lines_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ap_bill_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            name="fk_ap_bill_lines_bill_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ap_bill_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "ap_bill_id",
            "line_number",
            name="uq_ap_bill_lines_tenant_bill_line_number",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_purchase_ap_bill_lines_tenant_bill",
        "ap_bill_lines",
        ["tenant_id", "ap_bill_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_ap_bill_lines_tenant_bill",
        table_name="ap_bill_lines",
        schema=SCHEMA,
    )
    op.drop_table("ap_bill_lines", schema=SCHEMA)
