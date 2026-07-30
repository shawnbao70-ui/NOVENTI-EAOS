"""Add signing_secret to event_subscriptions for webhook HMAC (PHX-E22).

Revision ID: 0023_event_webhook_hmac_e22
Revises: 0022_marketplace_m17_commercial
Create Date: 2026-07-19
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0023_event_webhook_hmac_e22"
down_revision: Union[str, Sequence[str], None] = "0022_marketplace_m17_commercial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.add_column(
        "event_subscriptions",
        sa.Column("signing_secret", sa.String(length=256), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("event_subscriptions", "signing_secret", schema=SCHEMA)
