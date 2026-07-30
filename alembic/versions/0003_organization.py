"""Create Organization tables.

Revision ID: 0003_organization
Revises: 0002_shared_audit_identity
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_organization"
down_revision: Union[str, Sequence[str], None] = "0002_shared_audit_identity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("region_policy_ref", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active','suspended','closed','inactive','ended')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.PrimaryKeyConstraint("id", name="pk_tenants"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_tenants_legal_name_ci",
        "tenants",
        [sa.text("lower(legal_name)")],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "org_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("parent_unit_id", sa.Uuid(), nullable=True),
        sa.Column("unit_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "unit_type IN ('hq','group','branch','department','other')",
            name="unit_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active','suspended','closed','inactive','ended')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_org_units_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_unit_id", "tenant_id"],
            ["kernel.org_units.id", "kernel.org_units.tenant_id"],
            name="fk_org_units_parent_unit_id_tenant_id_org_units",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_org_units"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_org_units_id_tenant_id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_org_units_tenant_parent",
        "org_units",
        ["tenant_id", "parent_unit_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_org_units_tenant_status",
        "org_units",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("org_unit_id", sa.Uuid(), nullable=True),
        sa.Column("membership_role_label", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active','suspended','closed','inactive','ended')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_memberships_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_memberships_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["org_unit_id", "tenant_id"],
            ["kernel.org_units.id", "kernel.org_units.tenant_id"],
            name="fk_memberships_org_unit_id_tenant_id_org_units",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memberships"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_memberships_tenant_subject",
        "memberships",
        ["tenant_id", "subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_memberships_tenant_unit",
        "memberships",
        ["tenant_id", "org_unit_id"],
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


def downgrade() -> None:
    op.drop_table("memberships", schema=SCHEMA)
    op.drop_table("org_units", schema=SCHEMA)
    op.drop_table("tenants", schema=SCHEMA)
