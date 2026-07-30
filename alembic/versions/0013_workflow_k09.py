"""Workflow K09 binding, SLA, compensation and concurrency.

Revision ID: 0013_workflow_k09
Revises: 0012_permission_policy_scope
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0013_workflow_k09"
down_revision: Union[str, Sequence[str], None] = "0012_permission_policy_scope"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.drop_constraint(
        "status_valid",
        "workflow_instances",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "status_valid",
        "workflow_instances",
        "status IN ('running','pending_approval','approved','rejected',"
        "'cancelled','completed','compensating','compensated')",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "status_valid",
        "workflow_signal_receipts",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "status_valid",
        "workflow_signal_receipts",
        "resulting_status IN ('running','pending_approval','approved','rejected',"
        "'cancelled','completed','compensating','compensated')",
        schema=SCHEMA,
    )

    op.add_column(
        "workflow_instances",
        sa.Column("approval_plan_version", sa.String(length=64), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "workflow_instances",
        sa.Column("approval_scope", sa.String(length=255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "workflow_instances",
        sa.Column("approval_expires_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_workflow_instances_active_business_key",
        "workflow_instances",
        ["tenant_id", "business_key"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text(
            "business_key IS NOT NULL AND status IN "
            "('running','pending_approval','approved','compensating')"
        ),
    )

    op.add_column(
        "workflow_tasks",
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("workflow_tasks", "due_at", schema=SCHEMA)
    op.drop_index(
        "uq_workflow_instances_active_business_key",
        table_name="workflow_instances",
        schema=SCHEMA,
    )
    op.drop_column("workflow_instances", "approval_expires_at", schema=SCHEMA)
    op.drop_column("workflow_instances", "approval_scope", schema=SCHEMA)
    op.drop_column("workflow_instances", "approval_plan_version", schema=SCHEMA)
    op.drop_constraint(
        "status_valid",
        "workflow_signal_receipts",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "status_valid",
        "workflow_signal_receipts",
        "resulting_status IN ('running','pending_approval','approved',"
        "'rejected','cancelled','completed')",
        schema=SCHEMA,
    )
    op.drop_constraint("status_valid", "workflow_instances", schema=SCHEMA, type_="check")
    op.create_check_constraint(
        "status_valid",
        "workflow_instances",
        "status IN ('running','pending_approval','approved',"
        "'rejected','cancelled','completed')",
        schema=SCHEMA,
    )
