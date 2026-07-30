"""Event Bus HTTP DTO mapping (PHX-G26)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kernel.event_bus.models import DeliveryReport, EventEnvelope
from kernel.event_bus.outbox import DeadLetterEntry, DeliveryStats, DispatchReport


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def uuid_result(resource_id: UUID, *, audit_id: UUID | None = None) -> dict[str, Any]:
    from api.gateway.serializers.common import uuid_result as _uuid_result

    return _uuid_result(resource_id, audit_id=audit_id, ok=True)


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True, "data": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def list_envelope(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"ok": True, "data": items}


def serialize_envelope(event: EventEnvelope) -> dict[str, Any]:
    return {
        "event_id": str(event.event_id),
        "event_name": event.event_name,
        "schema_version": event.schema_version,
        "correlation_id": event.correlation_id,
        "timestamp": _iso(event.timestamp),
        "producer": event.producer,
        "payload": dict(event.payload),
    }


def serialize_delivery_report(
    report: DeliveryReport,
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "data": {
            "event_id": str(report.event_id),
            "delivered_count": report.delivered_count,
            "skipped_count": report.skipped_count,
            "failed_subscribers": list(report.failed_subscribers),
        },
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_dispatch_report(
    report: DispatchReport,
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "data": {
            "outbox_dispatched": report.outbox_dispatched,
            "outbox_failed": report.outbox_failed,
            "deliveries_retried": report.deliveries_retried,
            "deliveries_dead_lettered": report.deliveries_dead_lettered,
        },
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_delivery_stats(stats: DeliveryStats) -> dict[str, Any]:
    return {
        "ok": True,
        "data": {
            "pending_outbox": stats.pending_outbox,
            "leased_outbox": stats.leased_outbox,
            "failed_deliveries": stats.failed_deliveries,
            "dead_letter_depth": stats.dead_letter_depth,
        },
    }


def serialize_dead_letter(entry: DeadLetterEntry) -> dict[str, Any]:
    return {
        "id": str(entry.id),
        "event_id": str(entry.event_id),
        "subscriber_id": entry.subscriber_id,
        "reason": entry.reason,
        "attempt_count": entry.attempt_count,
        "created_at": _iso(entry.created_at),
        "replayed_at": _iso(entry.replayed_at),
    }
