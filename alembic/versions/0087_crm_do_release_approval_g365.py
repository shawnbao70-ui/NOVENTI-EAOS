"""Require approved Workflow action for tenant-configured DO.release (PHX-G365).

Revision ID: 0087_crm_do_release_approval_g365
Revises: 0086_crm_so_confirm_approval_g364
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0087_crm_do_release_approval_g365"
down_revision: Union[str, Sequence[str], None] = (
    "0086_crm_so_confirm_approval_g364"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_confirm_policies",
        sa.Column(
            "do_release_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_column(
        "tenant_confirm_policies",
        "do_release_approval_required",
        schema="crm",
    )
