"""Create platform idp_issuer_bindings table (PHX-G56).

Revision ID: 0025_idp_issuer_bindings_g56
Revises: 0024_terminal_extension_sql_g41
Create Date: 2026-07-19
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0025_idp_issuer_bindings_g56"
down_revision: Union[str, Sequence[str], None] = "0024_terminal_extension_sql_g41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
STATUSES = "'active','disabled'"


def upgrade() -> None:
    op.create_table(
        "idp_issuer_bindings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("issuer", sa.String(length=512), nullable=False),
        sa.Column("jwks_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "jwks_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_idp_issuer_bindings_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_idp_issuer_bindings_version_positive",
        ),
        sa.CheckConstraint(
            "jwks_url IS NOT NULL OR jwks_json IS NOT NULL",
            name="ck_idp_issuer_bindings_jwks_present",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_idp_issuer_bindings_issuer_lower",
        "idp_issuer_bindings",
        [sa.text("lower(issuer)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_idp_issuer_bindings_status",
        "idp_issuer_bindings",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_idp_issuer_bindings_status",
        table_name="idp_issuer_bindings",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_idp_issuer_bindings_issuer_lower",
        table_name="idp_issuer_bindings",
        schema=SCHEMA,
    )
    op.drop_table("idp_issuer_bindings", schema=SCHEMA)
