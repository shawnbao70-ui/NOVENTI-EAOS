"""PHX-G100 Terminal Event Subscribe/Replay Thin Probe contracts."""

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
SUBSCRIBER = uuid4()
WORKER = uuid4()
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


def test_terminal_exposes_event_subscribe_replay_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEventSubscribe"' in html
    assert 'id="btnAdminEventReplay"' in html
    assert 'id="eventSubscriberId"' in html
    assert 'id="eventDeliveryUrl"' in html
    assert "Event subscribe/replay 薄探针（G100）" in html
    assert "no signing secret in Terminal" in html
    assert 'eventSubscriptions: "/v1/events/subscriptions"' in js
    assert "eventReplay" in js
    assert "adminSubscribeEvent" in js
    assert "adminReplayEvent" in js
    start = js.index("async function adminSubscribeEvent")
    end = js.index("async function adminReplayEvent")
    chunk = js[start:end]
    assert "signing_secret" not in chunk
    assert "tenant_id" not in chunk
    assert "subject_id" not in chunk


def test_gateway_serves_subscribe_replay_ui_and_api() -> None:
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
    assert "Subscribe event" in page.text
    assert "Replay event" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminSubscribeEvent" in script.text
    assert "adminReplayEvent" in script.text
    assert "signing_secret" not in script.text.split("adminSubscribeEvent")[1].split(
        "async function adminReplayEvent"
    )[0]

    subscribed = client.post(
        "/v1/events/subscriptions",
        headers=_headers(SUBSCRIBER),
        json={
            "subscriber_id": "projection.orders",
            "event_name": "crm.order.updated",
        },
    )
    assert subscribed.status_code == 201
    assert subscribed.json()["ok"] is True

    published = client.post(
        "/v1/events",
        headers=_headers(PUBLISHER),
        json={
            "event_name": "crm.order.updated",
            "schema_version": "1",
            "producer": "pkg.crm",
            "payload": {"order_id": "O-100"},
        },
    )
    assert published.status_code == 201
    event_id = published.json()["data"]["event_id"]

    replayed = client.post(
        f"/v1/events/{event_id}/replay",
        headers=_headers(WORKER),
    )
    assert replayed.status_code == 200
    assert replayed.json()["ok"] is True
    assert replayed.json()["data"]["event_id"] == event_id
