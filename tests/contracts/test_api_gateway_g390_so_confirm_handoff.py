"""PHX-G390 SO.confirm commercial handoff — authorize ≠ auto-confirm."""

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
        correlation_id="corr-g390",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g390-http",
    }


def _build(*, handoff: bool = True, brain_execute: bool = True):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ADMIN},
        principal_eligibility=_Eligibility(),
    )
    admin = _ctx(ADMIN)
    for resource, actions in (
        (
            CUSTOMER_RESOURCE,
            {"create", "read", "update", "archive"},
        ),
        (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
        (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
        (QUOTE_RESOURCE, {"create", "read", "update", "issue"}),
        (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
        (CONVERSION_RESOURCE, {"convert", "read"}),
        (SALES_ORDER_RESOURCE, {"create", "read", "confirm"}),
        (
            "brain_insight",
            {"publish", "read"} | ({"execute"} if brain_execute else set()),
        ),
        ("twin_snapshot", {"write", "read", "authorize"}),
        (
            "pkg.platform.commercial_handoff",
            {"handoff_so_confirm"} if handoff else set(),
        ),
    ):
        if not actions:
            continue
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
    handoff_service = CommercialHandoffService(
        permission,
        brain=brain,
        twin=twin,
        crm=crm,
        sales_orders=crm,
        audit_log=audit,
    )
    client = TestClient(
        create_app(
            permission_service=permission,
            twin_service=twin,
            brain_service=brain,
            crm_service=crm,
            commercial_handoff_service=handoff_service,
        )
    )
    return client, crm, audit


def _created_sales_order(client: TestClient) -> str:
    headers = _headers()
    customer = client.post(
        "/v1/crm/customers",
        headers=headers,
        json={"code": f"G390-{uuid4().hex[:8]}", "display_name": "G390"},
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
            json={
                "description": "line",
                "quantity": "1",
                "unit_price": "10",
            },
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
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=headers,
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert sales_order["status"] == "created"
    return sales_order["id"]


def _seed_insight(client: TestClient) -> str:
    twin = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": f"pkg.crm.sales_order:{uuid4()}",
            "state": {"ready": True},
            "source_ref": "g390",
            "reason": "so confirm advisory",
            "confidence": 0.8,
        },
    )
    assert twin.status_code == 201, twin.text
    snapshot_id = twin.json()["data"]
    insight = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "confirm SO",
            "confidence": 0.75,
            "source_ref": "g390",
            "reason": "advisory",
            "bias_notes": "sample",
            "twin_ref": snapshot_id,
            "advisory": True,
        },
    )
    assert insight.status_code == 201, insight.text
    return insight.json()["data"]


def test_g390_so_confirm_handoff_does_not_auto_confirm() -> None:
    client, _crm, audit = _build()
    sales_order_id = _created_sales_order(client)
    insight_id = _seed_insight(client)
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
    data = response.json()["data"]
    assert data["auto_confirm"] is False
    assert data["sales_order_id"] == sales_order_id
    assert data["sales_order_status"] == "created"
    assert data["approval_ref"] == f"commercial-handoff:so-confirm:{insight_id}"
    assert data["authorization_audit_id"] is not None

    so = client.get(f"/v1/crm/sales-orders/{sales_order_id}", headers=_headers())
    assert so.status_code == 200
    assert so.json()["data"]["status"] == "created"

    events = [
        event
        for event in audit.list_events()
        if event.action == "Platform.CommercialHandoff.SoConfirm"
    ]
    assert any(event.result == "ok" for event in events)
    ok = next(event for event in events if event.result == "ok")
    assert ok.details["auto_confirm"] is False
    assert ok.details["authorization_audit_id"] is not None


def test_g390_denies_without_handoff_grant() -> None:
    client, _crm, _audit = _build(handoff=False)
    sales_order_id = _created_sales_order(client)
    insight_id = _seed_insight(client)
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
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "COMMERCIAL_HANDOFF_FORBIDDEN"


def test_g390_openapi_path_present() -> None:
    client, _crm, _audit = _build()
    paths = client.get("/openapi.json").json()["paths"]
    assert "/v1/platform/commercial-handoffs/so-confirm" in paths
    assert "post" in paths["/v1/platform/commercial-handoffs/so-confirm"]
