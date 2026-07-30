"""Enforce exclusive AI assignment and persist INHERIT lineage.

Revision ID: 0009_ai_assignment_semantics
Revises: 0008_platform_identity_governors
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009_ai_assignment_semantics"
down_revision: Union[str, Sequence[str], None] = "0008_platform_identity_governors"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ai_assignments",
        sa.Column("predecessor_assignment_id", sa.Uuid(), nullable=True),
        schema="kernel",
    )
    op.create_foreign_key(
        "fk_ai_assignment_predecessor",
        "ai_assignments",
        "ai_assignments",
        ["predecessor_assignment_id"],
        ["id"],
        source_schema="kernel",
        referent_schema="kernel",
        ondelete="RESTRICT",
    )
    op.drop_index(
        "uq_ai_assignments_tenant_ai_active",
        table_name="ai_assignments",
        schema="kernel",
    )
    op.create_index(
        "uq_ai_assignments_ai_active",
        "ai_assignments",
        ["ai_subject_id"],
        unique=True,
        schema="kernel",
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_ai_assignments_ai_active",
        table_name="ai_assignments",
        schema="kernel",
    )
    op.create_index(
        "uq_ai_assignments_tenant_ai_active",
        "ai_assignments",
        ["tenant_id", "ai_subject_id"],
        unique=True,
        schema="kernel",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.drop_constraint(
        "fk_ai_assignment_predecessor",
        "ai_assignments",
        schema="kernel",
        type_="foreignkey",
    )
    op.drop_column(
        "ai_assignments",
        "predecessor_assignment_id",
        schema="kernel",
    )
