"""Foundation harden — closed request DTOs reject unknown fields (extra=forbid → 422)."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app

OPERATOR = uuid4()
TENANT = uuid4()
GOVERNOR = uuid4()


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(OPERATOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.parametrize(
    ("method", "path", "headers", "body"),
    [
        (
            "POST",
            "/v1/packages/actions/resolve",
            _tenant_headers(),
            {"action_key": "ops.brief.compose", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/platform/roles",
            _platform_headers(),
            {"name": "operator", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/platform/idp/issuers",
            _platform_headers(),
            {
                "issuer": "https://extra.example/eaos",
                "jwks_url": "https://extra.example/jwks",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            f"/v1/platform/idp/federation/bindings/{uuid4()}/priority",
            _platform_headers(),
            {"priority": 1, "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/auth/webauthn/register/options",
            _tenant_headers(),
            {"user_name": "alice", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/permission/role-grants",
            _tenant_headers(),
            {
                "principal_id": str(OPERATOR),
                "roles": ["operator"],
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/terminal/extensions",
            _tenant_headers(),
            {
                "extension_key": "noventi.demo.panel",
                "version": "1.0.0",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            f"/v1/terminal/extensions/{uuid4()}/actions",
            _tenant_headers(),
            {"action": "panel.render", "surface": "extensions", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/identity/subjects",
            _tenant_headers(),
            {
                "subject_type": "human",
                "display_name": "Ada",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/permission/policies",
            _tenant_headers(),
            {
                "name": "demo-policy",
                "rules": [
                    {
                        "effect": "allow",
                        "resource_type": "document",
                        "actions": ["read"],
                        "scope_level": "tenant",
                    }
                ],
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/permission/grants",
            _tenant_headers(),
            {
                "principal_id": str(OPERATOR),
                "resource_type": "document",
                "scope_level": "tenant",
                "actions": ["read"],
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/workflow/definitions",
            _tenant_headers(),
            {
                "name": "demo-def",
                "definition_document_ref": "doc:demo",
                "version": "1.0.0",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/enterprises",
            _tenant_headers(),
            {"legal_name": "Demo Co", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/events",
            _tenant_headers(),
            {
                "event_name": "pkg.ops.brief.composed",
                "schema_version": "1",
                "producer": "test",
                "payload": {},
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/knowledge/entities",
            _tenant_headers(),
            {
                "entity_type": "customer",
                "name": "Acme",
                "layer": "operational",
                "source_ref": "test",
                "reason": "probe",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/ai/runs",
            _tenant_headers(),
            {"goal": "draft", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/marketplace/listings",
            _tenant_headers(),
            {
                "package_key": "noventi.demo",
                "package_version": "1.0.0",
                "required_permissions": ["a:b"],
                "data_scope": "tenant.x",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/twin/snapshots",
            _tenant_headers(),
            {
                "entity_ref": "plant:x",
                "state": {},
                "source_ref": "sensor",
                "reason": "sync",
                "confidence": 0.5,
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/brain/insights",
            _tenant_headers(),
            {
                "kind": "insight",
                "summary": "probe",
                "confidence": 0.5,
                "source_ref": "test",
                "reason": "probe",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/packages/manifests",
            _tenant_headers(),
            {
                "package_key": "noventi.demo",
                "version": "1.0.0",
                "package_type": "business",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/terminal/sessions",
            _tenant_headers(),
            {"device_trust": "trusted", "extra_field": "nope"},
        ),
        (
            "POST",
            "/v1/terminal/intents",
            _tenant_headers(),
            {
                "terminal_session_id": str(uuid4()),
                "text": "compose brief",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/terminal/previews",
            _tenant_headers(),
            {
                "intent_id": str(uuid4()),
                "action": "ops.brief.compose",
                "resource_ref": "doc:demo",
                "plan_version": "1",
                "scope": "tenant",
                "impact_summary": "low",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/ai/tools",
            _tenant_headers(),
            {
                "name": "demo.tool",
                "description": "demo",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/events/outbox",
            _tenant_headers(),
            {
                "event_name": "pkg.ops.brief.composed",
                "schema_version": "1",
                "producer": "test",
                "payload": {},
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/events/subscriptions",
            _tenant_headers(),
            {
                "subscriber_id": "test-consumer",
                "event_name": "pkg.ops.brief.composed",
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            f"/v1/marketplace/listings/{uuid4()}/payment-clearing",
            _tenant_headers(),
            {
                "invoice_id": str(uuid4()),
                "extra_field": "nope",
            },
        ),
        (
            "POST",
            "/v1/knowledge/links",
            _tenant_headers(),
            {
                "from_entity_id": str(uuid4()),
                "to_entity_id": str(uuid4()),
                "relation_type": "related",
                "source_ref": "test",
                "reason": "probe",
                "extra_field": "nope",
            },
        ),
    ],
)
def test_closed_request_dto_rejects_extra_field(
    client: TestClient,
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, object],
) -> None:
    response = client.request(method, path, headers=headers, json=body)
    assert response.status_code == 422, (path, response.status_code, response.text)
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    locs = [tuple(err.get("loc", ())) for err in detail]
    assert any("extra_field" in loc for loc in locs), locs
