"""Create CRM Quote Line C7 persistence (PHX-G300).

Revision ID: 0036_crm_quote_line_g300
Revises: 0035_crm_sales_order_g299
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0036_crm_quote_line_g300"
down_revision: Union[str, Sequence[str], None] = "0035_crm_sales_order_g299"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quote_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("quote_id", sa.Uuid(), nullable=False),
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
            name="ck_quote_lines_status_valid",
        ),
        sa.CheckConstraint(
            "line_number > 0", name="ck_quote_lines_line_number_positive"
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_quote_lines_quantity_positive"
        ),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_quote_lines_unit_price_non_negative",
        ),
        sa.CheckConstraint(
            "amount >= 0", name="ck_quote_lines_amount_non_negative"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_quote_lines_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_quote_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            name="fk_quote_lines_quote_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_quote_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "quote_id",
            "line_number",
            name="uq_quote_lines_tenant_quote_line_number",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_quote_lines_tenant_quote",
        "quote_lines",
        ["tenant_id", "quote_id"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_quote_lines_tenant_quote",
        table_name="quote_lines",
        schema="crm",
    )
    op.drop_table("quote_lines", schema="crm")
