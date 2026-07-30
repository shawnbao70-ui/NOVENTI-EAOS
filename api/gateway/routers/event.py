"""Event Bus HTTP surface — thin transport adapter (PHX-G26)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.commercial_event_catalog import commercial_event_catalog_projection
from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import EventGatewayService, get_event_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import UuidResult
from api.gateway.schemas.event import (
    DeadLetterListEnvelope,
    DeliveryReportResult,
    DeliveryStatsResult,
    DispatchDueRequest,
    DispatchReportResult,
    EventCatalogEnvelope,
    EventEnvelopeResponse,
    EventOkResponse,
    EventStatusEnvelope,
    PublishEventRequest,
    SubscribeRequest,
)
from api.gateway.serializers.event import (
    list_envelope,
    ok_response,
    serialize_dead_letter,
    serialize_delivery_report,
    serialize_delivery_stats,
    serialize_dispatch_report,
    serialize_envelope,
    uuid_result,
)
from kernel.event_bus.bus import DEFAULT_LEASE_SECONDS
from kernel.event_bus.models import EventEnvelope
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/events", tags=["Event"])


@router.get("/status", response_model=EventStatusEnvelope)
def get_event_status() -> EventStatusEnvelope:
    """Read-only Event Bus posture (PHX-G193) + outbox worker/lease honesty (PHX-G382)."""

    return EventStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "event_publish",
                    "outbox_enqueue",
                    "dispatch_run",
                    "delivery_stats",
                    "dead_letter_list",
                    "dead_letter_retry",
                    "commercial_catalog",
                ],
                "background_worker_daemon": False,
                "dispatch_trigger": "http_post_dispatch",
                "lease_claim_enabled": True,
                "default_lease_seconds": DEFAULT_LEASE_SECONDS,
                "dead_letter_list_access": "permission_gated",
                "dead_letter_replay_access": "permission_gated",
                "event_replay_access": "permission_gated",
                "fail_closed_without_grant": True,
                "outbox_delivery_mode": "on_demand",
                "audit_read_surface": True,
                "commercial_emit_catalog_only": True,
                "replay_stats_read_only": True,
                "multi_region_failover": False,
            }
        }
    )


@router.get("/catalog", response_model=EventCatalogEnvelope)
def get_event_catalog() -> EventCatalogEnvelope:
    """Read-only commercial domain-event catalog projection (PHX-G386)."""

    return EventCatalogEnvelope.model_validate(
        {"data": commercial_event_catalog_projection()}
    )


def _http_noop_handler(event: EventEnvelope) -> None:
    """Placeholder for HTTP-registered subscriptions (no business side effects)."""


@router.post(
    "",
    response_model=DeliveryReportResult,
    status_code=status.HTTP_201_CREATED,
)
def publish_event(
    body: PublishEventRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> DeliveryReportResult:
    reject_context_override(body.model_dump())
    result = event_bus.publish(
        ctx,
        event_name=body.event_name,
        schema_version=body.schema_version,
        producer=body.producer,
        payload=body.payload,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return DeliveryReportResult.model_validate(
        serialize_delivery_report(result.data, audit_id=result.audit_id)
    )


@router.post("/outbox", response_model=UuidResult, status_code=status.HTTP_202_ACCEPTED)
def enqueue_event(
    body: PublishEventRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = event_bus.enqueue(
        ctx,
        event_name=body.event_name,
        schema_version=body.schema_version,
        producer=body.producer,
        payload=body.payload,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_202_ACCEPTED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/dispatch", response_model=DispatchReportResult)
def dispatch_due(
    body: DispatchDueRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> DispatchReportResult:
    reject_context_override(body.model_dump())
    result = event_bus.dispatch_due(
        ctx,
        worker_id=body.worker_id,
        limit=body.limit,
    )
    raise_for_result(result)
    assert result.data is not None
    return DispatchReportResult.model_validate(
        serialize_dispatch_report(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/subscriptions",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def subscribe(
    body: SubscribeRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = event_bus.subscribe(
        ctx,
        subscriber_id=body.subscriber_id,
        event_name=body.event_name,
        handler=None if body.delivery_url else _http_noop_handler,
        delivery_url=body.delivery_url,
        signing_secret=body.signing_secret,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/stats", response_model=DeliveryStatsResult)
def get_delivery_stats(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> DeliveryStatsResult:
    result = event_bus.get_delivery_stats(ctx)
    raise_for_result(result)
    assert result.data is not None
    return DeliveryStatsResult.model_validate(
        serialize_delivery_stats(result.data)
    )


@router.get("/dead-letters", response_model=DeadLetterListEnvelope)
def list_dead_letters(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> DeadLetterListEnvelope:
    result = event_bus.list_dead_letters(ctx)
    raise_for_result(result)
    assert result.data is not None
    return DeadLetterListEnvelope.model_validate(
        list_envelope([serialize_dead_letter(item) for item in result.data])
    )


@router.post(
    "/dead-letters/{dead_letter_id}/replay",
    response_model=EventOkResponse,
)
def replay_dead_letter(
    dead_letter_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> EventOkResponse:
    result = event_bus.replay_dead_letter(ctx, dead_letter_id=dead_letter_id)
    raise_for_result(result)
    return EventOkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.get("/{event_id}", response_model=EventEnvelopeResponse)
def get_event(
    event_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> EventEnvelopeResponse:
    result = event_bus.get_event(ctx, event_id=event_id)
    raise_for_result(result)
    assert result.data is not None
    return EventEnvelopeResponse.model_validate(serialize_envelope(result.data))


@router.post("/{event_id}/replay", response_model=DeliveryReportResult)
def replay_event(
    event_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    event_bus: EventGatewayService = Depends(get_event_service),
) -> DeliveryReportResult:
    result = event_bus.replay(ctx, event_id=event_id)
    raise_for_result(result)
    assert result.data is not None
    return DeliveryReportResult.model_validate(
        serialize_delivery_report(result.data, audit_id=result.audit_id)
    )
