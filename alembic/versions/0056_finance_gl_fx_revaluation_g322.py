"""Add Finance GL FX revaluation shell (PHX-G322 / GL4).

Revision ID: 0056_finance_gl_fx_revaluation_g322
Revises: 0055_finance_gl_bridges_g321
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0056_finance_gl_fx_revaluation_g322"
down_revision: Union[str, Sequence[str], None] = (
    "0055_finance_gl_bridges_g321"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "gl_fx_revaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("period_id", sa.Uuid(), nullable=False),
        sa.Column("from_currency", sa.String(length=3), nullable=False),
        sa.Column("to_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("journal_entry_id", sa.Uuid(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('draft','posted')",
            name="ck_gl_fx_revaluations_status_valid",
        ),
        sa.CheckConstraint(
            "side IN ('gain','loss')",
            name="ck_gl_fx_revaluations_side_valid",
        ),
        sa.CheckConstraint(
            "amount > 0", name="ck_gl_fx_revaluations_amount_positive"
        ),
        sa.CheckConstraint(
            "rate > 0", name="ck_gl_fx_revaluations_rate_positive"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_gl_fx_revaluations_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_gl_fx_revaluations_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["period_id"],
            [f"{SCHEMA}.gl_periods.id"],
            name="fk_gl_fx_revaluations_period",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            [f"{SCHEMA}.journal_entries.id"],
            name="fk_gl_fx_revaluations_journal",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_gl_fx_revaluations_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_gl_fx_revaluations_tenant_idem",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "post_key",
            name="uq_gl_fx_revaluations_tenant_post_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_gl_fx_revaluations_tenant_period",
        "gl_fx_revaluations",
        ["tenant_id", "period_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_gl_fx_revaluations_tenant_period",
        table_name="gl_fx_revaluations",
        schema=SCHEMA,
    )
    op.drop_table("gl_fx_revaluations", schema=SCHEMA)
