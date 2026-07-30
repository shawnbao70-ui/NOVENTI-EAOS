"""Add CRM Quote Issue publish gate C13 (PHX-G306).

Revision ID: 0042_crm_quote_issue_g306
Revises: 0041_crm_confirm_approval_hook_g305
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0042_crm_quote_issue_g306"
down_revision: Union[str, Sequence[str], None] = (
    "0041_crm_confirm_approval_hook_g305"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.drop_constraint(
        "ck_quotes_status_valid", "quotes", schema=SCHEMA, type_="check"
    )
    op.add_column(
        "quotes",
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "quotes",
        sa.Column("issue_key", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_quotes_status_valid",
        "quotes",
        "status IN ('draft','issued','archived')",
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_quotes_tenant_issue_key",
        "quotes",
        ["tenant_id", "issue_key"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE crm.quotes SET status = 'draft', issued_at = NULL, "
            "issue_key = NULL WHERE status = 'issued'"
        )
    )
    op.drop_constraint(
        "uq_quotes_tenant_issue_key", "quotes", schema=SCHEMA, type_="unique"
    )
    op.drop_constraint(
        "ck_quotes_status_valid", "quotes", schema=SCHEMA, type_="check"
    )
    op.drop_column("quotes", "issue_key", schema=SCHEMA)
    op.drop_column("quotes", "issued_at", schema=SCHEMA)
    op.create_check_constraint(
        "ck_quotes_status_valid",
        "quotes",
        "status IN ('draft','archived')",
        schema=SCHEMA,
    )
