"""Create Permission tables.

Revision ID: 0004_permission
Revises: 0003_organization
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_permission"
down_revision: Union[str, Sequence[str], None] = "0003_organization"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "grants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("principal_subject_id", sa.Uuid(), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("actions", postgresql.JSONB(), nullable=False),
        sa.Column("conditions_ref", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('active','revoked')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_grants_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["principal_subject_id"],
            ["kernel.subjects.id"],
            name="fk_grants_principal_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_grants"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_grants_tenant_principal",
        "grants",
        ["tenant_id", "principal_subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_grants_tenant_resource",
        "grants",
        ["tenant_id", "resource_type", "resource_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_grants_equivalent_active",
        "grants",
        [
            "tenant_id",
            "principal_subject_id",
            "resource_type",
            sa.text(
                "coalesce(resource_id, '00000000-0000-0000-0000-000000000000'::uuid)"
            ),
            "actions",
        ],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "permission_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("principal_subject_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("effect", sa.String(length=16), nullable=False),
        sa.Column("reason_code", sa.String(length=128), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "effect IN ('allow','deny')",
            name="effect_valid",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_permission_decisions_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["principal_subject_id"],
            ["kernel.subjects.id"],
            name="fk_permission_decisions_principal_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_permission_decisions"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_permission_decisions_tenant_principal",
        "permission_decisions",
        ["tenant_id", "principal_subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_permission_decisions_correlation",
        "permission_decisions",
        ["correlation_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("permission_decisions", schema=SCHEMA)
    op.drop_table("grants", schema=SCHEMA)
