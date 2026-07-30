"""Add Finance bank statement recon shell (PHX-G323 / GL5).

Revision ID: 0057_finance_gl_bank_recon_g323
Revises: 0056_finance_gl_fx_revaluation_g322
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0057_finance_gl_bank_recon_g323"
down_revision: Union[str, Sequence[str], None] = (
    "0056_finance_gl_fx_revaluation_g322"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "bank_statements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("account_ref", sa.String(length=128), nullable=False),
        sa.Column(
            "statement_date", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('open','reconciled')",
            name="ck_bank_statements_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_bank_statements_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_bank_statements_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_bank_statements_id_tenant"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_bank_statements_tenant_status",
        "bank_statements",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "bank_statement_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("statement_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("matched_journal_line_id", sa.Uuid(), nullable=True),
        sa.Column("matched_receipt_id", sa.Uuid(), nullable=True),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('unmatched','matched','cleared')",
            name="ck_bank_statement_lines_status_valid",
        ),
        sa.CheckConstraint(
            "amount != 0", name="ck_bank_statement_lines_amount_nonzero"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_bank_statement_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["statement_id"],
            [f"{SCHEMA}.bank_statements.id"],
            name="fk_bank_statement_lines_statement",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_bank_statement_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "statement_id",
            "line_no",
            name="uq_bank_statement_lines_statement_line_no",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_bank_statement_lines_tenant_statement",
        "bank_statement_lines",
        ["tenant_id", "statement_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_bank_statement_lines_tenant_statement",
        table_name="bank_statement_lines",
        schema=SCHEMA,
    )
    op.drop_table("bank_statement_lines", schema=SCHEMA)
    op.drop_index(
        "ix_finance_bank_statements_tenant_status",
        table_name="bank_statements",
        schema=SCHEMA,
    )
    op.drop_table("bank_statements", schema=SCHEMA)
