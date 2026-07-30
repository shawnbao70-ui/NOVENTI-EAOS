"""Create noventi.crm Opportunity C2 persistence (PHX-G295).

Revision ID: 0031_crm_opportunity_g295
Revises: 0030_crm_customer_contact_g294
Create Date: 2026-07-24
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0031_crm_opportunity_g295"
down_revision: Union[str, Sequence[str], None] = "0030_crm_customer_contact_g294"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"
STATUSES = "'active','archived'"


def upgrade() -> None:
    op.create_table(
        "opportunities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("owner_subject_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_opportunities_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_opportunities_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_opportunities_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_opportunities_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_opportunities_id_tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_opportunities_tenant_id_code",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_opportunities_tenant_customer",
        "opportunities",
        ["tenant_id", "customer_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_opportunities_tenant_status",
        "opportunities",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_opportunities_tenant_status",
        table_name="opportunities",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_crm_opportunities_tenant_customer",
        table_name="opportunities",
        schema=SCHEMA,
    )
    op.drop_table("opportunities", schema=SCHEMA)
