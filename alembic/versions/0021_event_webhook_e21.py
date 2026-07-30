"""Add delivery_url to event_subscriptions for webhook transport.

Revision ID: 0021_event_webhook_e21
Revises: 0020_marketplace_m16
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0021_event_webhook_e21"
down_revision: Union[str, Sequence[str], None] = "0020_marketplace_m16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "kernel"


def upgrade() -> None:
    op.add_column(
        "event_subscriptions",
        sa.Column("delivery_url", sa.String(length=2048), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("event_subscriptions", "delivery_url", schema=SCHEMA)
