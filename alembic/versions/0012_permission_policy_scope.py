"""Permission Policy, Scope, Delegation and Explain evidence.

Revision ID: 0012_permission_policy_scope
Revises: 0011_organization_enterprises
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0012_permission_policy_scope"
down_revision: Union[str, Sequence[str], None] = "0011_organization_enterprises"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "policies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('draft','active','deprecated')",
            name="policy_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="policy_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_policies_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_policies"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_policies_tenant_name_version",
        "policies",
        ["tenant_id", sa.text("lower(name)"), "policy_version"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "policy_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("policy_id", sa.Uuid(), nullable=False),
        sa.Column("effect", sa.String(length=16), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=False),
        sa.Column("actions", postgresql.JSONB(), nullable=False),
        sa.Column("scope_level", sa.String(length=32), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=True),
        sa.Column("org_unit_id", sa.Uuid(), nullable=True),
        sa.Column("conditions_ref", sa.String(length=255), nullable=True),
        sa.CheckConstraint("effect IN ('allow','deny')", name="rule_effect_valid"),
        sa.CheckConstraint(
            "scope_level IN ('resource','org_unit','enterprise','tenant')",
            name="rule_scope_valid",
        ),
        sa.ForeignKeyConstraint(
            ["policy_id"],
            ["kernel.policies.id"],
            name="fk_policy_rules_policy_id_policies",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_policy_rules"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_policy_rules_policy",
        "policy_rules",
        ["policy_id"],
        schema=SCHEMA,
    )

    op.add_column(
        "grants",
        sa.Column(
            "scope_level",
            sa.String(length=32),
            server_default="resource",
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column("enterprise_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column("org_unit_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column("parent_grant_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column("delegator_subject_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column(
            "remaining_depth",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "grants",
        sa.Column(
            "delegable",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "remaining_depth_non_negative",
        "grants",
        "remaining_depth >= 0",
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "grant_scope_valid",
        "grants",
        "scope_level IN ('resource','org_unit','enterprise','tenant')",
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_grants_parent_grant_id_grants",
        "grants",
        "grants",
        ["parent_grant_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_grants_delegator_subject_id_subjects",
        "grants",
        "subjects",
        ["delegator_subject_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )

    op.drop_index(
        "uq_grants_equivalent_active",
        table_name="grants",
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
            "scope_level",
            sa.text(
                "coalesce(enterprise_id, '00000000-0000-0000-0000-000000000000'::uuid)"
            ),
            sa.text(
                "coalesce(org_unit_id, '00000000-0000-0000-0000-000000000000'::uuid)"
            ),
            sa.text(
                "coalesce(parent_grant_id, '00000000-0000-0000-0000-000000000000'::uuid)"
            ),
        ],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.add_column(
        "permission_decisions",
        sa.Column("evidence_json", postgresql.JSONB(), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("permission_decisions", "evidence_json", schema=SCHEMA)
    op.drop_index(
        "uq_grants_equivalent_active",
        table_name="grants",
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
    op.drop_constraint(
        "fk_grants_delegator_subject_id_subjects",
        "grants",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_grants_parent_grant_id_grants",
        "grants",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_constraint("grant_scope_valid", "grants", schema=SCHEMA, type_="check")
    op.drop_constraint(
        "remaining_depth_non_negative",
        "grants",
        schema=SCHEMA,
        type_="check",
    )
    for column in (
        "delegable",
        "remaining_depth",
        "delegator_subject_id",
        "parent_grant_id",
        "org_unit_id",
        "enterprise_id",
        "scope_level",
    ):
        op.drop_column("grants", column, schema=SCHEMA)
    op.drop_index("ix_policy_rules_policy", table_name="policy_rules", schema=SCHEMA)
    op.drop_table("policy_rules", schema=SCHEMA)
    op.drop_index(
        "uq_policies_tenant_name_version",
        table_name="policies",
        schema=SCHEMA,
    )
    op.drop_table("policies", schema=SCHEMA)
