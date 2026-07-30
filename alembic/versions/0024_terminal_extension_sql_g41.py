"""Create terminal_extensions table for Extension Host SQL.

Revision ID: 0024_terminal_extension_sql_g41
Revises: 0023_event_webhook_hmac_e22
Create Date: 2026-07-19
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0024_terminal_extension_sql_g41"
down_revision: Union[str, Sequence[str], None] = "0023_event_webhook_hmac_e22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
EXTENSION_STATUSES = "'registered','active','revoked'"


def upgrade() -> None:
    op.create_table(
        "terminal_extensions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("extension_key", sa.String(length=256), nullable=False),
        sa.Column("extension_version", sa.String(length=64), nullable=False),
        sa.Column("signature_ref", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "declared_capabilities_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "declared_actions_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "allowed_surfaces_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("data_scope", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({EXTENSION_STATUSES})",
            name="ck_terminal_extensions_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_terminal_extensions_version_positive"),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_terminal_extensions_tenant_key",
        "terminal_extensions",
        ["tenant_id", sa.text("lower(extension_key)"), "extension_version"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_terminal_extensions_tenant_status",
        "terminal_extensions",
        ["tenant_id", "status"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_terminal_extensions_tenant_status",
        table_name="terminal_extensions",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_terminal_extensions_tenant_key",
        table_name="terminal_extensions",
        schema=SCHEMA,
    )
    op.drop_table("terminal_extensions", schema=SCHEMA)
