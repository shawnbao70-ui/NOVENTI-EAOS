"""Create oidc_refresh_bindings table (PHX-G63).

Revision ID: 0026_oidc_refresh_bindings_g63
Revises: 0025_idp_issuer_bindings_g56
Create Date: 2026-07-20
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0026_oidc_refresh_bindings_g63"
down_revision: Union[str, Sequence[str], None] = "0025_idp_issuer_bindings_g56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "oidc_refresh_bindings",
        sa.Column("eaos_jti", sa.String(length=128), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("id_token", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "refresh_token IS NOT NULL OR id_token IS NOT NULL",
            name="ck_oidc_refresh_bindings_token_present",
        ),
        sa.PrimaryKeyConstraint("eaos_jti"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_oidc_refresh_bindings_updated_at",
        "oidc_refresh_bindings",
        ["updated_at"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_oidc_refresh_bindings_updated_at",
        table_name="oidc_refresh_bindings",
        schema=SCHEMA,
    )
    op.drop_table("oidc_refresh_bindings", schema=SCHEMA)
