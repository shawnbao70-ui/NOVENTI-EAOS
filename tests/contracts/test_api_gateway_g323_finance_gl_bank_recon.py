"""PHX-G323 Finance GL5 bank recon HTTP contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.finance.models import ARReceipt, ReceiptStatus
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    BANK_STATEMENT_RESOURCE,
    GL_ACCOUNT_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT = uuid4(), uuid4()
REPO = InMemoryFinanceRepository(tenant_id=TENANT)


class _Invoices:
    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        return None


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g323",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g323-http",
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
        (BANK_STATEMENT_RESOURCE, {"create", "read", "match", "clear"}),
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
                repository=REPO,
                audit_log=audit,
                ar_invoice_reader=_Invoices(),
            )
        )
    )


def test_g323_http_bank_statement_match_clear() -> None:
    client = _client()
    receipt = ARReceipt(
        id=uuid4(),
        tenant_id=TENANT,
        customer_id=uuid4(),
        code="RCPT-HTTP",
        currency="USD",
        amount=Decimal("10.00"),
        idempotency_key=uuid4(),
        status=ReceiptStatus.APPLIED,
        created_at=datetime.now(timezone.utc),
        ar_invoice_id=uuid4(),
        ar_invoice_version=1,
        apply_key=uuid4(),
        applied_at=datetime.now(timezone.utc),
    )
    REPO.add_receipt(receipt)

    created = client.post(
        "/v1/finance/bank-statements",
        headers=_headers(),
        json={
            "account_ref": "BANK-001",
            "statement_date": "2026-03-01T00:00:00Z",
            "currency": "USD",
            "lines": [
                {"amount": "10.00", "description": "deposit"},
            ],
        },
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["status"] == "open"
    statement_id = body["id"]
    line_id = body["lines"][0]["id"]

    matched = client.post(
        f"/v1/finance/bank-statements/{statement_id}/lines/{line_id}/match",
        headers=_headers(),
        json={"matched_receipt_id": str(receipt.id)},
    )
    assert matched.status_code == 200
    assert matched.json()["data"]["lines"][0]["status"] == "matched"

    cleared = client.post(
        f"/v1/finance/bank-statements/{statement_id}/clear",
        headers=_headers(),
        json={"human_confirm": True},
    )
    assert cleared.status_code == 200
    assert cleared.json()["data"]["status"] == "reconciled"

    got = client.get(
        f"/v1/finance/bank-statements/{statement_id}", headers=_headers()
    )
    assert got.status_code == 200
    assert got.json()["data"]["status"] == "reconciled"


def test_g323_openapi_exposes_gl5_and_forbids_parked() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/finance/bank-statements" in paths
    assert "/v1/finance/bank-statements/{statement_id}" in paths
    assert (
        "/v1/finance/bank-statements/{statement_id}/lines/{line_id}/match"
        in paths
    )
    assert "/v1/finance/bank-statements/{statement_id}/clear" in paths

    finance_paths = " ".join(
        path for path in paths if path.startswith("/v1/finance/")
    ).casefold()
    for forbidden in (
        "enable_tax_network",
        "enable_psp_network",
        "/ap/",
        "retention",
    ):
        assert forbidden not in finance_paths
    assert "brain" not in finance_paths
    assert "twin" not in finance_paths
    schema = spec["components"]["schemas"]["BankStatementView"]
    assert schema["additionalProperties"] is False
