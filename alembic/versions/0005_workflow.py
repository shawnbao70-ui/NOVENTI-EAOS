"""Create Workflow tables.

Revision ID: 0005_workflow
Revises: 0004_permission
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_workflow"
down_revision: Union[str, Sequence[str], None] = "0004_permission"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
WORKFLOW_STATUSES = (
    "'running','pending_approval','approved','rejected','cancelled','completed'"
)


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("document_ref", sa.String(512), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('active','deprecated')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_workflow_definitions_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_definitions"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_workflow_definitions_tenant_name_version",
        "workflow_definitions",
        ["tenant_id", sa.text("lower(name)"), "version"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("tenant_id IS NOT NULL"),
    )
    op.create_index(
        "uq_workflow_definitions_platform_name_version",
        "workflow_definitions",
        [sa.text("lower(name)"), "version"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("tenant_id IS NULL"),
    )

    op.create_table(
        "workflow_instances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("definition_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("initiator_subject_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("business_key", sa.String(255), nullable=True),
        sa.Column("current_task_id", sa.Uuid(), nullable=True),
        sa.Column("approval_principal_subject_id", sa.Uuid(), nullable=True),
        sa.Column("approval_action", sa.String(128), nullable=True),
        sa.Column("approval_resource_ref", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({WORKFLOW_STATUSES})",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["definition_id"],
            ["kernel.workflow_definitions.id"],
            name="fk_workflow_instances_definition_id_workflow_definitions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_workflow_instances_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["initiator_subject_id"],
            ["kernel.subjects.id"],
            name="fk_workflow_instances_initiator_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["approval_principal_subject_id"],
            ["kernel.subjects.id"],
            name="fk_workflow_instances_approval_principal_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_instances"),
        sa.UniqueConstraint(
            "id",
            "tenant_id",
            name="uq_workflow_instances_id_tenant_id",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_workflow_instances_tenant_status",
        "workflow_instances",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_workflow_instances_tenant_business",
        "workflow_instances",
        ["tenant_id", "business_key"],
        schema=SCHEMA,
    )

    op.create_table(
        "workflow_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("instance_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("assignee_subject_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("decision_comment", sa.String(1000), nullable=True),
        sa.Column("escalated_from_subject_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected','cancelled')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            name="fk_workflow_tasks_instance_id_tenant_id_workflow_instances",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["assignee_subject_id"],
            ["kernel.subjects.id"],
            name="fk_workflow_tasks_assignee_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["escalated_from_subject_id"],
            ["kernel.subjects.id"],
            name="fk_workflow_tasks_escalated_from_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_tasks"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_workflow_tasks_tenant_assignee",
        "workflow_tasks",
        ["tenant_id", "assignee_subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_workflow_tasks_tenant_status",
        "workflow_tasks",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )

    op.create_table(
        "workflow_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("instance_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            name="fk_workflow_history_instance_id_tenant_id_workflow_instances",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_workflow_history_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_history"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_workflow_history_instance_time",
        "workflow_history",
        ["instance_id", "timestamp"],
        schema=SCHEMA,
    )

    op.create_table(
        "workflow_signal_receipts",
        sa.Column("instance_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("resulting_status", sa.String(32), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"resulting_status IN ({WORKFLOW_STATUSES})",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            name="fk_wf_signal_receipt_instance_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "instance_id",
            "idempotency_key",
            name="pk_workflow_signal_receipts",
        ),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("workflow_signal_receipts", schema=SCHEMA)
    op.drop_table("workflow_history", schema=SCHEMA)
    op.drop_table("workflow_tasks", schema=SCHEMA)
    op.drop_table("workflow_instances", schema=SCHEMA)
    op.drop_table("workflow_definitions", schema=SCHEMA)
