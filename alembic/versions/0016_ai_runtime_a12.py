"""Create AI Runtime tables.

Revision ID: 0016_ai_runtime_a12
Revises: 0015_event_outbox_dlq
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0016_ai_runtime_a12"
down_revision: Union[str, Sequence[str], None] = "0015_event_outbox_dlq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
RUN_STATUSES = (
    "'planned','running','pending_approval','completed','failed','cancelled'"
)


def upgrade() -> None:
    op.create_table(
        "ai_agent_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("goal", sa.String(1000), nullable=False),
        sa.Column("plan_summary", sa.String(2000), server_default="", nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("approval_ref", sa.String(128), nullable=True),
        sa.Column("last_error_code", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({RUN_STATUSES})", name="status_valid"),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ai_agent_runs_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_ai_agent_runs_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ai_agent_runs"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_agent_runs_tenant_subject",
        "ai_agent_runs",
        ["tenant_id", "subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_agent_runs_tenant_status",
        "ai_agent_runs",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )

    op.create_table(
        "ai_tool_declarations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("high_impact", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ai_tool_declarations_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ai_tool_declarations"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_ai_tool_declarations_tenant_name",
        "ai_tool_declarations",
        ["tenant_id", sa.text("lower(name)")],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "ai_memory_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ai_memory_entries_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["kernel.ai_agent_runs.id"],
            name="fk_ai_memory_entries_run_id_ai_agent_runs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ai_memory_entries"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_ai_memory_entries_run_key",
        "ai_memory_entries",
        ["tenant_id", "run_id", sa.text("lower(key)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_memory_entries_run",
        "ai_memory_entries",
        ["tenant_id", "run_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_memory_entries_run", table_name="ai_memory_entries", schema=SCHEMA)
    op.drop_index(
        "uq_ai_memory_entries_run_key",
        table_name="ai_memory_entries",
        schema=SCHEMA,
    )
    op.drop_table("ai_memory_entries", schema=SCHEMA)
    op.drop_index(
        "uq_ai_tool_declarations_tenant_name",
        table_name="ai_tool_declarations",
        schema=SCHEMA,
    )
    op.drop_table("ai_tool_declarations", schema=SCHEMA)
    op.drop_index(
        "ix_ai_agent_runs_tenant_status",
        table_name="ai_agent_runs",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_ai_agent_runs_tenant_subject",
        table_name="ai_agent_runs",
        schema=SCHEMA,
    )
    op.drop_table("ai_agent_runs", schema=SCHEMA)
