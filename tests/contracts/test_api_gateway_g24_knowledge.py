"""PHX-G24 Gateway Knowledge HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.knowledge.service import KnowledgeService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ADMIN = uuid4()
AUTHOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = AUTHOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> tuple[TestClient, PermissionService]:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    knowledge = KnowledgeService(permission)
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_entity",
        actions={"upsert", "read", "archive", "share"},
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
        resource_type="knowledge_graph",
        resource_id=TENANT,
        actions={"query", "search"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AUTHOR,
        resource_type="knowledge_provenance",
        actions={"read"},
    ).ok
    client = TestClient(
        create_app(permission_service=permission, knowledge_service=knowledge)
    )
    return client, permission


def test_knowledge_requires_trusted_headers(gateway: tuple) -> None:
    client, _ = gateway
    response = client.get("/v1/knowledge/search", params={"text": "x"})
    assert response.status_code == 401


def test_upsert_get_query_search_and_provenance(gateway: tuple) -> None:
    client, _ = gateway
    created = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "Billing",
            "layer": "canonical",
            "labels": ["finance"],
            "source_ref": "docs/billing.md",
            "reason": "seed",
        },
    )
    assert created.status_code == 200
    entity_id = created.json()["id"]

    got = client.get(f"/v1/knowledge/entities/{entity_id}", headers=_headers())
    assert got.status_code == 200
    assert got.json()["name"] == "Billing"
    assert got.json()["layer"] == "canonical"

    queried = client.get(
        "/v1/knowledge/entities",
        headers=_headers(),
        params={"entityType": "Capability"},
    )
    assert queried.status_code == 200
    assert queried.json()["ok"] is True
    assert any(item["id"] == entity_id for item in queried.json()["data"])

    searched = client.get(
        "/v1/knowledge/search",
        headers=_headers(),
        params={"text": "bill"},
    )
    assert searched.status_code == 200
    assert any(item["id"] == entity_id for item in searched.json()["data"])

    provenance = client.get(
        f"/v1/knowledge/provenance/entity/{entity_id}",
        headers=_headers(),
    )
    assert provenance.status_code == 200
    assert provenance.json()["ok"] is True
    assert len(provenance.json()["data"]) >= 1
    assert provenance.json()["data"][0]["source_ref"] == "docs/billing.md"


def test_create_link(gateway: tuple) -> None:
    client, _ = gateway
    a = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": f"A-{uuid4()}",
            "layer": "canonical",
            "source_ref": "docs/a.md",
            "reason": "seed",
        },
    ).json()["id"]
    b = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": f"B-{uuid4()}",
            "layer": "canonical",
            "source_ref": "docs/b.md",
            "reason": "seed",
        },
    ).json()["id"]
    linked = client.post(
        "/v1/knowledge/links",
        headers=_headers(),
        json={
            "from_entity_id": a,
            "to_entity_id": b,
            "relation_type": "depends_on",
            "source_ref": "docs/link.md",
            "reason": "relate",
        },
    )
    assert linked.status_code == 201
    assert "id" in linked.json()


def test_upsert_requires_provenance(gateway: tuple) -> None:
    client, _ = gateway
    response = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "Missing",
            "layer": "canonical",
            "source_ref": "",
            "reason": "seed",
        },
    )
    # Closed UpsertEntityRequest requires non-empty source_ref (provenance honesty).
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("source_ref" in str(item.get("loc", ())) for item in detail)


def test_upsert_rejects_context_override(gateway: tuple) -> None:
    client, _ = gateway
    response = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "X",
            "layer": "canonical",
            "source_ref": "docs/x.md",
            "reason": "seed",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed UpsertEntityRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_query_without_permission_denied(gateway: tuple) -> None:
    client, _ = gateway
    response = client.get(
        "/v1/knowledge/entities",
        headers=_headers(subject_id=uuid4()),
    )
    assert response.status_code == 403
