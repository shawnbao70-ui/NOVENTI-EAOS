"""Add Finance tax rates and tax authority port (PHX-G317 / Tax2).

Revision ID: 0052_finance_tax_rate_authority_port_g317
Revises: 0051_finance_tax_invoice_shell_g316
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0052_finance_tax_rate_authority_port_g317"
down_revision: Union[str, Sequence[str], None] = (
    "0051_finance_tax_invoice_shell_g316"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.add_column(
        "tax_invoices",
        sa.Column("tax_code", sa.String(length=64), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "tax_invoices",
        sa.Column("authority_ref", sa.String(length=128), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "tax_invoices",
        sa.Column("authority_status", sa.String(length=32), nullable=True),
        schema=SCHEMA,
    )
    op.create_table(
        "tax_rates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("tax_code", sa.String(length=64), nullable=False),
        sa.Column("tax_name", sa.String(length=128), nullable=False),
        sa.Column("rate_percent", sa.Numeric(9, 4), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "rate_percent >= 0", name="ck_tax_rates_rate_percent_non_negative"
        ),
        sa.CheckConstraint(
            "status IN ('active','archived')",
            name="ck_tax_rates_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_tax_rates_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tax_rates_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_tax_rates_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "tax_code", name="uq_tax_rates_tenant_tax_code"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_tax_rates_tenant_status",
        "tax_rates",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "tenant_tax_authority_policies",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "tax_authority_required",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_tenant_tax_authority_policies_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tenant_tax_authority_policies_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("tenant_tax_authority_policies", schema=SCHEMA)
    op.drop_index(
        "ix_finance_tax_rates_tenant_status",
        table_name="tax_rates",
        schema=SCHEMA,
    )
    op.drop_table("tax_rates", schema=SCHEMA)
    op.drop_column("tax_invoices", "authority_status", schema=SCHEMA)
    op.drop_column("tax_invoices", "authority_ref", schema=SCHEMA)
    op.drop_column("tax_invoices", "tax_code", schema=SCHEMA)
