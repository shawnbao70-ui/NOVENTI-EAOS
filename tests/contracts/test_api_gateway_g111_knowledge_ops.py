"""PHX-G111 Knowledge Archive / Share / Search Thin Probe contracts."""

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
PEER = uuid4()
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


def test_terminal_exposes_knowledge_ops_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminKnowledgeArchiveEntity"' in html
    assert 'id="btnAdminKnowledgeShareEntity"' in html
    assert 'id="btnAdminKnowledgeSearch"' in html
    assert 'id="knowledgeSearchText"' in html
    assert 'id="knowledgeShareWithSubjectId"' in html
    assert "Knowledge archive/share/search 薄探针（G111" in html
    assert "knowledgeEntityArchive" in js
    assert "knowledgeEntityShare" in js
    assert "knowledgeSearch" in js
    assert "adminArchiveKnowledgeEntity" in js
    assert "adminShareKnowledgeEntity" in js
    assert "adminSearchKnowledge" in js
    start = js.index("async function adminArchiveKnowledgeEntity")
    end = js.index("async function adminCreateKnowledgeLink")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/links" not in chunk
    assert "/provenance" not in chunk


def test_gateway_serves_knowledge_ops_ui_and_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_entity",
        actions={"upsert", "read", "archive", "share"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_graph",
        resource_id=TENANT,
        actions={"query", "search"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            knowledge_service=KnowledgeService(permission),
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Archive knowledge entity" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminArchiveKnowledgeEntity" in script.text

    created = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "G111-Shared",
            "layer": "canonical",
            "source_ref": "docs/g111.md",
            "reason": "seed",
        },
    )
    assert created.status_code == 200
    entity_id = created.json()["id"]
    version = client.get(
        f"/v1/knowledge/entities/{entity_id}",
        headers=_headers(),
    ).json()["version"]

    searched = client.get(
        "/v1/knowledge/search",
        headers=_headers(),
        params={"text": "G111"},
    )
    assert searched.status_code == 200
    assert any(item["id"] == entity_id for item in searched.json()["data"])

    shared = client.post(
        f"/v1/knowledge/entities/{entity_id}/share",
        headers=_headers(),
        json={
            "share_with_subject_id": str(PEER),
            "source_ref": "docs/g111.md",
            "reason": "collaborate",
            "expected_version": version,
        },
    )
    assert shared.status_code == 200
    assert shared.json()["ok"] is True
    after_share = client.get(
        f"/v1/knowledge/entities/{entity_id}",
        headers=_headers(),
    ).json()
    assert str(PEER) in after_share["shared_with_subject_ids"]

    archived = client.post(
        f"/v1/knowledge/entities/{entity_id}/archive",
        headers=_headers(),
        json={
            "source_ref": "docs/g111.md",
            "reason": "retire",
            "expected_version": after_share["version"],
        },
    )
    assert archived.status_code == 200
    assert archived.json()["ok"] is True
