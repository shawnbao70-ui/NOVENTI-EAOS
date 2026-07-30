"""Create Event outbox and dead-letter tables; extend delivery status.

Revision ID: 0015_event_outbox_dlq
Revises: 0014_knowledge_k10
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0015_event_outbox_dlq"
down_revision: Union[str, Sequence[str], None] = "0014_knowledge_k10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.drop_constraint(
        "status_valid",
        "event_deliveries",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "status_valid",
        "event_deliveries",
        "status IN ('delivered','failed','dead')",
        schema=SCHEMA,
    )

    op.create_table(
        "event_outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("event_name", sa.String(255), nullable=False),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("producer", sa.String(255), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("leased_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("leased_by", sa.String(255), nullable=True),
        sa.Column("last_error_code", sa.String(128), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','leased','dispatched','dead')",
            name="status_valid",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="attempt_count_non_negative"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_event_outbox_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_event_outbox"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_event_outbox_claim",
        "event_outbox",
        ["tenant_id", "status", "available_at"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_event_outbox_event_id",
        "event_outbox",
        ["event_id"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "event_dead_letters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("subscriber_id", sa.String(255), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replayed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["event_id", "tenant_id"],
            ["kernel.events.event_id", "kernel.events.tenant_id"],
            name="fk_event_dead_letters_event_id_tenant_id_events",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_event_dead_letters"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_event_dead_letters_tenant",
        "event_dead_letters",
        ["tenant_id", "created_at"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_event_dead_letters_open",
        "event_dead_letters",
        ["tenant_id", "event_id", "subscriber_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("replayed_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_event_dead_letters_open",
        table_name="event_dead_letters",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_event_dead_letters_tenant",
        table_name="event_dead_letters",
        schema=SCHEMA,
    )
    op.drop_table("event_dead_letters", schema=SCHEMA)
    op.drop_index("ix_event_outbox_event_id", table_name="event_outbox", schema=SCHEMA)
    op.drop_index("ix_event_outbox_claim", table_name="event_outbox", schema=SCHEMA)
    op.drop_table("event_outbox", schema=SCHEMA)
    op.drop_constraint(
        "status_valid",
        "event_deliveries",
        schema=SCHEMA,
        type_="check",
    )
    op.create_check_constraint(
        "status_valid",
        "event_deliveries",
        "status IN ('delivered','failed')",
        schema=SCHEMA,
    )
