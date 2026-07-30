"""PHX-G98 Terminal Event Dispatch Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.event_bus.bus import EventBus
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
WORKER = uuid4()
PUBLISHER = uuid4()
SUBSCRIBER = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield


def _headers(subject_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "service",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.SERVICE,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_terminal_exposes_event_dispatch_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEventDispatch"' in html
    assert 'id="btnAdminEventGet"' in html
    assert 'id="eventWorkerId"' in html
    assert 'id="eventDispatchLimit"' in html
    assert 'id="eventId"' in html
    assert "Event dispatch/get 薄探针（G98）" in html
    assert 'eventDispatch: "/v1/events/dispatch"' in js
    assert "eventById" in js
    assert "adminDispatchDueEvents" in js
    assert "adminGetEvent" in js
    start = js.index("async function adminDispatchDueEvents")
    end = js.index("async function adminGetEvent")
    assert "tenant_id" not in js[start:end]
    assert "subject_id" not in js[start:end]


def test_gateway_serves_dispatch_ui_and_api() -> None:
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
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Dispatch due events" in page.text
    assert "Get event" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminDispatchDueEvents" in script.text

    assert (
        client.post(
            "/v1/events/subscriptions",
            headers=_headers(SUBSCRIBER),
            json={
                "subscriber_id": "projection.orders",
                "event_name": "crm.order.created",
            },
        ).status_code
        == 201
    )
    enqueued = client.post(
        "/v1/events/outbox",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-98"},
        },
    )
    assert enqueued.status_code == 202

    dispatched = client.post(
        "/v1/events/dispatch",
        headers=_headers(WORKER),
        json={"worker_id": "worker-g98", "limit": 8},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["data"]["outbox_dispatched"] >= 1

    published = client.post(
        "/v1/events",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.updated",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-98b"},
        },
    )
    assert published.status_code == 201
    event_id = published.json()["data"]["event_id"]
    fetched = client.get(f"/v1/events/{event_id}", headers=_headers(WORKER))
    assert fetched.status_code == 200
    assert fetched.json()["event_id"] == event_id
    assert fetched.json()["event_name"] == "crm.order.updated"
