"""Persist Platform Identity Governor authorization history.

Revision ID: 0008_platform_identity_governors
Revises: 0007_session_credential_binding
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_platform_identity_governors"
down_revision: Union[str, Sequence[str], None] = "0007_session_credential_binding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_identity_governors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("granted_by_subject_id", sa.Uuid(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("revoked_by_subject_id", sa.Uuid(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(1000), nullable=True),
        sa.CheckConstraint(
            "status IN ('active','revoked')",
            name="ck_platform_identity_governors_status_valid",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_platform_identity_governors"),
        schema="kernel",
    )
    op.create_index(
        "uq_platform_identity_governors_subject_active",
        "platform_identity_governors",
        ["subject_id"],
        unique=True,
        schema="kernel",
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_table("platform_identity_governors", schema="kernel")
