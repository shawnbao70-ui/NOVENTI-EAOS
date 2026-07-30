"""Link restocked CRM returns to Finance AR credit notes (PHX-G337).

Revision ID: 0066_crm_return_credit_note_g337
Revises: 0065_purchase_ap_payment_g336
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0066_crm_return_credit_note_g337"
down_revision: Union[str, Sequence[str], None] = (
    "0065_purchase_ap_payment_g336"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "crm"


def upgrade() -> None:
    op.add_column(
        "return_authorizations",
        sa.Column("credit_note_id", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "return_authorizations",
        sa.Column("credit_note_key", sa.Uuid(), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_return_authorizations_credit_note_tenant",
        "return_authorizations",
        "ar_credit_notes",
        ["credit_note_id", "tenant_id"],
        ["id", "tenant_id"],
        source_schema=SCHEMA,
        referent_schema="finance",
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_return_authorizations_tenant_credit_note",
        "return_authorizations",
        ["tenant_id", "credit_note_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "uq_crm_return_authorizations_tenant_credit_note_key",
        "return_authorizations",
        ["tenant_id", "credit_note_key"],
        unique=True,
        schema=SCHEMA,
        postgresql_where=sa.text("credit_note_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_crm_return_authorizations_tenant_credit_note_key",
        table_name="return_authorizations",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "uq_return_authorizations_tenant_credit_note",
        "return_authorizations",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_constraint(
        "fk_return_authorizations_credit_note_tenant",
        "return_authorizations",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("return_authorizations", "credit_note_key", schema=SCHEMA)
    op.drop_column("return_authorizations", "credit_note_id", schema=SCHEMA)
