"""PHX-G112 Knowledge Link / Provenance Thin Probe contracts."""

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


def test_terminal_exposes_link_provenance_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminKnowledgeCreateLink"' in html
    assert 'id="btnAdminKnowledgeGetProvenance"' in html
    assert 'id="knowledgeLinkToId"' in html
    assert 'id="knowledgeProvenanceKind"' in html
    assert "Knowledge link/provenance 薄探针（G112" in html
    assert "Knowledge Terminal 运维面齐" in html
    assert "knowledgeLinks" in js
    assert "knowledgeProvenance" in js
    assert "adminCreateKnowledgeLink" in js
    assert "adminGetKnowledgeProvenance" in js
    start = js.index("async function adminCreateKnowledgeLink")
    end = js.index("async function adminUpsertTwinSnapshot")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk


def test_gateway_serves_link_provenance_ui_and_api() -> None:
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
        resource_type="knowledge_link",
        actions={"create", "read"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_provenance",
        actions={"read"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            knowledge_service=KnowledgeService(permission),
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Create knowledge link" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreateKnowledgeLink" in script.text

    a = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": f"G112-A-{uuid4()}",
            "layer": "canonical",
            "source_ref": "docs/g112-a.md",
            "reason": "seed",
        },
    )
    assert a.status_code == 200
    a_id = a.json()["id"]
    b = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": f"G112-B-{uuid4()}",
            "layer": "canonical",
            "source_ref": "docs/g112-b.md",
            "reason": "seed",
        },
    )
    assert b.status_code == 200
    b_id = b.json()["id"]

    linked = client.post(
        "/v1/knowledge/links",
        headers=_headers(),
        json={
            "from_entity_id": a_id,
            "to_entity_id": b_id,
            "relation_type": "depends_on",
            "source_ref": "docs/g112-link.md",
            "reason": "relate",
        },
    )
    assert linked.status_code == 201
    assert linked.json()["id"]

    provenance = client.get(
        f"/v1/knowledge/provenance/entity/{a_id}",
        headers=_headers(),
    )
    assert provenance.status_code == 200
    assert provenance.json()["ok"] is True
    assert len(provenance.json()["data"]) >= 1
    assert provenance.json()["data"][0]["source_ref"] == "docs/g112-a.md"
