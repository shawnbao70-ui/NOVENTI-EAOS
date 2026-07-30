"""PHX-G110 Knowledge Status / Entity Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from eaos_platform.knowledge.service import KnowledgeService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
AUTHOR = uuid4()
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


def _headers(subject_id: UUID = AUTHOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )


def test_terminal_exposes_knowledge_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminKnowledgeStatus"' in html
    assert 'id="btnAdminKnowledgeUpsertEntity"' in html
    assert 'id="btnAdminKnowledgeGetEntity"' in html
    assert 'id="btnAdminKnowledgeListEntities"' in html
    assert 'id="knowledgeEntityId"' in html
    assert "Knowledge 状态/entity 薄探针（G110" in html
    assert 'knowledgeStatus: "/v1/knowledge/status"' in js
    assert 'knowledgeEntities: "/v1/knowledge/entities"' in js
    assert "adminUpsertKnowledgeEntity" in js
    assert "adminGetKnowledgeEntity" in js
    assert "adminListKnowledgeEntities" in js
    start = js.index("async function adminUpsertKnowledgeEntity")
    end = js.index("async function adminArchiveKnowledgeEntity")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/archive" not in chunk
    assert "/share" not in chunk
    assert "/search" not in chunk
    assert "/links" not in chunk
    assert "/provenance" not in chunk


def test_knowledge_status_and_probe_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_entity",
        actions={"upsert", "read"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_graph",
        resource_id=TENANT,
        actions={"query"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            knowledge_service=KnowledgeService(permission),
        )
    )

    status = client.get("/v1/knowledge/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert "entity_upsert" in data["supported_surfaces"]
    assert "entity_query" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Knowledge status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminUpsertKnowledgeEntity" in script.text

    created = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "G110-Billing",
            "layer": "canonical",
            "labels": ["finance"],
            "source_ref": "docs/g110.md",
            "reason": "probe",
        },
    )
    assert created.status_code == 200
    entity_id = created.json()["id"]

    got = client.get(f"/v1/knowledge/entities/{entity_id}", headers=_headers())
    assert got.status_code == 200
    assert got.json()["name"] == "G110-Billing"

    listed = client.get(
        "/v1/knowledge/entities",
        headers=_headers(),
        params={"entityType": "Capability"},
    )
    assert listed.status_code == 200
    assert listed.json()["ok"] is True
    assert any(item["id"] == entity_id for item in listed.json()["data"])
