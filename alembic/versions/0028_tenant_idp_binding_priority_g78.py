"""Add priority to tenant_idp_bindings (PHX-G78).

Revision ID: 0028_tenant_idp_binding_priority_g78
Revises: 0027_tenant_idp_bindings_g67
Create Date: 2026-07-20
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0028_tenant_idp_binding_priority_g78"
down_revision: Union[str, Sequence[str], None] = "0027_tenant_idp_bindings_g67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    # Alembic creates version_num as VARCHAR(32), but this revision ID is longer.
    # Widen it before Alembic records this revision at the end of the migration.
    op.alter_column(
        "alembic_version",
        "version_num",
        existing_type=sa.String(length=32),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
    op.add_column(
        "tenant_idp_bindings",
        sa.Column(
            "priority",
            sa.Integer(),
            server_default="100",
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_tenant_idp_bindings_priority_nonneg",
        "tenant_idp_bindings",
        "priority >= 0",
        schema=SCHEMA,
    )
    op.create_index(
        "ix_tenant_idp_bindings_tenant_priority",
        "tenant_idp_bindings",
        ["tenant_id", "priority"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tenant_idp_bindings_tenant_priority",
        table_name="tenant_idp_bindings",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "ck_tenant_idp_bindings_priority_nonneg",
        "tenant_idp_bindings",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("tenant_idp_bindings", "priority", schema=SCHEMA)
