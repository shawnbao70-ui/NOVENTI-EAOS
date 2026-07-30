"""Create Marketplace technical foundation tables.

Revision ID: 0020_marketplace_m16
Revises: 0019_enterprise_brain_twin_e15
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0020_marketplace_m16"
down_revision: Union[str, Sequence[str], None] = "0019_enterprise_brain_twin_e15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"
LISTING_STATUSES = "'draft','submitted','approved','rejected','published','revoked'"


def upgrade() -> None:
    op.create_table(
        "marketplace_listings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("package_key", sa.String(length=256), nullable=False),
        sa.Column("package_version", sa.String(length=64), nullable=False),
        sa.Column("publisher_subject_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("signature_ref", sa.String(length=512), nullable=True),
        sa.Column("review_notes", sa.String(length=2000), server_default="", nullable=False),
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
        sa.Column("data_scope", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({LISTING_STATUSES})",
            name="ck_marketplace_listings_status_valid",
        ),
        sa.CheckConstraint("version > 0", name="ck_marketplace_listings_version_positive"),
        sa.ForeignKeyConstraint(
            ["publisher_subject_id"],
            [f"{SCHEMA}.subjects.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_marketplace_listings_tenant_package",
        "marketplace_listings",
        ["tenant_id", sa.text("lower(package_key)"), "package_version"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_marketplace_listings_tenant_status",
        "marketplace_listings",
        ["tenant_id", "status"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "marketplace_acquisitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("package_key", sa.String(length=256), nullable=False),
        sa.Column("package_version", sa.String(length=64), nullable=False),
        sa.Column("acquired_by_subject_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_marketplace_acquisitions_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["acquired_by_subject_id"],
            [f"{SCHEMA}.subjects.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            [f"{SCHEMA}.marketplace_listings.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "uq_marketplace_acquisitions_tenant_listing",
        "marketplace_acquisitions",
        ["tenant_id", "listing_id"],
        unique=True,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_marketplace_acquisitions_tenant_listing",
        table_name="marketplace_acquisitions",
        schema=SCHEMA,
    )
    op.drop_table("marketplace_acquisitions", schema=SCHEMA)
    op.drop_index(
        "ix_marketplace_listings_tenant_status",
        table_name="marketplace_listings",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_marketplace_listings_tenant_package",
        table_name="marketplace_listings",
        schema=SCHEMA,
    )
    op.drop_table("marketplace_listings", schema=SCHEMA)
