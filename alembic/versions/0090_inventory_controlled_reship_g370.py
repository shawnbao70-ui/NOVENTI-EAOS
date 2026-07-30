"""Relax DO ship posting uniqueness for controlled reship (PHX-G370).

Revision ID: 0090_inventory_controlled_reship_g370
Revises: 0089_inventory_ship_pod_g367
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0090_inventory_controlled_reship_g370"
down_revision: Union[str, Sequence[str], None] = "0089_inventory_ship_pod_g367"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "inventory"


def upgrade() -> None:
    op.drop_constraint(
        "uq_delivery_ship_postings_tenant_do",
        "delivery_ship_postings",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_index(
        "ix_inventory_ship_postings_tenant_do",
        table_name="delivery_ship_postings",
        schema=SCHEMA,
    )
    op.create_index(
        "ix_inventory_ship_postings_tenant_do_status",
        "delivery_ship_postings",
        ["tenant_id", "delivery_order_id", "status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_ship_postings_tenant_do_status",
        table_name="delivery_ship_postings",
        schema=SCHEMA,
    )
    op.create_index(
        "ix_inventory_ship_postings_tenant_do",
        "delivery_ship_postings",
        ["tenant_id", "delivery_order_id"],
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_delivery_ship_postings_tenant_do",
        "delivery_ship_postings",
        ["tenant_id", "delivery_order_id"],
        schema=SCHEMA,
    )
