"""PHX-G321 Finance GL3 bridges HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    GL_ACCOUNT_RESOURCE,
    GL_BRIDGE_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Invoices:
    def __init__(self) -> None:
        self._items: dict[UUID, ARInvoiceSnapshot] = {}

    def put(self, snap: ARInvoiceSnapshot) -> None:
        self._items[snap.id] = snap

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        return self._items.get(invoice_id)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


INVOICES = _Invoices()


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g321",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g321-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (GL_ACCOUNT_RESOURCE, {"create", "read", "archive"}),
        (GL_PERIOD_RESOURCE, {"create", "read", "close"}),
        (JOURNAL_ENTRY_RESOURCE, {"create", "read", "post"}),
        (GL_BRIDGE_RESOURCE, {"read", "update", "bridge"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(
        create_app(
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=INVOICES,
            )
        )
    )


def _create_account(client: TestClient, code: str, account_type: str) -> str:
    resp = client.post(
        "/v1/finance/gl-accounts",
        headers=_headers(),
        json={"code": code, "name": code, "account_type": account_type},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def test_g321_http_bridge_map_and_ar_invoice() -> None:
    client = _client()
    period = client.post(
        "/v1/finance/gl-periods",
        headers=_headers(),
        json={
            "code": "2026-Q1",
            "name": "2026 Q1",
            "start_at": "2026-01-01T00:00:00Z",
            "end_at": "2026-04-01T00:00:00Z",
        },
    )
    assert period.status_code == 201
    period_id = period.json()["data"]["id"]

    ar = _create_account(client, "1100", "asset")
    cash = _create_account(client, "1000", "asset")
    rev = _create_account(client, "4000", "revenue")
    tax = _create_account(client, "2100", "liability")
    cexp = _create_account(client, "5100", "expense")
    cpay = _create_account(client, "2200", "liability")

    mapped = client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={
            "ar_control": ar,
            "cash": cash,
            "revenue": rev,
            "tax_payable": tax,
            "commission_expense": cexp,
            "commission_payable": cpay,
            "expected_version": 0,
        },
    )
    assert mapped.status_code == 200
    assert mapped.json()["data"]["version"] == 1

    got = client.get("/v1/finance/gl-bridge-map", headers=_headers())
    assert got.status_code == 200
    assert got.json()["data"]["ar_control"] == ar

    invoice_id = uuid4()
    INVOICES.put(
        ARInvoiceSnapshot(
            id=invoice_id,
            tenant_id=TENANT,
            customer_id=uuid4(),
            currency="USD",
            total_amount=Decimal("42.00"),
            status="issued",
            version=1,
        )
    )
    key = str(uuid4())
    bridged = client.post(
        "/v1/finance/gl-bridges/ar-invoice-issue",
        headers=_headers(),
        json={
            "source_id": str(invoice_id),
            "period_id": period_id,
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert bridged.status_code == 201
    body = bridged.json()["data"]
    assert body["source_type"] == "ar_invoice"
    assert body["source_id"] == str(invoice_id)
    journal_id = body["journal_entry_id"]

    again = client.post(
        "/v1/finance/gl-bridges/ar-invoice-issue",
        headers=_headers(),
        json={
            "source_id": str(invoice_id),
            "period_id": period_id,
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert again.status_code == 201
    assert again.json()["data"]["journal_entry_id"] == journal_id

    journal = client.get(
        f"/v1/finance/journal-entries/{journal_id}", headers=_headers()
    )
    assert journal.status_code == 200
    assert journal.json()["data"]["status"] == "posted"


def test_g321_openapi_exposes_gl3_and_forbids_later_slices() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/finance/gl-bridge-map" in paths
    assert "/v1/finance/gl-bridges/ar-invoice-issue" in paths
    assert "/v1/finance/gl-bridges/ar-receipt-apply" in paths
    assert "/v1/finance/gl-bridges/tax-invoice-issue" in paths
    assert "/v1/finance/gl-bridges/commission-accrue" in paths

    finance_paths = " ".join(
        path for path in paths if path.startswith("/v1/finance/")
    ).casefold()
    for forbidden in (
        "enable_tax_network",
        "enable_psp_network",
    ):
        assert forbidden not in finance_paths
    assert "brain" not in finance_paths
    assert "twin" not in finance_paths

    map_schema = spec["components"]["schemas"]["GlBridgeMapView"]
    assert map_schema["additionalProperties"] is False
    posting_schema = spec["components"]["schemas"]["GlBridgePostingView"]
    assert posting_schema["additionalProperties"] is False
