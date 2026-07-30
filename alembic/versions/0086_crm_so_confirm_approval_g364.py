"""Require approved Workflow action for tenant-configured SO.confirm (PHX-G364).

Revision ID: 0086_crm_so_confirm_approval_g364
Revises: 0085_purchase_ap_writeoff_close_g362
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0086_crm_so_confirm_approval_g364"
down_revision: Union[str, Sequence[str], None] = (
    "0085_purchase_ap_writeoff_close_g362"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_confirm_policies",
        sa.Column(
            "so_confirm_workflow_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_column(
        "tenant_confirm_policies",
        "so_confirm_workflow_approval_required",
        schema="crm",
    )
