"""Add CRM Customer commercial_hold gate C11 (PHX-G304).

Revision ID: 0040_crm_commercial_hold_g304
Revises: 0039_crm_ar_invoice_g303
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0040_crm_commercial_hold_g304"
down_revision: Union[str, Sequence[str], None] = "0039_crm_ar_invoice_g303"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column(
            "commercial_hold",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )
    op.create_index(
        "ix_crm_customers_tenant_commercial_hold",
        "customers",
        ["tenant_id", "commercial_hold"],
        schema="crm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_crm_customers_tenant_commercial_hold",
        table_name="customers",
        schema="crm",
    )
    op.drop_column("customers", "commercial_hold", schema="crm")
