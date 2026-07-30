"""Add CRM Delivery Order Release status gate C14 (PHX-G307).

Revision ID: 0043_crm_delivery_order_release_g307
Revises: 0042_crm_quote_issue_g306
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0043_crm_delivery_order_release_g307"
down_revision: Union[str, Sequence[str], None] = (
    "0042_crm_quote_issue_g306"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.drop_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        schema=SCHEMA,
        type_="check",
    )
    op.add_column(
        "delivery_orders",
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "delivery_orders",
        sa.Column("release_key", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        "status IN ('draft','released')",
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_delivery_orders_tenant_release_key",
        "delivery_orders",
        ["tenant_id", "release_key"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.delivery_orders SET status = 'draft', "
            "released_at = NULL, release_key = NULL WHERE status = 'released'"
        )
    )
    op.drop_constraint(
        "uq_delivery_orders_tenant_release_key",
        "delivery_orders",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("delivery_orders", "release_key", schema=SCHEMA)
    op.drop_column("delivery_orders", "released_at", schema=SCHEMA)
    op.create_check_constraint(
        "ck_delivery_orders_status_valid",
        "delivery_orders",
        "status = 'draft'",
        schema=SCHEMA,
    )
