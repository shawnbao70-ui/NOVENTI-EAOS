"""Require approved Workflow action for tenant-configured Quote.convert (PHX-G353).

Revision ID: 0077_crm_quote_convert_approval_g353
Revises: 0076_crm_convert_fx_snapshot_g352
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0077_crm_quote_convert_approval_g353"
down_revision: Union[str, Sequence[str], None] = "0076_crm_convert_fx_snapshot_g352"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_confirm_policies",
        sa.Column(
            "quote_convert_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_column(
        "tenant_confirm_policies",
        "quote_convert_approval_required",
        schema="crm",
    )
