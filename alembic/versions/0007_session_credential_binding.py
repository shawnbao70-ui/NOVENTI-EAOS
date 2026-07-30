"""Bind new sessions to credentials.

Revision ID: 0007_session_credential_binding
Revises: 0006_event_bus
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_session_credential_binding"
down_revision: Union[str, Sequence[str], None] = "0006_event_bus"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("credential_id", sa.Uuid(), nullable=True),
        schema="kernel",
    )
    op.create_foreign_key(
        "fk_sessions_credential_id_credentials",
        "sessions",
        "credentials",
        ["credential_id"],
        ["id"],
        source_schema="kernel",
        referent_schema="kernel",
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_sessions_tenant_credential",
        "sessions",
        ["tenant_id", "credential_id"],
        schema="kernel",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sessions_tenant_credential",
        table_name="sessions",
        schema="kernel",
    )
    op.drop_constraint(
        "fk_sessions_credential_id_credentials",
        "sessions",
        schema="kernel",
        type_="foreignkey",
    )
    op.drop_column("sessions", "credential_id", schema="kernel")
