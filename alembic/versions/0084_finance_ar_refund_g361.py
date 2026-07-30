"""Create AR refunds linked to issued credit notes (PHX-G361).

Revision ID: 0084_finance_ar_refund_g361
Revises: 0083_finance_tax_red_credit_g360
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0084_finance_ar_refund_g361"
down_revision: Union[str, Sequence[str], None] = (
    "0083_finance_tax_red_credit_g360"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "finance"


def upgrade() -> None:
    op.create_table(
        "ar_refunds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("credit_note_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_key", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_ar_refunds_amount_positive"),
        sa.CheckConstraint(
            "status IN ('draft','posted')", name="ck_ar_refunds_status_valid"
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_ar_refunds_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_ar_refunds_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["credit_note_id", "tenant_id"],
            ["finance.ar_credit_notes.id", "finance.ar_credit_notes.tenant_id"],
            name="fk_ar_refunds_credit_note_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            name="fk_ar_refunds_customer_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "tenant_id", name="uq_ar_refunds_id_tenant"),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_ar_refunds_tenant_idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id", "post_key", name="uq_ar_refunds_tenant_post_key"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_refunds_tenant_status",
        "ar_refunds",
        ["tenant_id", "status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_finance_ar_refunds_tenant_credit_note",
        "ar_refunds",
        ["tenant_id", "credit_note_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_ar_refunds_tenant_credit_note",
        table_name="ar_refunds",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_finance_ar_refunds_tenant_status",
        table_name="ar_refunds",
        schema=SCHEMA,
    )
    op.drop_table("ar_refunds", schema=SCHEMA)
