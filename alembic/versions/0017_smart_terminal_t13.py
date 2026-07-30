"""Create Smart Terminal workspace tables.

Revision ID: 0017_smart_terminal_t13
Revises: 0016_ai_runtime_a12
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0017_smart_terminal_t13"
down_revision: Union[str, Sequence[str], None] = "0016_ai_runtime_a12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
SESSION_STATUSES = "'open','closed'"
INTENT_STATUSES = "'draft','previewed','cancelled'"
PREVIEW_STATUSES = "'active','invalidated','committed'"
DEVICE_TRUSTS = "'trusted','untrusted'"


def upgrade() -> None:
    op.create_table(
        "terminal_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("identity_session_id", sa.Uuid(), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("device_trust", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({SESSION_STATUSES})", name="ck_terminal_sessions_status_valid"),
        sa.CheckConstraint(
            f"device_trust IN ({DEVICE_TRUSTS})",
            name="ck_terminal_sessions_device_trust_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_terminal_sessions_version_positive"),
        sa.ForeignKeyConstraint(["subject_id"], [f"{SCHEMA}.subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_terminal_sessions_tenant_subject",
        "terminal_sessions",
        ["tenant_id", "subject_id"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "terminal_intents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("terminal_session_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({INTENT_STATUSES})", name="ck_terminal_intents_status_valid"),
        sa.CheckConstraint("version > 0", name="ck_terminal_intents_version_positive"),
        sa.ForeignKeyConstraint(["subject_id"], [f"{SCHEMA}.subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["terminal_session_id"],
            [f"{SCHEMA}.terminal_sessions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_terminal_intents_tenant_session",
        "terminal_intents",
        ["tenant_id", "terminal_session_id"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "terminal_previews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("intent_id", sa.Uuid(), nullable=False),
        sa.Column("terminal_session_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=256), nullable=False),
        sa.Column("resource_ref", sa.String(length=512), nullable=False),
        sa.Column("plan_version", sa.String(length=128), nullable=False),
        sa.Column("scope", sa.String(length=256), nullable=False),
        sa.Column("impact_summary", sa.String(length=2000), nullable=False),
        sa.Column("high_impact", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("approval_ref", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(f"status IN ({PREVIEW_STATUSES})", name="ck_terminal_previews_status_valid"),
        sa.CheckConstraint("version > 0", name="ck_terminal_previews_version_positive"),
        sa.ForeignKeyConstraint(["intent_id"], [f"{SCHEMA}.terminal_intents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], [f"{SCHEMA}.subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["terminal_session_id"],
            [f"{SCHEMA}.terminal_sessions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_terminal_previews_tenant_intent",
        "terminal_previews",
        ["tenant_id", "intent_id"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_terminal_previews_tenant_intent",
        table_name="terminal_previews",
        schema=SCHEMA,
    )
    op.drop_table("terminal_previews", schema=SCHEMA)
    op.drop_index(
        "ix_terminal_intents_tenant_session",
        table_name="terminal_intents",
        schema=SCHEMA,
    )
    op.drop_table("terminal_intents", schema=SCHEMA)
    op.drop_index(
        "ix_terminal_sessions_tenant_subject",
        table_name="terminal_sessions",
        schema=SCHEMA,
    )
    op.drop_table("terminal_sessions", schema=SCHEMA)
