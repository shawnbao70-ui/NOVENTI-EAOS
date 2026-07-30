"""Create Event Bus tables.

Revision ID: 0006_event_bus
Revises: 0005_workflow
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_event_bus"
down_revision: Union[str, Sequence[str], None] = "0005_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("event_name", sa.String(255), nullable=False),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("producer", sa.String(255), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_events_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("event_id", name="pk_events"),
        sa.UniqueConstraint(
            "event_id",
            "tenant_id",
            name="uq_events_event_id_tenant_id",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_events_tenant_name_time",
        "events",
        ["tenant_id", "event_name", "timestamp"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_events_correlation",
        "events",
        ["correlation_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "event_subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subscriber_id", sa.String(255), nullable=False),
        sa.Column("subscriber_subject_id", sa.Uuid(), nullable=False),
        sa.Column("event_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_event_subscriptions_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_subject_id"],
            ["kernel.subjects.id"],
            name="fk_event_subscriptions_subscriber_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_event_subscriptions"),
        sa.UniqueConstraint(
            "tenant_id",
            "subscriber_id",
            "event_name",
            name="uq_event_sub_tenant_subscriber_name",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_event_subscriptions_tenant_name",
        "event_subscriptions",
        ["tenant_id", "event_name"],
        schema=SCHEMA,
    )

    op.create_table(
        "event_deliveries",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("subscriber_id", sa.String(255), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error_code", sa.String(128), nullable=True),
        sa.CheckConstraint(
            "status IN ('delivered','failed')",
            name="status_valid",
        ),
        sa.CheckConstraint("attempt_count > 0", name="attempt_count_positive"),
        sa.ForeignKeyConstraint(
            ["event_id", "tenant_id"],
            ["kernel.events.event_id", "kernel.events.tenant_id"],
            name="fk_event_deliveries_event_id_tenant_id_events",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "event_id",
            "subscriber_id",
            name="pk_event_deliveries",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_event_deliveries_tenant_status",
        "event_deliveries",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("event_deliveries", schema=SCHEMA)
    op.drop_table("event_subscriptions", schema=SCHEMA)
    op.drop_table("events", schema=SCHEMA)
