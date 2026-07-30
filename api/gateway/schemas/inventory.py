"""HTTP schemas for Inventory DO Ship I1 (PHX-G311)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AdjustStockRequest(_ClosedModel):
    sales_order_line_id: UUID
    quantity_delta: Decimal = Field(max_digits=18, decimal_places=4)
    idempotency_key: UUID


class ShipDeliveryOrderRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    approval_ref: str | None = Field(default=None, min_length=1, max_length=64)
    pod_ref: str | None = Field(default=None, min_length=1, max_length=128)


class UnshipDeliveryOrderRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class SetShipPodPolicyRequest(_ClosedModel):
    ship_pod_required: bool
    expected_version: int = Field(ge=0)


class StockBalanceView(_ClosedModel):
    sales_order_line_id: UUID
    on_hand: Decimal
    version: int
    updated_at: datetime


class StockBalanceEnvelope(_ClosedModel):
    data: StockBalanceView
    audit_id: UUID | None = None


class StockOnHandEnvelope(_ClosedModel):
    data: Decimal
    audit_id: UUID | None = None


class DeliveryShipPostingView(_ClosedModel):
    id: UUID
    delivery_order_id: UUID
    sales_order_id: UUID
    status: Literal["shipped", "unshipped"]
    shipped_at: datetime
    unshipped_at: datetime | None = None
    version: int
    pod_ref: str | None = None
    pod_captured_at: datetime | None = None


class DeliveryShipPostingEnvelope(_ClosedModel):
    data: DeliveryShipPostingView
    audit_id: UUID | None = None


class ShipPodPolicyView(_ClosedModel):
    ship_pod_required: bool
    updated_at: datetime
    version: int


class ShipPodPolicyEnvelope(_ClosedModel):
    data: ShipPodPolicyView
    audit_id: UUID | None = None
