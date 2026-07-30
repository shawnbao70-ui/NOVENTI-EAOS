"""PHX-G521 CRM Customer 360 read-only UI contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.customer360 import (
    CUSTOMER360_RESOURCE,
    AssembledCustomer360Repository,
    Customer360Service,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    CRMService,
)
from noventi.finance.repository import InMemoryFinanceRepository

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
        correlation_id="corr-g521-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g521-http",
    }


def _client(*, grant_360: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
        (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
    ):
        assert permission.grant(
            _context(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    if grant_360:
        assert permission.grant(
            _context(),
            principal_subject_id=SUBJECT,
            resource_type=CUSTOMER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    finance_repo = InMemoryFinanceRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission, repository=crm_repo, audit_log=audit
            ),
            customer360_service=Customer360Service(
                permission,
                repository=AssembledCustomer360Repository(crm_repo, finance_repo),
            ),
            permission_service=permission,
        )
    )


def _customer_with_opportunity(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G521", "display_name": "G521 Customer"},
    ).json()["data"]
    assert (
        client.post(
            "/v1/crm/opportunities",
            headers=_headers(),
            json={"customer_id": customer["id"], "title": "G521 Opp"},
        ).status_code
        == 201
    )
    return customer


def test_g521_customer360_projection_is_read_only_and_minimal() -> None:
    client = _client()
    customer = _customer_with_opportunity(client)
    response = client.get(
        f"/v1/crm/customers/{customer['id']}/360", headers=_headers()
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data) == {
        "customer_id",
        "customer_code",
        "display_name",
        "commercial_hold",
        "opportunities_count",
        "open_sales_orders_count",
        "open_delivery_orders_count",
        "invoice_traces",
        "applied_receipt_traces",
        "credit_note_traces",
    }
    assert data["customer_id"] == customer["id"]
    assert data["opportunities_count"] == 1
    assert data["invoice_traces"] == []
    assert data["applied_receipt_traces"] == []
    assert data["credit_note_traces"] == []


def test_g521_customer360_fails_closed_without_permission() -> None:
    client = _client(grant_360=False)
    customer = _customer_with_opportunity(client)
    assert (
        client.get(
            f"/v1/crm/customers/{customer['id']}/360", headers=_headers()
        ).status_code
        == 403
    )


def test_g521_terminal_exposes_360_without_hold_or_issue_writes() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "crmCustomer360Detail",
        "crmCustomer360State",
        "crmCustomer360InvoiceList",
        "crmCustomer360ReceiptList",
        "crmCustomer360CreditList",
        "btnCrmRefreshCustomer360",
    ):
        assert f'id="{control}"' in html
    assert 'id="btnCrmCommercialHold"' not in html
    chunk = app[
        app.index("function clearCrmCustomer360") :
        app.index("async function loadCrmCustomers")
    ]
    assert "crmCustomer360" in chunk
    assert "createCrmTraceRow" in chunk
    assert "commercial-hold" not in chunk
    assert "/issue" not in chunk
    assert "delivery-order" not in chunk
    assert "ar-invoice" not in chunk
    assert "tenant_id" not in chunk
    assert "clearCrmCustomer360" in app
    assert "loadCrmCustomer360" in app


def test_g521_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_CUSTOMER_360_UI_G521_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_CUSTOMER_360_G521_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G521" in roadmap
    assert "G522–G527 remain closed" in roadmap
    assert "PHX-G521 COMPLETE" in acceptance
    assert "53 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G521" in manifest
