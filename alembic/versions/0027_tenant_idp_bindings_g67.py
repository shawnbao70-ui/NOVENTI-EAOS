"""Create tenant_idp_bindings table (PHX-G67).

Revision ID: 0027_tenant_idp_bindings_g67
Revises: 0026_oidc_refresh_bindings_g63
Create Date: 2026-07-20
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0027_tenant_idp_bindings_g67"
down_revision: Union[str, Sequence[str], None] = "0026_oidc_refresh_bindings_g63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
STATUSES = "'active','disabled'"


def upgrade() -> None:
    op.create_table(
        "tenant_idp_bindings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("issuer", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_tenant_idp_bindings_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_tenant_idp_bindings_version_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_tenant_idp_bindings_tenant_issuer_lower",
        "tenant_idp_bindings",
        ["tenant_id", sa.text("lower(issuer)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_tenant_idp_bindings_tenant_status",
        "tenant_idp_bindings",
        ["tenant_id", "status"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tenant_idp_bindings_tenant_status",
        table_name="tenant_idp_bindings",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_tenant_idp_bindings_tenant_issuer_lower",
        table_name="tenant_idp_bindings",
        schema=SCHEMA,
    )
    op.drop_table("tenant_idp_bindings", schema=SCHEMA)
