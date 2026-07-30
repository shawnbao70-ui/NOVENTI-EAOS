"""Create Enterprise Brain and Digital Twin tables.

Revision ID: 0019_enterprise_brain_twin_e15
Revises: 0018_package_platform_b14
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0019_enterprise_brain_twin_e15"
down_revision: Union[str, Sequence[str], None] = "0018_package_platform_b14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
TWIN_STATUSES = "'active','superseded','archived'"
INSIGHT_KINDS = "'insight','recommendation','simulation'"


def upgrade() -> None:
    op.create_table(
        "twin_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("entity_ref", sa.String(length=512), nullable=False),
        sa.Column(
            "state_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("source_ref", sa.String(length=512), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({TWIN_STATUSES})", name="ck_twin_snapshots_status_valid"),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_twin_snapshots_confidence_range",
        ),
        sa.CheckConstraint("version > 0", name="ck_twin_snapshots_version_positive"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_twin_snapshots_tenant_entity",
        "twin_snapshots",
        ["tenant_id", "entity_ref"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_twin_snapshots_tenant_status",
        "twin_snapshots",
        ["tenant_id", "status"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "brain_insights",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.String(length=2000), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_ref", sa.String(length=512), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("advisory", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("bias_notes", sa.String(length=2000), server_default="", nullable=False),
        sa.Column("twin_ref", sa.Uuid(), nullable=True),
        sa.Column(
            "knowledge_refs_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "details_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"kind IN ({INSIGHT_KINDS})", name="ck_brain_insights_kind_valid"),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_brain_insights_confidence_range",
        ),
        sa.CheckConstraint("advisory = true", name="ck_brain_insights_advisory_required"),
        sa.CheckConstraint("version > 0", name="ck_brain_insights_version_positive"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["twin_ref"],
            [f"{SCHEMA}.twin_snapshots.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_brain_insights_tenant_kind",
        "brain_insights",
        ["tenant_id", "kind"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_brain_insights_tenant_kind", table_name="brain_insights", schema=SCHEMA)
    op.drop_table("brain_insights", schema=SCHEMA)
    op.drop_index("ix_twin_snapshots_tenant_status", table_name="twin_snapshots", schema=SCHEMA)
    op.drop_index("ix_twin_snapshots_tenant_entity", table_name="twin_snapshots", schema=SCHEMA)
    op.drop_table("twin_snapshots", schema=SCHEMA)
