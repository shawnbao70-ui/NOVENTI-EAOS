"""PHX-E21 Event webhook transport contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

from kernel.event_bus.bus import EventBus
from kernel.event_bus.url_safety import validate_webhook_delivery_url
from kernel.event_bus.webhook import RecordingWebhookPoster
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ACTOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _admin() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _bus(poster: RecordingWebhookPoster | None = None) -> EventBus:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    assert permission.grant(
        _admin(),
        principal_subject_id=ACTOR,
        resource_type="event_stream",
        actions={"subscribe", "publish", "dispatch", "read"},
    ).ok
    return EventBus(permission, webhook_poster=poster)


def test_url_safety_rejects_private_and_metadata() -> None:
    validate_webhook_delivery_url("https://hooks.example.com/eaos")
    validate_webhook_delivery_url("http://127.0.0.1:8080/hook")
    with pytest.raises(KernelError) as denied:
        validate_webhook_delivery_url("https://10.0.0.8/hook")
    assert denied.value.code == ErrorCode.EVENT_SUBSCRIPTION_INVALID
    with pytest.raises(KernelError) as meta:
        validate_webhook_delivery_url("http://169.254.169.254/latest")
    assert meta.value.code == ErrorCode.EVENT_SUBSCRIPTION_INVALID
    with pytest.raises(KernelError) as creds:
        validate_webhook_delivery_url("https://user:pass@hooks.example.com/x")
    assert creds.value.code == ErrorCode.EVENT_SUBSCRIPTION_INVALID


def test_webhook_subscribe_dispatch_posts_envelope() -> None:
    poster = RecordingWebhookPoster()
    bus = _bus(poster)
    ctx = _ctx()
    subscribed = bus.subscribe(
        ctx,
        subscriber_id="webhook.orders",
        event_name="organization.tenant.created",
        delivery_url="https://hooks.example.com/eaos",
    )
    assert subscribed.ok
    enqueued = bus.enqueue(
        ctx,
        event_name="organization.tenant.created",
        schema_version="1",
        producer="organization.kernel",
        payload={"tenant_id": str(TENANT)},
    )
    assert enqueued.ok
    dispatched = bus.dispatch_due(ctx, worker_id="worker-e21", limit=8)
    assert dispatched.ok
    assert dispatched.data is not None
    assert dispatched.data.outbox_dispatched == 1
    assert len(poster.calls) == 1
    call = poster.calls[0]
    assert call["url"] == "https://hooks.example.com/eaos"
    assert call["payload"]["event_name"] == "organization.tenant.created"
    assert call["payload"]["tenant_id"] == str(TENANT)
    assert call["headers"]["X-EAOS-Event-Name"] == "organization.tenant.created"


def test_webhook_failure_marks_delivery_failed() -> None:
    poster = RecordingWebhookPoster(fail_with=RuntimeError("webhook_http_500"))
    bus = _bus(poster)
    ctx = _ctx()
    assert bus.subscribe(
        ctx,
        subscriber_id="webhook.fail",
        event_name="organization.tenant.created",
        delivery_url="https://hooks.example.com/fail",
    ).ok
    assert bus.enqueue(
        ctx,
        event_name="organization.tenant.created",
        schema_version="1",
        producer="organization.kernel",
        payload={"ok": False},
    ).ok
    report = bus.dispatch_due(ctx, worker_id="worker-e21-fail", limit=8)
    assert report.ok
    stats = bus.get_delivery_stats(ctx)
    assert stats.ok and stats.data is not None
    assert stats.data.failed_deliveries >= 1


def test_gateway_webhook_subscribe_and_reject_unsafe_url() -> None:
    poster = RecordingWebhookPoster()
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    bus = EventBus(permission, webhook_poster=poster)
    assert permission.grant(
        _admin(),
        principal_subject_id=ACTOR,
        resource_type="event_stream",
        actions={"subscribe", "publish", "dispatch", "read"},
    ).ok
    client = TestClient(
        create_app(permission_service=permission, event_service=bus)
    )
    headers = {
        "X-EAOS-Subject-Id": str(ACTOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }
    denied = client.post(
        "/v1/events/subscriptions",
        headers=headers,
        json={
            "subscriber_id": "webhook.bad",
            "event_name": "crm.order.created",
            "delivery_url": "https://10.1.2.3/hook",
        },
    )
    assert denied.status_code == 400
    assert denied.json()["detail"]["code"] == "EVENT_SUBSCRIPTION_INVALID"

    ok = client.post(
        "/v1/events/subscriptions",
        headers=headers,
        json={
            "subscriber_id": "webhook.ok",
            "event_name": "crm.order.created",
            "delivery_url": "https://hooks.example.com/orders",
        },
    )
    assert ok.status_code == 201
    enqueued = client.post(
        "/v1/events/outbox",
        headers=headers,
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "1"},
        },
    )
    assert enqueued.status_code in {201, 202}
    dispatched = client.post(
        "/v1/events/dispatch",
        headers=headers,
        json={"worker_id": "gw-e21", "limit": 8},
    )
    assert dispatched.status_code == 200
    assert len(poster.calls) == 1
    assert poster.calls[0]["url"] == "https://hooks.example.com/orders"
