"""Require approved Workflow action for tenant-configured DO.ship (PHX-G354).

Revision ID: 0078_inventory_do_ship_approval_g354
Revises: 0077_crm_quote_convert_approval_g353
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0078_inventory_do_ship_approval_g354"
down_revision: Union[str, Sequence[str], None] = "0077_crm_quote_convert_approval_g353"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_confirm_policies",
        sa.Column(
            "do_ship_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_column(
        "tenant_confirm_policies",
        "do_ship_approval_required",
        schema="crm",
    )
