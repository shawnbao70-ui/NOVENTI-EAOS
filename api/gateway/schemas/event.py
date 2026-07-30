"""Event Bus request/response DTOs — runtime parity with docs/api/event.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EventStatusData(_ClosedModel):
    """Event Bus status with worker/lease (G382) + DLQ/replay fail-closed (G383)."""

    writable: Literal[False] = False
    supported_surfaces: list[str] = Field(min_length=1)
    background_worker_daemon: Literal[False] = False
    dispatch_trigger: Literal["http_post_dispatch"] = "http_post_dispatch"
    lease_claim_enabled: Literal[True] = True
    default_lease_seconds: Literal[30] = 30
    dead_letter_list_access: Literal["permission_gated"] = "permission_gated"
    dead_letter_replay_access: Literal["permission_gated"] = "permission_gated"
    event_replay_access: Literal["permission_gated"] = "permission_gated"
    fail_closed_without_grant: Literal[True] = True
    outbox_delivery_mode: Literal["on_demand"] = "on_demand"
    audit_read_surface: Literal[True] = True
    commercial_emit_catalog_only: Literal[True] = True
    replay_stats_read_only: Literal[True] = True
    multi_region_failover: Literal[False] = False


class EventStatusEnvelope(_ClosedModel):
    data: EventStatusData


class CommercialEventCatalogEntry(_ClosedModel):
    event_name: str = Field(
        pattern=r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
    )
    producer: Literal["crm.package", "inventory.package"]
    trigger: str = Field(min_length=1)


class EventCatalogData(_ClosedModel):
    """Read-only commercial event catalog projection (PHX-G386)."""

    writable: Literal[False] = False
    catalog_id: Literal["EVT-COMMERCIAL-001"] = "EVT-COMMERCIAL-001"
    milestone: Literal["PHX-G386"] = "PHX-G386"
    events: list[CommercialEventCatalogEntry] = Field(min_length=1)


class EventCatalogEnvelope(_ClosedModel):
    data: EventCatalogData


class PublishEventRequest(_ClosedModel):
    event_name: str = Field(
        pattern=r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
    )
    schema_version: str = Field(min_length=1)
    producer: str = Field(min_length=1)
    payload: dict[str, Any]


class DispatchDueRequest(_ClosedModel):
    worker_id: str = Field(min_length=1)
    limit: int = Field(default=32, ge=1)


class SubscribeRequest(_ClosedModel):
    subscriber_id: str = Field(min_length=1)
    event_name: str = Field(min_length=1)
    delivery_url: str | None = Field(default=None, max_length=2048)
    signing_secret: str | None = Field(default=None, min_length=16, max_length=256)

    @field_validator("delivery_url", "signing_secret", mode="before")
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class DeliveryReportPayload(_ClosedModel):
    event_id: UUID
    delivered_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    failed_subscribers: list[str]


class DeliveryReportResult(_ClosedModel):
    ok: Literal[True] = True
    data: DeliveryReportPayload
    audit_id: UUID | str | None = None


class DispatchReportPayload(_ClosedModel):
    outbox_dispatched: int = Field(ge=0)
    outbox_failed: int = Field(ge=0)
    deliveries_retried: int = Field(ge=0)
    deliveries_dead_lettered: int = Field(ge=0)


class DispatchReportResult(_ClosedModel):
    ok: Literal[True] = True
    data: DispatchReportPayload
    audit_id: UUID | str | None = None


class DeliveryStatsPayload(_ClosedModel):
    pending_outbox: int = Field(ge=0)
    leased_outbox: int = Field(ge=0)
    failed_deliveries: int = Field(ge=0)
    dead_letter_depth: int = Field(ge=0)


class DeliveryStatsResult(_ClosedModel):
    ok: Literal[True] = True
    data: DeliveryStatsPayload


class DeadLetterEntry(_ClosedModel):
    id: UUID
    event_id: UUID
    subscriber_id: str = Field(min_length=1)
    reason: str
    attempt_count: int = Field(ge=0)
    created_at: str | None = None
    replayed_at: str | None = None


class DeadLetterListEnvelope(_ClosedModel):
    ok: Literal[True] = True
    data: list[DeadLetterEntry]


class EventEnvelopeResponse(_ClosedModel):
    """GET /events/{id} — payload remains free-form (OpenAPI honesty)."""

    event_id: UUID
    event_name: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    correlation_id: str | None = None
    timestamp: str | None = None
    producer: str = Field(min_length=1)
    payload: dict[str, Any]


class EventOkResponse(_ClosedModel):
    """Event-domain ok envelope includes data:true (runtime dialect)."""

    ok: Literal[True] = True
    data: Literal[True] = True
    audit_id: UUID | str | None = None
