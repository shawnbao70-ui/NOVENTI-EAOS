"""PHX-G345 explicit, tenant-only Cap→grant gateway contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from tests.contracts.test_api_gateway_g339_brain_commercial_handoff import (
    ADMIN,
    SUBJECT,
    TENANT,
    _client as g339_client,
    _headers as g339_headers,
    _restock,
    _seed,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def _client() -> tuple[TestClient, InMemoryAuditLog]:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    audit = InMemoryAuditLog()
    service = PermissionService(
        audit_log=audit,
        grant_administrators={ADMIN},
        principal_eligibility=_Eligibility(),
    )
    return TestClient(create_app(permission_service=service)), audit


def _cap_body(*, resource_type: str = "document", actions: list[str] | None = None) -> dict[str, object]:
    return {
        "principal_subject_id": str(SUBJECT),
        "capability": "cap.document.manage",
        "resource_type": resource_type,
        "actions": actions or ["read"],
        "scope_level": "tenant",
        "idempotency_key": "g345-idempotency",
    }


def test_g345_requires_grant_administrator_and_rejects_non_tenant_scope() -> None:
    client, _audit = _client()

    denied = client.post("/v1/permission/cap-grants", headers=_headers(SUBJECT), json=_cap_body())
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "PERMISSION_DENIED"

    cross_tenant_shape = client.post(
        "/v1/permission/cap-grants",
        headers=_headers(ADMIN),
        json={**_cap_body(), "scope_level": "enterprise"},
    )
    assert cross_tenant_shape.status_code == 422

    context_override = client.post(
        "/v1/permission/cap-grants",
        headers=_headers(ADMIN),
        json={**_cap_body(), "tenant_id": str(uuid4())},
    )
    assert context_override.status_code == 422


def test_g345_mints_lists_revokes_real_tenant_grant_and_audits_capability() -> None:
    client, audit = _client()
    created = client.post(
        "/v1/permission/cap-grants", headers=_headers(ADMIN), json=_cap_body()
    )
    assert created.status_code == 201, created.text
    grant_id = created.json()["id"]

    replay = client.post(
        "/v1/permission/cap-grants", headers=_headers(ADMIN), json=_cap_body()
    )
    assert replay.status_code == 201
    assert replay.json()["id"] == grant_id

    listed = client.get(
        f"/v1/permission/cap-grants?principal_subject_id={SUBJECT}",
        headers=_headers(ADMIN),
    )
    assert listed.status_code == 200
    assert {item["grant_id"] for item in listed.json()} == {grant_id}
    assert listed.json()[0]["scope_level"] == "tenant"

    revoked = client.post(
        f"/v1/permission/cap-grants/{grant_id}/revoke",
        headers=_headers(ADMIN),
        json={"reason": "test revoke", "expected_version": 1},
    )
    assert revoked.status_code == 200
    assert revoked.json()["ok"] is True
    events = audit.list_events()
    assert any(
        event.action == "Permission.CapGrant.Create"
        and event.details["capability"] == "cap.document.manage"
        for event in events
    )
    assert any(event.action == "Permission.CapGrant.Revoke" for event in events)


def test_g345_handoff_cap_does_not_write_or_bypass_g339_confirmation() -> None:
    client, rma_id = g339_client(handoff=False)
    admin_headers = {
        **g339_headers(),
        "X-EAOS-Subject-Id": str(ADMIN),
    }
    granted = client.post(
        "/v1/permission/cap-grants",
        headers=admin_headers,
        json=_cap_body(
            resource_type="pkg.platform.commercial_handoff",
            actions=["handoff_rma_credit_note"],
        ),
    )
    assert granted.status_code == 201, granted.text

    # Minting a handoff grant itself cannot create a commercial object.
    before_execute = client.get(
        f"/v1/crm/return-authorizations/{rma_id}", headers=g339_headers()
    )
    assert before_execute.json()["data"]["credit_note_id"] is None

    _restock(client, rma_id)
    _snapshot_id, insight_id = _seed(client)
    executed = client.post(
        f"/v1/brain/insights/{insight_id}/execute", headers=g339_headers()
    )
    assert executed.status_code == 200
    after_execute = client.get(
        f"/v1/crm/return-authorizations/{rma_id}", headers=g339_headers()
    )
    assert after_execute.json()["data"]["credit_note_id"] is None

    missing_confirmation = client.post(
        "/v1/platform/commercial-handoffs/rma-credit-note",
        headers=g339_headers(),
        json={
            "authorization_source": "brain",
            "insight_id": insight_id,
            "return_authorization_id": rma_id,
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": False,
        },
    )
    assert missing_confirmation.status_code == 422
    assert client.get(
        f"/v1/crm/return-authorizations/{rma_id}", headers=g339_headers()
    ).json()["data"]["credit_note_id"] is None
