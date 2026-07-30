"""Add ship POD evidence fields and tenant policy (PHX-G367).

Revision ID: 0089_inventory_ship_pod_g367
Revises: 0088_purchase_3wm_tolerance_g366
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0089_inventory_ship_pod_g367"
down_revision: Union[str, Sequence[str], None] = (
    "0088_purchase_3wm_tolerance_g366"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "inventory"


def upgrade() -> None:
    op.add_column(
        "delivery_ship_postings",
        sa.Column("pod_ref", sa.String(length=128), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "delivery_ship_postings",
        sa.Column(
            "pod_captured_at", sa.DateTime(timezone=True), nullable=True
        ),
        schema=SCHEMA,
    )
    op.create_table(
        "tenant_ship_pod_policies",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "ship_pod_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_tenant_ship_pod_policies_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tenant_ship_pod_policies_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("tenant_ship_pod_policies", schema=SCHEMA)
    op.drop_column("delivery_ship_postings", "pod_captured_at", schema=SCHEMA)
    op.drop_column("delivery_ship_postings", "pod_ref", schema=SCHEMA)
