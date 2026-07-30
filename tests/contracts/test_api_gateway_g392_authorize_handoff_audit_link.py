"""PHX-G392 Authorize ↔ handoff audit correlation contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.brain.service import BrainService
from eaos_platform.commercial_handoff.service import CommercialHandoffService
from eaos_platform.twin.service import TwinService
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)

SUBJECT, ADMIN, TENANT = uuid4(), uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(subject_id: UUID = SUBJECT) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g392",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g392-http",
    }


def _build() -> tuple[TestClient, InMemoryAuditLog]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ADMIN},
        principal_eligibility=_Eligibility(),
    )
    admin = _ctx(ADMIN)
    for resource, actions in (
        (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
        (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
        (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
        (QUOTE_RESOURCE, {"create", "read", "update", "issue"}),
        (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
        (CONVERSION_RESOURCE, {"convert", "read"}),
        (SALES_ORDER_RESOURCE, {"create", "read", "confirm"}),
        ("brain_insight", {"publish", "read", "execute"}),
        ("twin_snapshot", {"write", "read", "authorize"}),
        ("pkg.platform.commercial_handoff", {"handoff_so_confirm"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    twin = TwinService(permission, audit_log=audit)
    brain = BrainService(permission, audit_log=audit, twin_reader=twin)
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    client = TestClient(
        create_app(
            permission_service=permission,
            twin_service=twin,
            brain_service=brain,
            crm_service=crm,
            commercial_handoff_service=CommercialHandoffService(
                permission,
                brain=brain,
                twin=twin,
                crm=crm,
                sales_orders=crm,
                audit_log=audit,
            ),
        )
    )
    return client, audit


def _created_sales_order(client: TestClient) -> str:
    headers = _headers()
    customer = client.post(
        "/v1/crm/customers",
        headers=headers,
        json={"code": f"G392-{uuid4().hex[:8]}", "display_name": "G392"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=headers,
        json={"customer_id": customer["id"], "title": "Opp"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=headers,
        json={"opportunity_id": opportunity["id"], "title": "Req"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=headers,
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=headers,
            json={"description": "line", "quantity": "1", "unit_price": "10"},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=headers,
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=headers,
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    return client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=headers,
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]["id"]


def test_g392_handoff_links_authorization_audit_id() -> None:
    client, audit = _build()
    sales_order_id = _created_sales_order(client)
    snapshot_id = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": f"pkg.crm.sales_order:{sales_order_id}",
            "state": {"ready": True},
            "source_ref": "g392",
            "reason": "link",
            "confidence": 0.7,
        },
    ).json()["data"]
    insight_id = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "link audit",
            "confidence": 0.7,
            "source_ref": "g392",
            "reason": "link",
            "twin_ref": snapshot_id,
            "advisory": True,
        },
    ).json()["data"]

    response = client.post(
        "/v1/platform/commercial-handoffs/so-confirm",
        headers=_headers(),
        json={
            "authorization_source": "brain",
            "insight_id": insight_id,
            "sales_order_id": sales_order_id,
            "human_confirm": True,
        },
    )
    assert response.status_code == 200, response.text
    auth_audit_id = response.json()["data"]["authorization_audit_id"]
    assert auth_audit_id is not None
    handoff_audit_id = response.json()["audit_id"]
    assert handoff_audit_id is not None
    assert str(auth_audit_id) != str(handoff_audit_id)

    brain_ok = [
        event
        for event in audit.list_events()
        if event.action == "Brain.RequestExecution" and event.result == "ok"
    ]
    assert brain_ok
    assert str(brain_ok[-1].id) == str(auth_audit_id)

    handoff_ok = [
        event
        for event in audit.list_events()
        if event.action == "Platform.CommercialHandoff.SoConfirm"
        and event.result == "ok"
    ]
    assert handoff_ok
    assert handoff_ok[-1].details["authorization_audit_id"] == str(auth_audit_id)
    assert str(handoff_ok[-1].id) == str(handoff_audit_id)
