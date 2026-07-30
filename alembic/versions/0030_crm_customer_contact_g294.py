"""Create noventi.crm Customer + Contact C1 persistence (PHX-G294).

Revision ID: 0030_crm_customer_contact_g294
Revises: 0029_eaos_declared_roles_g90
Create Date: 2026-07-24
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0030_crm_customer_contact_g294"
down_revision: Union[str, Sequence[str], None] = "0029_eaos_declared_roles_g90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"
STATUSES = "'active','archived'"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("owner_subject_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_customers_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_customers_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_customers_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_customers_id_tenant_id"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_crm_customers_tenant_code_ci",
        "customers",
        ["tenant_id", sa.text("lower(code)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_customers_tenant_status",
        "customers",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "contacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_contacts_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_contacts_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_contacts_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_contacts_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_contacts_id_tenant_id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_contacts_tenant_customer",
        "contacts",
        ["tenant_id", "customer_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_contacts_tenant_status",
        "contacts",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_contacts_tenant_status",
        table_name="contacts",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_crm_contacts_tenant_customer",
        table_name="contacts",
        schema=SCHEMA,
    )
    op.drop_table("contacts", schema=SCHEMA)
    op.drop_index(
        "ix_crm_customers_tenant_status",
        table_name="customers",
        schema=SCHEMA,
    )
    op.drop_index(
        "uq_crm_customers_tenant_code_ci",
        table_name="customers",
        schema=SCHEMA,
    )
    op.drop_table("customers", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
