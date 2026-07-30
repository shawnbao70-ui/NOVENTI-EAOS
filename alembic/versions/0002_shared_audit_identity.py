"""Create Shared Audit and Identity tables.

Revision ID: 0002_shared_audit_identity
Revises: 0001_kernel_baseline
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_shared_audit_identity"
down_revision: Union[str, Sequence[str], None] = "0001_kernel_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS kernel"))

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("resource", sa.String(length=255), nullable=False),
        sa.Column("result", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_audit_events_tenant_timestamp",
        "audit_events",
        ["tenant_id", "timestamp"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_audit_events_correlation_id",
        "audit_events",
        ["correlation_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("subject_type", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column(
            "is_platform_managed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "subject_type IN ('human','ai_employee','service','device','application','plugin')",
            name="subject_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active','archived','revoked','ended')",
            name="status_valid",
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.PrimaryKeyConstraint("id", name="pk_subjects"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_subjects_tenant_status",
        "subjects",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )

    op.create_table(
        "subject_external_refs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("system", sa.String(length=100), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_subject_external_refs_subject_id_subjects",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_subject_external_refs"),
        sa.UniqueConstraint(
            "system",
            "external_id",
            name="uq_subject_external_refs_system_external_id",
        ),
        schema=SCHEMA,
    )

    op.create_table(
        "credentials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("credential_kind", sa.String(length=64), nullable=False),
        sa.Column("secret_handle", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('active','archived','revoked','ended')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_credentials_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_credentials"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_credentials_tenant_subject",
        "credentials",
        ["tenant_id", "subject_id"],
        schema=SCHEMA,
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correlation_id_at_issue", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["kernel.subjects.id"],
            name="fk_sessions_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_sessions_tenant_subject",
        "sessions",
        ["tenant_id", "subject_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_sessions_tenant_expires",
        "sessions",
        ["tenant_id", "expires_at"],
        schema=SCHEMA,
    )

    op.create_table(
        "ai_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("ai_subject_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("management_policy", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.CheckConstraint(
            "mode IN ('assign','reassign','inherit','archive')",
            name="mode_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active','archived','revoked','ended')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["ai_subject_id"],
            ["kernel.subjects.id"],
            name="fk_ai_assignments_ai_subject_id_subjects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ai_assignments"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_assignments_tenant_status",
        "ai_assignments",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_ai_assignments_ai_status",
        "ai_assignments",
        ["ai_subject_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_ai_assignments_tenant_ai_active",
        "ai_assignments",
        ["tenant_id", "ai_subject_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_table("ai_assignments", schema=SCHEMA)
    op.drop_table("sessions", schema=SCHEMA)
    op.drop_table("credentials", schema=SCHEMA)
    op.drop_table("subject_external_refs", schema=SCHEMA)
    op.drop_table("subjects", schema=SCHEMA)
    op.drop_table("audit_events", schema=SCHEMA)
    op.execute(sa.text("DROP SCHEMA kernel"))
