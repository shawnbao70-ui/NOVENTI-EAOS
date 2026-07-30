"""Create noventi.crm Requirement C3 persistence (PHX-G296).

Revision ID: 0032_crm_requirement_g296
Revises: 0031_crm_opportunity_g295
Create Date: 2026-07-24
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0032_crm_requirement_g296"
down_revision: Union[str, Sequence[str], None] = "0031_crm_opportunity_g295"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"
STATUSES = "'active','archived'"


def upgrade() -> None:
    op.create_table(
        "requirements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=4000), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            f"status IN ({STATUSES})", name="ck_requirements_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_requirements_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_requirements_tenant_id_tenants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id", "tenant_id"],
            ["crm.opportunities.id", "crm.opportunities.tenant_id"],
            name="fk_requirements_opportunity_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_requirements_id_tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_requirements_tenant_id_code"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_requirements_tenant_opportunity",
        "requirements",
        ["tenant_id", "opportunity_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_crm_requirements_tenant_status",
        "requirements",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_requirements_tenant_status",
        table_name="requirements",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_crm_requirements_tenant_opportunity",
        table_name="requirements",
        schema=SCHEMA,
    )
    op.drop_table("requirements", schema=SCHEMA)
