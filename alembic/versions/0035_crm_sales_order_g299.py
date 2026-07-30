"""Create CRM Sales Order trace C6 persistence (PHX-G299).

Revision ID: 0035_crm_sales_order_g299
Revises: 0034_crm_quote_convert_g298
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0035_crm_sales_order_g299"
down_revision: Union[str, Sequence[str], None] = "0034_crm_quote_convert_g298"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("conversion_id", sa.Uuid(), nullable=False),
        sa.Column("quote_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status = 'created'", name="ck_sales_orders_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_sales_orders_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_sales_orders_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["conversion_id", "tenant_id"],
            ["crm.quote_conversions.id", "crm.quote_conversions.tenant_id"],
            name="fk_sales_orders_conversion_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            name="fk_sales_orders_quote_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            name="fk_sales_orders_requirement_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_sales_orders_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "conversion_id",
            name="uq_sales_orders_tenant_conversion",
        ),
        sa.UniqueConstraint(
            "tenant_id", "quote_id", name="uq_sales_orders_tenant_quote"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_sales_orders_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_sales_orders_tenant_idempotency",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_sales_orders_tenant_status",
        "sales_orders",
        ["tenant_id", "status"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_sales_orders_tenant_status",
        table_name="sales_orders",
        schema="crm",
    )
    op.drop_table("sales_orders", schema="crm")
