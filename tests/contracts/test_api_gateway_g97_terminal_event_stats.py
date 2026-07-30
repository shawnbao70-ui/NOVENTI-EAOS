"""PHX-G97 Terminal Event Bus Stats Thin Probe contracts."""

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


def _headers(subject_id: UUID = WORKER) -> dict[str, str]:
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


def test_terminal_exposes_event_bus_ops_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEventStats"' in html
    assert 'id="btnAdminDeadLetters"' in html
    assert 'id="btnAdminReplayDeadLetter"' in html
    assert 'id="deadLetterId"' in html
    assert "Event Bus stats/DLQ 薄探针（G97）" in html
    assert 'eventStats: "/v1/events/stats"' in js
    assert 'eventDeadLetters: "/v1/events/dead-letters"' in js
    assert "eventDeadLetterReplay" in js
    assert "adminEventDeliveryStats" in js
    assert "adminListDeadLetters" in js
    assert "adminReplayDeadLetter" in js


def test_gateway_serves_event_ops_ui_and_stats() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    bus = EventBus(permission)
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=WORKER,
        resource_type="event_stream",
        actions={"dispatch", "read", "replay"},
    ).ok
    client = TestClient(
        create_app(permission_service=permission, event_service=bus)
    )
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Event delivery stats" in page.text
    assert "List dead letters" in page.text
    assert "Replay dead letter" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminEventDeliveryStats" in script.text

    stats = client.get("/v1/events/stats", headers=_headers())
    assert stats.status_code == 200
    body = stats.json()
    assert body["ok"] is True
    assert "pending_outbox" in body["data"]

    letters = client.get("/v1/events/dead-letters", headers=_headers())
    assert letters.status_code == 200
    assert letters.json()["ok"] is True
    assert isinstance(letters.json()["data"], list)
