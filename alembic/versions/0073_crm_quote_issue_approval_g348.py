"""Require approved Workflow action for tenant-configured Quote.issue (PHX-G348).

Revision ID: 0073_crm_quote_issue_approval_g348
Revises: 0072_finance_ar_writeoff_close_g347
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0073_crm_quote_issue_approval_g348"
down_revision: Union[str, Sequence[str], None] = (
    "0072_finance_ar_writeoff_close_g347"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_confirm_policies",
        sa.Column(
            "quote_issue_approval_required",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        schema="crm",
    )


def downgrade() -> None:
    op.drop_column(
        "tenant_confirm_policies",
        "quote_issue_approval_required",
        schema="crm",
    )
