"""PHX-G383 DLQ/replay fail-closed probe contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.event import EventStatusEnvelope
from kernel.event_bus.bus import EventBus
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
EVENT_OPENAPI = ROOT / "docs" / "api" / "event.openapi.yaml"
ADMIN, TENANT = uuid4(), uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _client() -> TestClient:
    return TestClient(create_app())


def _gated_client() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    return TestClient(
        create_app(permission_service=permission, event_service=EventBus(permission))
    )


def _headers(subject_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": f"corr-g383-{uuid4()}",
    }


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(EVENT_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g383_event_status_dlq_replay_fail_closed_flags() -> None:
    response = _client().get("/v1/events/status")
    assert response.status_code == 200, response.text
    body = response.json()
    EventStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["dead_letter_list_access"] == "permission_gated"
    assert data["dead_letter_replay_access"] == "permission_gated"
    assert data["event_replay_access"] == "permission_gated"
    assert data["fail_closed_without_grant"] is True


def test_g383_dead_letters_unauthenticated_fail_closed() -> None:
    client = _client()
    listed = client.get("/v1/events/dead-letters")
    assert listed.status_code == 401
    replayed = client.post(f"/v1/events/dead-letters/{uuid4()}/replay")
    assert replayed.status_code == 401
    event_replay = client.post(f"/v1/events/{uuid4()}/replay")
    assert event_replay.status_code == 401


def test_g383_dead_letters_without_grant_fail_closed() -> None:
    client = _gated_client()
    stranger = uuid4()
    listed = client.get("/v1/events/dead-letters", headers=_headers(stranger))
    assert listed.status_code == 403
    assert listed.json()["detail"]["code"] == "PERMISSION_DENIED"
    replayed = client.post(
        f"/v1/events/dead-letters/{uuid4()}/replay",
        headers=_headers(stranger),
    )
    assert replayed.status_code == 403
    assert replayed.json()["detail"]["code"] == "PERMISSION_DENIED"
    event_replay = client.post(
        f"/v1/events/{uuid4()}/replay",
        headers=_headers(stranger),
    )
    assert event_replay.status_code == 403
    assert event_replay.json()["detail"]["code"] == "PERMISSION_DENIED"


def test_g383_event_openapi_documents_fail_closed_flags() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    data = spec["components"]["schemas"]["EventStatusData"]
    props = data["properties"]
    assert props["dead_letter_list_access"]["const"] == "permission_gated"
    assert props["dead_letter_replay_access"]["const"] == "permission_gated"
    assert props["event_replay_access"]["const"] == "permission_gated"
    assert props["fail_closed_without_grant"]["const"] is True
