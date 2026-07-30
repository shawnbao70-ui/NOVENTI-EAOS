"""Add Finance GL period + journal period bind (PHX-G320 / GL2).

Revision ID: 0054_finance_gl_period_g320
Revises: 0053_finance_gl_chart_journal_g319
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0054_finance_gl_period_g320"
down_revision: Union[str, Sequence[str], None] = (
    "0053_finance_gl_chart_journal_g319"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "gl_periods",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('open','closed')",
            name="ck_gl_periods_status_valid",
        ),
        sa.CheckConstraint(
            "start_at < end_at", name="ck_gl_periods_start_before_end"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_gl_periods_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_gl_periods_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_gl_periods_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_gl_periods_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id", "close_key", name="uq_gl_periods_tenant_close_key"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_gl_periods_tenant_status",
        "gl_periods",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.add_column(
        "journal_entries",
        sa.Column("period_id", sa.Uuid(), nullable=False),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_journal_entries_period",
        "journal_entries",
        "gl_periods",
        ["period_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_finance_journal_entries_tenant_period",
        "journal_entries",
        ["tenant_id", "period_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_journal_entries_tenant_period",
        table_name="journal_entries",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "fk_journal_entries_period",
        "journal_entries",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("journal_entries", "period_id", schema=SCHEMA)
    op.drop_index(
        "ix_finance_gl_periods_tenant_status",
        table_name="gl_periods",
        schema=SCHEMA,
    )
    op.drop_table("gl_periods", schema=SCHEMA)
