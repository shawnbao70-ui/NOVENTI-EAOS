"""Create noventi.crm Quote C4 persistence (PHX-G297).

Revision ID: 0033_crm_quote_g297
Revises: 0032_crm_requirement_g296
Create Date: 2026-07-24
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0033_crm_quote_g297"
down_revision: Union[str, Sequence[str], None] = "0032_crm_requirement_g296"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("notes", sa.String(length=4000), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('draft','archived')", name="ck_quotes_status_valid"
        ),
        sa.CheckConstraint("version > 0", name="ck_quotes_version_positive"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_quotes_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            name="fk_quotes_requirement_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_quotes_id_tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_quotes_tenant_id_code"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_quotes_tenant_requirement",
        "quotes",
        ["tenant_id", "requirement_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_quotes_tenant_status",
        "quotes",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_quotes_tenant_status", table_name="quotes", schema=SCHEMA
    )
    op.drop_index(
        "ix_crm_quotes_tenant_requirement", table_name="quotes", schema=SCHEMA
    )
    op.drop_table("quotes", schema=SCHEMA)
