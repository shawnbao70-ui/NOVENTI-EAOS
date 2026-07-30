"""Create CRM confirm approval policy C12 (PHX-G305).

Revision ID: 0041_crm_confirm_approval_hook_g305
Revises: 0040_crm_commercial_hold_g304
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0041_crm_confirm_approval_hook_g305"
down_revision: Union[str, Sequence[str], None] = "0040_crm_commercial_hold_g304"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_confirm_policies",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "confirm_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "version > 0", name="ck_tenant_confirm_policies_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["kernel.tenants.id"],
            name="fk_tenant_confirm_policies_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id"),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_table("tenant_confirm_policies", schema="crm")
