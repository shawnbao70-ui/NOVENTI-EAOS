"""PHX-G99 Terminal Event Enqueue/Publish Thin Probe contracts."""

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
PUBLISHER = uuid4()
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


def _headers(subject_id: UUID = PUBLISHER) -> dict[str, str]:
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


def test_terminal_exposes_event_enqueue_publish_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEventEnqueue"' in html
    assert 'id="btnAdminEventPublish"' in html
    assert 'id="eventName"' in html
    assert 'id="eventSchemaVersion"' in html
    assert 'id="eventProducer"' in html
    assert 'id="eventPayloadJson"' in html
    assert "Event enqueue/publish 薄探针（G99）" in html
    assert 'eventOutbox: "/v1/events/outbox"' in js
    assert 'eventPublish: "/v1/events"' in js
    assert "adminEnqueueOutbox" in js
    assert "adminPublishEvent" in js
    assert "buildEventProbeBody" in js
    start = js.index("function buildEventProbeBody")
    end = js.index("async function adminEnqueueOutbox")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "subject_id" not in chunk


def test_gateway_serves_enqueue_publish_ui_and_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    bus = EventBus(permission)
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=PUBLISHER,
        resource_type="event_stream",
        actions={"publish"},
    ).ok
    client = TestClient(
        create_app(permission_service=permission, event_service=bus)
    )
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Enqueue outbox" in page.text
    assert "Publish event" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminEnqueueOutbox" in script.text
    assert "adminPublishEvent" in script.text

    enqueued = client.post(
        "/v1/events/outbox",
        headers=_headers(),
        json={
            "event_name": "crm.order.created",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-99"},
        },
    )
    assert enqueued.status_code == 202
    assert enqueued.json()["ok"] is True

    published = client.post(
        "/v1/events",
        headers=_headers(),
        json={
            "event_name": "crm.order.updated",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-99b"},
        },
    )
    assert published.status_code == 201
    assert published.json()["ok"] is True
    assert "event_id" in published.json()["data"]
