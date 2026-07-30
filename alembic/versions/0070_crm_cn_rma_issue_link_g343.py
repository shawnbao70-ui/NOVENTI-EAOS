"""Trace issuing a credit note linked from a CRM return authorization.

Revision ID: 0070_crm_cn_rma_issue_link_g343
Revises: 0069_finance_ar_allocation_g342
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0070_crm_cn_rma_issue_link_g343"
down_revision: Union[str, Sequence[str], None] = (
    "0069_finance_ar_allocation_g342"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.add_column(
        "return_authorizations",
        sa.Column("credit_note_issued_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column(
        "return_authorizations",
        "credit_note_issued_at",
        schema=SCHEMA,
    )
