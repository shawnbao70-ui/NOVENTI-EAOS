"""Create kernel.eaos_declared_roles table (PHX-G90).

Revision ID: 0029_eaos_declared_roles_g90
Revises: 0028_tenant_idp_binding_priority_g78
Create Date: 2026-07-20
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0029_eaos_declared_roles_g90"
down_revision: Union[str, Sequence[str], None] = "0028_tenant_idp_binding_priority_g78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
STATUSES = "'active','disabled'"


def upgrade() -> None:
    op.create_table(
        "eaos_declared_roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})",
            name="ck_eaos_declared_roles_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_eaos_declared_roles_version_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_eaos_declared_roles_name_lower",
        "eaos_declared_roles",
        [sa.text("lower(name)")],
        unique=True,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_eaos_declared_roles_status",
        "eaos_declared_roles",
        ["status"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_eaos_declared_roles_status",
        table_name="eaos_declared_roles",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_eaos_declared_roles_name_lower",
        table_name="eaos_declared_roles",
        schema=SCHEMA,
    )
    op.drop_table("eaos_declared_roles", schema=SCHEMA)
