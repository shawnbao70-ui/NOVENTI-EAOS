"""Create CRM Quote Convert C5 persistence (PHX-G298).

Revision ID: 0034_crm_quote_convert_g298
Revises: 0033_crm_quote_g297
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0034_crm_quote_convert_g298"
down_revision: Union[str, Sequence[str], None] = "0033_crm_quote_g297"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quote_conversions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("quote_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("quote_version", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('ready','consumed')",
            name="ck_quote_conversions_status_valid",
        ),
        sa.CheckConstraint(
            "quote_version > 0",
            name="ck_quote_conversions_quote_version_positive",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_quote_conversions_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_quote_conversions_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            name="fk_quote_conversions_quote_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            name="fk_quote_conversions_requirement_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_quote_conversions_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "quote_id",
            name="uq_quote_conversions_tenant_quote",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_quote_conversions_tenant_idempotency",
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_quote_conversions_tenant_status",
        "quote_conversions",
        ["tenant_id", "status"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_quote_conversions_tenant_status",
        table_name="quote_conversions",
        schema="crm",
    )
    op.drop_table("quote_conversions", schema="crm")
