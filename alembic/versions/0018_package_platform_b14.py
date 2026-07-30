"""Create Package Platform tables.

Revision ID: 0018_package_platform_b14
Revises: 0017_smart_terminal_t13
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0018_package_platform_b14"
down_revision: Union[str, Sequence[str], None] = "0017_smart_terminal_t13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
MANIFEST_STATUSES = "'draft','published','deprecated'"
INSTALL_STATUSES = "'installed','disabled'"
PACKAGE_TYPES = "'industry','business','ai','integration'"


def upgrade() -> None:
    op.create_table(
        "package_manifests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("package_key", sa.String(length=256), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("package_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "surfaces_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "actions_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "required_permissions_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column(
            "declared_events_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version_number", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({MANIFEST_STATUSES})",
            name="ck_package_manifests_status_valid",
        ),
        sa.CheckConstraint(
            f"package_type IN ({PACKAGE_TYPES})",
            name="ck_package_manifests_package_type_valid",
        ),
        sa.CheckConstraint(
            "version_number > 0",
            name="ck_package_manifests_version_positive",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_package_manifests_tenant_key_version",
        "package_manifests",
        ["tenant_id", sa.text("lower(package_key)"), "version"],
        unique=True,
        schema=SCHEMA,
    )

    op.create_table(
        "package_installations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("manifest_id", sa.Uuid(), nullable=False),
        sa.Column("package_key", sa.String(length=256), nullable=False),
        sa.Column("manifest_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version_number", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({INSTALL_STATUSES})",
            name="ck_package_installations_status_valid",
        ),
        sa.CheckConstraint(
            "version_number > 0",
            name="ck_package_installations_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["manifest_id"],
            [f"{SCHEMA}.package_manifests.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_package_installations_tenant_key",
        "package_installations",
        ["tenant_id", "package_key"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_package_installations_tenant_status",
        "package_installations",
        ["tenant_id", "status"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_package_installations_tenant_status",
        table_name="package_installations",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_package_installations_tenant_key",
        table_name="package_installations",
        schema=SCHEMA,
    )
    op.drop_table("package_installations", schema=SCHEMA)
    op.drop_index(
        "uq_package_manifests_tenant_key_version",
        table_name="package_manifests",
        schema=SCHEMA,
    )
    op.drop_table("package_manifests", schema=SCHEMA)
