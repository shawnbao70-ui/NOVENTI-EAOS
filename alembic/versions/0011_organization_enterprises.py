"""Separate Enterprise subjects from Tenant isolation boundaries.

Revision ID: 0011_organization_enterprises
Revises: 0010_ai_employee_profiles
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011_organization_enterprises"
down_revision: Union[str, Sequence[str], None] = "0010_ai_employee_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "enterprises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active','suspended','closed','inactive','ended')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_enterprises_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_enterprises"),
        sa.UniqueConstraint(
            "id",
            "tenant_id",
            name="uq_enterprises_id_tenant",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_enterprises_tenant_legal_name_ci",
        "enterprises",
        ["tenant_id", sa.text("lower(legal_name)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "uq_enterprises_primary_per_tenant",
        "enterprises",
        ["tenant_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("is_primary"),
    )

    op.add_column(
        "org_units",
        sa.Column("enterprise_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "memberships",
        sa.Column("enterprise_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )

    op.execute(
        """
        INSERT INTO kernel.enterprises (
            id, tenant_id, legal_name, status, is_primary,
            created_at, updated_at, version
        )
        SELECT
            md5('primary-enterprise-' || t.id::text)::uuid,
            t.id,
            t.legal_name,
            t.status,
            true,
            t.created_at,
            t.updated_at,
            1
        FROM kernel.tenants AS t
        WHERE NOT EXISTS (
            SELECT 1
            FROM kernel.enterprises AS e
            WHERE e.tenant_id = t.id AND e.is_primary
        )
        """
    )
    op.execute(
        """
        UPDATE kernel.org_units AS u
        SET enterprise_id = e.id
        FROM kernel.enterprises AS e
        WHERE e.tenant_id = u.tenant_id
          AND e.is_primary
          AND u.enterprise_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE kernel.memberships AS m
        SET enterprise_id = e.id
        FROM kernel.enterprises AS e
        WHERE e.tenant_id = m.tenant_id
          AND e.is_primary
          AND m.enterprise_id IS NULL
        """
    )
    op.alter_column(
        "org_units",
        "enterprise_id",
        nullable=False,
        schema=SCHEMA,
    )
    op.alter_column(
        "memberships",
        "enterprise_id",
        nullable=False,
        schema=SCHEMA,
    )

    op.create_foreign_key(
        "fk_org_units_enterprise_tenant",
        "org_units",
        "enterprises",
        ["enterprise_id", "tenant_id"],
        ["id", "tenant_id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_org_units_tenant_enterprise",
        "org_units",
        ["tenant_id", "enterprise_id"],
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_org_units_id_tenant_enterprise",
        "org_units",
        ["id", "tenant_id", "enterprise_id"],
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_org_units_parent_tenant_enterprise",
        "org_units",
        "org_units",
        ["parent_unit_id", "tenant_id", "enterprise_id"],
        ["id", "tenant_id", "enterprise_id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )

    op.create_foreign_key(
        "fk_memberships_enterprise_tenant",
        "memberships",
        "enterprises",
        ["enterprise_id", "tenant_id"],
        ["id", "tenant_id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_memberships_tenant_enterprise",
        "memberships",
        ["tenant_id", "enterprise_id"],
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_memberships_unit_tenant_enterprise",
        "memberships",
        "org_units",
        ["org_unit_id", "tenant_id", "enterprise_id"],
        ["id", "tenant_id", "enterprise_id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.drop_index(
        "uq_memberships_active_unit",
        table_name="memberships",
        schema=SCHEMA,
    )
    op.drop_index(
        "uq_memberships_active_no_unit",
        table_name="memberships",
        schema=SCHEMA,
    )
    op.create_index(
        "uq_memberships_active_unit",
        "memberships",
        ["tenant_id", "enterprise_id", "subject_id", "org_unit_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active' AND org_unit_id IS NOT NULL"),
    )
    op.create_index(
        "uq_memberships_active_no_unit",
        "memberships",
        ["tenant_id", "enterprise_id", "subject_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active' AND org_unit_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_memberships_active_unit",
        table_name="memberships",
        schema=SCHEMA,
    )
    op.drop_index(
        "uq_memberships_active_no_unit",
        table_name="memberships",
        schema=SCHEMA,
    )
    op.create_index(
        "uq_memberships_active_unit",
        "memberships",
        ["tenant_id", "subject_id", "org_unit_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active' AND org_unit_id IS NOT NULL"),
    )
    op.create_index(
        "uq_memberships_active_no_unit",
        "memberships",
        ["tenant_id", "subject_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active' AND org_unit_id IS NULL"),
    )
    op.drop_constraint(
        "fk_memberships_unit_tenant_enterprise",
        "memberships",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_index(
        "ix_memberships_tenant_enterprise",
        table_name="memberships",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "fk_memberships_enterprise_tenant",
        "memberships",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("memberships", "enterprise_id", schema=SCHEMA)
    op.drop_constraint(
        "fk_org_units_parent_tenant_enterprise",
        "org_units",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_org_units_id_tenant_enterprise",
        "org_units",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_index(
        "ix_org_units_tenant_enterprise",
        table_name="org_units",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "fk_org_units_enterprise_tenant",
        "org_units",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("org_units", "enterprise_id", schema=SCHEMA)
    op.drop_table("enterprises", schema=SCHEMA)
