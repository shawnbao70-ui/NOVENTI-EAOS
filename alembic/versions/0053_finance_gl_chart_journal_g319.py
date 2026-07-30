"""Add Finance GL chart of accounts and journal shell (PHX-G319 / GL1).

Revision ID: 0053_finance_gl_chart_journal_g319
Revises: 0052_finance_tax_rate_authority_port_g317
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0053_finance_gl_chart_journal_g319"
down_revision: Union[str, Sequence[str], None] = (
    "0052_finance_tax_rate_authority_port_g317"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "gl_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("account_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "account_type IN ('asset','liability','equity','revenue','expense')",
            name="ck_gl_accounts_account_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('active','archived')",
            name="ck_gl_accounts_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_gl_accounts_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_gl_accounts_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_gl_accounts_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_gl_accounts_tenant_code"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_gl_accounts_tenant_status",
        "gl_accounts",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("memo", sa.String(length=500), nullable=True),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "status IN ('draft','posted')",
            name="ck_journal_entries_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_journal_entries_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_journal_entries_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_journal_entries_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_journal_entries_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_journal_entries_tenant_idempotency_key",
        ),
        sa.UniqueConstraint(
            "tenant_id", "post_key", name="uq_journal_entries_tenant_post_key"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_journal_entries_tenant_status",
        "journal_entries",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_table(
        "journal_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("journal_entry_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("debit", sa.Numeric(18, 2), nullable=False),
        sa.Column("credit", sa.Numeric(18, 2), nullable=False),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "debit >= 0", name="ck_journal_lines_debit_non_negative"
        ),
        sa.CheckConstraint(
            "credit >= 0", name="ck_journal_lines_credit_non_negative"
        ),
        sa.CheckConstraint(
            "((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0))",
            name="ck_journal_lines_debit_xor_credit",
        ),
        sa.CheckConstraint(
            "line_no > 0", name="ck_journal_lines_line_no_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_journal_lines_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["finance.journal_entries.id"],
            name="fk_journal_lines_entry",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["finance.gl_accounts.id"],
            name="fk_journal_lines_account",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_journal_lines_id_tenant"
        ),
        sa.UniqueConstraint(
            "journal_entry_id",
            "line_no",
            name="uq_journal_lines_entry_line_no",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_journal_lines_tenant_entry",
        "journal_lines",
        ["tenant_id", "journal_entry_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_journal_lines_tenant_entry",
        table_name="journal_lines",
        schema=SCHEMA,
    )
    op.drop_table("journal_lines", schema=SCHEMA)
    op.drop_index(
        "ix_finance_journal_entries_tenant_status",
        table_name="journal_entries",
        schema=SCHEMA,
    )
    op.drop_table("journal_entries", schema=SCHEMA)
    op.drop_index(
        "ix_finance_gl_accounts_tenant_status",
        table_name="gl_accounts",
        schema=SCHEMA,
    )
    op.drop_table("gl_accounts", schema=SCHEMA)
