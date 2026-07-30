"""Create Knowledge Shared Capability tables.

Revision ID: 0014_knowledge_k10
Revises: 0013_workflow_k09
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0014_knowledge_k10"
down_revision: Union[str, Sequence[str], None] = "0013_workflow_k09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
LAYERS = "'canonical','operational','documentary','derived'"
STATUSES = "'active','archived'"


def upgrade() -> None:
    op.create_table(
        "knowledge_entities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(128), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("layer", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attributes", postgresql.JSONB(), nullable=False),
        sa.Column("labels", postgresql.JSONB(), nullable=False),
        sa.Column("shared_with_subject_ids", postgresql.JSONB(), nullable=False),
        sa.Column("retain_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"layer IN ({LAYERS})", name="layer_valid"),
        sa.CheckConstraint(f"status IN ({STATUSES})", name="status_valid"),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_knowledge_entities_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_knowledge_entities"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_knowledge_entities_tenant_type",
        "knowledge_entities",
        ["tenant_id", "entity_type"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_knowledge_entities_tenant_status",
        "knowledge_entities",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_knowledge_entities_active_type_name",
        "knowledge_entities",
        ["tenant_id", sa.text("lower(entity_type)"), sa.text("lower(name)")],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "knowledge_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("from_entity_id", sa.Uuid(), nullable=False),
        sa.Column("to_entity_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attributes", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({STATUSES})", name="status_valid"),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.CheckConstraint(
            "from_entity_id <> to_entity_id",
            name="no_self_link",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_knowledge_links_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["from_entity_id"],
            ["kernel.knowledge_entities.id"],
            name="fk_knowledge_links_from_entity_id_knowledge_entities",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["to_entity_id"],
            ["kernel.knowledge_entities.id"],
            name="fk_knowledge_links_to_entity_id_knowledge_entities",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_knowledge_links"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_knowledge_links_tenant_from",
        "knowledge_links",
        ["tenant_id", "from_entity_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_knowledge_links_tenant_to",
        "knowledge_links",
        ["tenant_id", "to_entity_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "knowledge_provenance",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_kind", sa.String(16), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("actor_subject_id", sa.Uuid(), nullable=False),
        sa.Column("source_ref", sa.String(512), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=False),
        sa.Column("derived", sa.Boolean(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint(
            "subject_kind IN ('entity','link')",
            name="subject_kind_valid",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_knowledge_provenance_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_subject_id"],
            ["kernel.subjects.id"],
            name="fk_knowledge_provenance_actor_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_knowledge_provenance"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_knowledge_provenance_subject",
        "knowledge_provenance",
        ["tenant_id", "subject_kind", "subject_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_provenance_subject",
        table_name="knowledge_provenance",
        schema=SCHEMA,
    )
    op.drop_table("knowledge_provenance", schema=SCHEMA)
    op.drop_index(
        "ix_knowledge_links_tenant_to",
        table_name="knowledge_links",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_knowledge_links_tenant_from",
        table_name="knowledge_links",
        schema=SCHEMA,
    )
    op.drop_table("knowledge_links", schema=SCHEMA)
    op.drop_index(
        "uq_knowledge_entities_active_type_name",
        table_name="knowledge_entities",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_knowledge_entities_tenant_status",
        table_name="knowledge_entities",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_knowledge_entities_tenant_type",
        table_name="knowledge_entities",
        schema=SCHEMA,
    )
    op.drop_table("knowledge_entities", schema=SCHEMA)
