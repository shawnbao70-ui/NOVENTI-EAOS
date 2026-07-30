"""Persist governed AI employee profiles.

Revision ID: 0010_ai_employee_profiles
Revises: 0009_ai_assignment_semantics
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010_ai_employee_profiles"
down_revision: Union[str, Sequence[str], None] = "0009_ai_assignment_semantics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_employee_profiles",
        sa.Column("ai_subject_id", sa.Uuid(), nullable=False),
        sa.Column("capabilities_profile_ref", sa.String(255), nullable=False),
        sa.Column("owner_policy_ref", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "version > 0",
            name="ck_ai_employee_profiles_version_positive",
        ),
        sa.ForeignKeyConstraint(
            ["ai_subject_id"],
            ["kernel.subjects.id"],
            name="fk_ai_employee_profiles_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "ai_subject_id",
            name="pk_ai_employee_profiles",
        ),
        schema="kernel",
    )


def downgrade() -> None:
    op.drop_table("ai_employee_profiles", schema="kernel")
