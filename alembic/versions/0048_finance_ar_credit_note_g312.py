"""Create Finance AR Credit Note shell N1 (PHX-G312).

Revision ID: 0048_finance_ar_credit_note_g312
Revises: 0047_inventory_do_ship_g311
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0048_finance_ar_credit_note_g312"
down_revision: Union[str, Sequence[str], None] = (
    "0047_inventory_do_ship_g311"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "ar_credit_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_id", sa.Uuid(), nullable=False),
        sa.Column("ar_invoice_version", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issue_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "amount > 0", name="ck_ar_credit_notes_amount_positive"
        ),
        sa.CheckConstraint(
            "status IN ('draft','issued')",
            name="ck_ar_credit_notes_status_valid",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ar_credit_notes_version_positive"
        ),
        sa.CheckConstraint(
            "ar_invoice_version > 0",
            name="ck_ar_credit_notes_invoice_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ar_credit_notes_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_ar_credit_notes_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ar_invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            name="fk_ar_credit_notes_ar_invoice_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "tenant_id", name="uq_ar_credit_notes_id_tenant"
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_ar_credit_notes_tenant_code"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ar_credit_notes_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "issue_key",
            name="uq_ar_credit_notes_tenant_issue_key",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_credit_notes_tenant_status",
        "ar_credit_notes",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_credit_notes_tenant_customer",
        "ar_credit_notes",
        ["tenant_id", "customer_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_ar_credit_notes_tenant_customer",
        table_name="ar_credit_notes",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_ar_credit_notes_tenant_status",
        table_name="ar_credit_notes",
        schema=SCHEMA,
    )
    op.drop_table("ar_credit_notes", schema=SCHEMA)
