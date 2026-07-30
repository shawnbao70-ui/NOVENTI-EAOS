"""Establish the EAOS Kernel migration baseline.

Revision ID: 0001_kernel_baseline
Revises:
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "0001_kernel_baseline"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Reserve the baseline before domain tables are introduced."""


def downgrade() -> None:
    """The empty baseline has no schema objects to remove."""
