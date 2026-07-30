"""Create Marketplace commercial policy tables (PHX-M17).

Revision ID: 0022_marketplace_m17_commercial
Revises: 0021_event_webhook_e21
Create Date: 2026-07-19
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0022_marketplace_m17_commercial"
down_revision: Union[str, Sequence[str], None] = "0021_event_webhook_e21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.create_table(
        "marketplace_listing_pricing",
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("pricing_model", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("version > 0", name="ck_marketplace_pricing_version_positive"),
        sa.CheckConstraint(
            "pricing_model = 'fixed'",
            name="ck_marketplace_pricing_model_fixed",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            [f"{SCHEMA}.marketplace_listings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("listing_id"),
        schema=SCHEMA,
    )

    op.create_table(
        "marketplace_listing_revenue_share",
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("platform_share_bps", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_marketplace_revenue_share_version_positive",
        ),
        sa.CheckConstraint(
            "platform_share_bps >= 0 AND platform_share_bps <= 5000",
            name="ck_marketplace_revenue_share_bps_range",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            [f"{SCHEMA}.marketplace_listings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("listing_id"),
        schema=SCHEMA,
    )

    op.create_table(
        "marketplace_invoices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("billing_cycle", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("issued_by_subject_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("version > 0", name="ck_marketplace_invoices_version_positive"),
        sa.CheckConstraint(
            "status IN ('issued','void')",
            name="ck_marketplace_invoices_status_valid",
        ),
        sa.CheckConstraint(
            "billing_cycle = 'immediate'",
            name="ck_marketplace_invoices_billing_immediate",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            [f"{SCHEMA}.marketplace_listings.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["issued_by_subject_id"],
            [f"{SCHEMA}.subjects.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_marketplace_invoices_tenant_listing",
        "marketplace_invoices",
        ["tenant_id", "listing_id"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "marketplace_disputes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(length=2000), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("opened_by_subject_id", sa.Uuid(), nullable=False),
        sa.Column("resolution", sa.String(length=2000), server_default="", nullable=False),
        sa.Column("resolved_by_subject_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("version > 0", name="ck_marketplace_disputes_version_positive"),
        sa.CheckConstraint(
            "status IN ('open','resolved')",
            name="ck_marketplace_disputes_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            [f"{SCHEMA}.marketplace_listings.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["opened_by_subject_id"],
            [f"{SCHEMA}.subjects.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by_subject_id"],
            [f"{SCHEMA}.subjects.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], [f"{SCHEMA}.tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_marketplace_disputes_tenant_listing",
        "marketplace_disputes",
        ["tenant_id", "listing_id"],
        unique=False,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_marketplace_disputes_tenant_listing",
        table_name="marketplace_disputes",
        schema=SCHEMA,
    )
    op.drop_table("marketplace_disputes", schema=SCHEMA)
    op.drop_index(
        "ix_marketplace_invoices_tenant_listing",
        table_name="marketplace_invoices",
        schema=SCHEMA,
    )
    op.drop_table("marketplace_invoices", schema=SCHEMA)
    op.drop_table("marketplace_listing_revenue_share", schema=SCHEMA)
    op.drop_table("marketplace_listing_pricing", schema=SCHEMA)
