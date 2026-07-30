"""PHX-G524 CRM AR Invoice create/read/issue UI contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)

ROOT = Path(__file__).resolve().parents[2]
SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g524-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g524-http",
    }


def _client(*, grant: bool = True, invoice: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        for resource, actions in (
            (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
            (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
            (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
            (QUOTE_RESOURCE, {"create", "read", "update", "archive", "issue"}),
            (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
            (CONVERSION_RESOURCE, {"create", "read", "convert"}),
            (SALES_ORDER_RESOURCE, {"create", "read", "confirm"}),
            (DELIVERY_ORDER_RESOURCE, {"create", "read", "release"}),
        ):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource,
                actions=actions,
                scope_level=ScopeLevel.TENANT,
            ).ok
        if invoice:
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=AR_INVOICE_RESOURCE,
                actions={"create", "read", "issue"},
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def _released_delivery_order(client: TestClient, suffix: str = "A") -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C-G524-{suffix}", "display_name": f"G524 {suffix}"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": f"G524 Opp {suffix}"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": f"G524 Req {suffix}",
            "description": None,
        },
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": requirement["id"],
            "currency": "USD",
            "notes": None,
        },
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=_headers(),
            json={
                "description": f"Line {suffix}",
                "quantity": "1.000",
                "unit_price": "30.00",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    delivery_order = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    released = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/release",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert released.status_code == 200
    return released.json()["data"]


def test_g524_create_issue_is_idempotent_and_do_scoped() -> None:
    client = _client()
    delivery_order = _released_delivery_order(client)
    create_key = str(uuid4())
    first = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/ar-invoice",
        headers=_headers(),
        json={"idempotency_key": create_key},
    )
    assert first.status_code == 201
    invoice = first.json()["data"]
    assert invoice["status"] == "draft"
    assert invoice["delivery_order_id"] == delivery_order["id"]
    retry_create = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/ar-invoice",
        headers=_headers(),
        json={"idempotency_key": create_key},
    )
    assert retry_create.status_code == 201
    assert retry_create.json()["data"]["id"] == invoice["id"]
    detail = client.get(
        f"/v1/crm/ar-invoices/{invoice['id']}", headers=_headers()
    )
    assert detail.status_code == 200
    issue_key = str(uuid4())
    issued = client.post(
        f"/v1/crm/ar-invoices/{invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": issue_key, "human_confirm": True},
    )
    assert issued.status_code == 200
    assert issued.json()["data"]["status"] == "issued"
    retry_issue = client.post(
        f"/v1/crm/ar-invoices/{invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": issue_key, "human_confirm": True},
    )
    assert retry_issue.status_code == 200
    assert retry_issue.json()["data"]["id"] == invoice["id"]


def test_g524_invoice_fails_closed_without_permission() -> None:
    no_invoice = _client(invoice=False)
    delivery_order = _released_delivery_order(no_invoice, "B")
    assert (
        no_invoice.post(
            f"/v1/crm/delivery-orders/{delivery_order['id']}/ar-invoice",
            headers=_headers(),
            json={"idempotency_key": str(uuid4())},
        ).status_code
        == 403
    )
    denied = _client(grant=False)
    assert (
        denied.post(
            f"/v1/crm/ar-invoices/{uuid4()}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )


def test_g524_terminal_exposes_invoice_without_void_or_list() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmCreateArInvoice",
        "crmCreateArInvoiceForm",
        "crmCreateArInvoiceConfirmed",
        "crmArInvoiceDetail",
        "btnCrmIssueArInvoice",
        "crmIssueArInvoiceForm",
        "crmIssueArInvoiceConfirmed",
    ):
        assert f'id="{control}"' in html
    assert "GET /v1/crm/ar-invoices?" not in app
    assert "crmArInvoices:" not in app
    chunk = app[
        app.index("async function submitCrmCreateArInvoice") :
        app.index("async function submitCrmCreateReturnAuthorization")
    ]
    assert "crmDeliveryOrderArInvoice" in chunk
    assert "crmArInvoiceIssue" in chunk
    assert "human_confirm: true" in chunk
    assert "/void" not in chunk
    assert "tenant_id" not in chunk


def test_g524_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_AR_INVOICE_UI_G524_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_AR_INVOICE_G524_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G524" in roadmap
    assert "G525–G527 remain closed" in roadmap
    assert "PHX-G524 COMPLETE" in acceptance
    assert "65 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G524" in manifest
