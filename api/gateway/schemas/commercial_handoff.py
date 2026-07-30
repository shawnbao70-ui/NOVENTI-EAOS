"""HTTP DTOs for commercial handoffs (PHX-G339 / G390 / G392)."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RmaCreditNoteHandoffRequest(_ClosedModel):
    authorization_source: Literal["brain", "twin"]
    insight_id: UUID | None = None
    snapshot_id: UUID | None = None
    return_authorization_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID
    human_confirm: Literal[True]

    @model_validator(mode="after")
    def source_identifier_matches(self) -> "RmaCreditNoteHandoffRequest":
        if self.authorization_source == "brain":
            valid = self.insight_id is not None and self.snapshot_id is None
        else:
            valid = self.snapshot_id is not None and self.insight_id is None
        if not valid:
            raise ValueError(
                "authorization_source must match exactly one of insight_id or snapshot_id"
            )
        return self


class RmaCreditNoteHandoffData(_ClosedModel):
    authorization_source: Literal["brain", "twin"]
    authorization_id: UUID
    return_authorization_id: UUID
    credit_note_id: UUID
    authorization_audit_id: UUID | str | None = None


class RmaCreditNoteHandoffEnvelope(_ClosedModel):
    data: RmaCreditNoteHandoffData
    audit_id: UUID | str | None = None


class SoConfirmHandoffRequest(_ClosedModel):
    authorization_source: Literal["brain", "twin"]
    insight_id: UUID | None = None
    snapshot_id: UUID | None = None
    sales_order_id: UUID
    human_confirm: Literal[True]

    @model_validator(mode="after")
    def source_identifier_matches(self) -> "SoConfirmHandoffRequest":
        if self.authorization_source == "brain":
            valid = self.insight_id is not None and self.snapshot_id is None
        else:
            valid = self.snapshot_id is not None and self.insight_id is None
        if not valid:
            raise ValueError(
                "authorization_source must match exactly one of insight_id or snapshot_id"
            )
        return self


class SoConfirmHandoffData(_ClosedModel):
    authorization_source: Literal["brain", "twin"]
    authorization_id: UUID
    sales_order_id: UUID
    sales_order_status: str = Field(min_length=1)
    auto_confirm: Literal[False] = False
    approval_ref: str = Field(min_length=1)
    authorization_audit_id: UUID | str | None = None


class SoConfirmHandoffEnvelope(_ClosedModel):
    data: SoConfirmHandoffData
    audit_id: UUID | str | None = None
