"""PHX-G26 Gateway Event Bus HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.event_bus.bus import EventBus
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ADMIN = uuid4()
PUBLISHER = uuid4()
WORKER = uuid4()
SUBSCRIBER = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = PUBLISHER, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "service",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.SERVICE,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> tuple[TestClient, PermissionService, EventBus]:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    bus = EventBus(permission)
    for principal, actions in (
        (PUBLISHER, {"publish"}),
        (SUBSCRIBER, {"subscribe"}),
        (WORKER, {"dispatch", "read", "replay"}),
    ):
        assert permission.grant(
            _admin_ctx(),
            principal_subject_id=principal,
            resource_type="event_stream",
            actions=actions,
        ).ok
    client = TestClient(
        create_app(permission_service=permission, event_service=bus)
    )
    return client, permission, bus


def test_event_requires_trusted_headers(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.get("/v1/events/stats")
    assert response.status_code == 401


def test_enqueue_dispatch_get_and_stats(gateway: tuple) -> None:
    client, _, _ = gateway
    subscribed = client.post(
        "/v1/events/subscriptions",
        headers=_headers(SUBSCRIBER),
        json={
            "subscriber_id": "projection.orders",
            "event_name": "crm.order.created",
        },
    )
    assert subscribed.status_code == 201
    assert subscribed.json()["ok"] is True

    enqueued = client.post(
        "/v1/events/outbox",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-1"},
        },
    )
    assert enqueued.status_code == 202
    assert enqueued.json()["ok"] is True

    before = client.get("/v1/events/stats", headers=_headers(WORKER))
    assert before.status_code == 200
    assert before.json()["data"]["pending_outbox"] == 1

    dispatched = client.post(
        "/v1/events/dispatch",
        headers=_headers(WORKER),
        json={"worker_id": "worker-1"},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["data"]["outbox_dispatched"] == 1

    after = client.get("/v1/events/stats", headers=_headers(WORKER))
    assert after.json()["data"]["pending_outbox"] == 0


def test_publish_get_and_replay(gateway: tuple) -> None:
    client, _, _ = gateway
    published = client.post(
        "/v1/events",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.updated",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-2"},
        },
    )
    assert published.status_code == 201
    event_id = published.json()["data"]["event_id"]

    fetched = client.get(f"/v1/events/{event_id}", headers=_headers(WORKER))
    assert fetched.status_code == 200
    assert fetched.json()["event_name"] == "crm.order.updated"
    assert fetched.json()["payload"]["order_id"] == "O-2"

    replayed = client.post(
        f"/v1/events/{event_id}/replay",
        headers=_headers(WORKER),
    )
    assert replayed.status_code == 200
    assert replayed.json()["ok"] is True
    assert replayed.json()["data"]["event_id"] == event_id


def test_dead_letters_list_empty_when_healthy(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.get("/v1/events/dead-letters", headers=_headers(WORKER))
    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": []}


def test_permission_denied_without_grant(gateway: tuple) -> None:
    client, _, _ = gateway
    stranger = uuid4()
    response = client.post(
        "/v1/events/outbox",
        headers=_headers(stranger),
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {},
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_DENIED"


def test_body_cannot_elevate_context(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.post(
        "/v1/events/outbox",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {},
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed PublishEventRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_invalid_event_name_rejected(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.post(
        "/v1/events",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "NotAValidName",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {},
        },
    )
    # Closed DTO pattern rejects invalid event_name before domain envelope checks.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("event_name" in str(item.get("loc", ())) for item in detail)
