"""Add Finance GL bridge map + postings (PHX-G321 / GL3).

Revision ID: 0055_finance_gl_bridges_g321
Revises: 0054_finance_gl_period_g320
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0055_finance_gl_bridges_g321"
down_revision: Union[str, Sequence[str], None] = (
    "0054_finance_gl_period_g320"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "gl_bridge_maps",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("ar_control", sa.Uuid(), nullable=False),
        sa.Column("cash", sa.Uuid(), nullable=False),
        sa.Column("revenue", sa.Uuid(), nullable=False),
        sa.Column("tax_payable", sa.Uuid(), nullable=False),
        sa.Column("commission_expense", sa.Uuid(), nullable=False),
        sa.Column("commission_payable", sa.Uuid(), nullable=False),
        sa.Column("fx_gain", sa.Uuid(), nullable=True),
        sa.Column("fx_loss", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0", name="ck_gl_bridge_maps_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_gl_bridge_maps_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_control"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_ar_control",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cash"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_cash",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["revenue"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_revenue",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tax_payable"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_tax_payable",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commission_expense"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_commission_expense",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commission_payable"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_commission_payable",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fx_gain"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_fx_gain",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fx_loss"],
            [f"{SCHEMA}.gl_accounts.id"],
            name="fk_gl_bridge_maps_fx_loss",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema=SCHEMA,
    )
    op.create_table(
        "gl_bridge_postings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("journal_entry_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "source_type IN ("
            "'ar_invoice','ar_receipt','tax_invoice','commission')",
            name="ck_gl_bridge_postings_source_type_valid",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_gl_bridge_postings_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            [f"{SCHEMA}.journal_entries.id"],
            name="fk_gl_bridge_postings_journal",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_gl_bridge_postings_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "source_type",
            "source_id",
            name="uq_gl_bridge_postings_tenant_source",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_gl_bridge_postings_tenant_idem",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_gl_bridge_postings_tenant_source",
        "gl_bridge_postings",
        ["tenant_id", "source_type", "source_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_gl_bridge_postings_tenant_source",
        table_name="gl_bridge_postings",
        schema=SCHEMA,
    )
    op.drop_table("gl_bridge_postings", schema=SCHEMA)
    op.drop_table("gl_bridge_maps", schema=SCHEMA)
