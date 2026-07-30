"""PHX-G319 Finance GL1 chart + journal HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    GL_ACCOUNT_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT = uuid4(), uuid4()


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
        correlation_id="corr-g319",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g319-http",
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
                ar_invoice_reader=_Invoices(),
            )
        )
    )


def test_g319_http_gl_account_and_journal_happy_path() -> None:
    client = _client()
    period = client.post(
        "/v1/finance/gl-periods",
        headers=_headers(),
        json={
            "code": "2026-Q1",
            "start_at": "2026-01-01T00:00:00Z",
            "end_at": "2026-04-01T00:00:00Z",
        },
    )
    assert period.status_code == 201
    period_id = period.json()["data"]["id"]

    cash = client.post(
        "/v1/finance/gl-accounts",
        headers=_headers(),
        json={
            "code": "1000",
            "name": "Cash",
            "account_type": "asset",
        },
    )
    assert cash.status_code == 201
    cash_id = cash.json()["data"]["id"]
    revenue = client.post(
        "/v1/finance/gl-accounts",
        headers=_headers(),
        json={
            "code": "4000",
            "name": "Revenue",
            "account_type": "revenue",
        },
    )
    assert revenue.status_code == 201
    revenue_id = revenue.json()["data"]["id"]

    got = client.get(
        f"/v1/finance/gl-accounts/{cash_id}", headers=_headers()
    )
    assert got.status_code == 200
    assert got.json()["data"]["code"] == "1000"

    created = client.post(
        "/v1/finance/journal-entries",
        headers=_headers(),
        json={
            "currency": "USD",
            "period_id": period_id,
            "memo": "sale",
            "idempotency_key": str(uuid4()),
            "lines": [
                {
                    "account_id": cash_id,
                    "debit": "25.00",
                    "credit": "0.00",
                },
                {
                    "account_id": revenue_id,
                    "debit": "0.00",
                    "credit": "25.00",
                },
            ],
        },
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["status"] == "draft"
    entry_id = body["id"]

    fetched = client.get(
        f"/v1/finance/journal-entries/{entry_id}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert len(fetched.json()["data"]["lines"]) == 2

    posted = client.post(
        f"/v1/finance/journal-entries/{entry_id}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert posted.status_code == 200
    assert posted.json()["data"]["status"] == "posted"


def test_g319_openapi_exposes_gl1_and_forbids_later_slices() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/finance/gl-accounts" in paths
    assert "/v1/finance/gl-accounts/{account_id}" in paths
    assert "/v1/finance/journal-entries" in paths
    assert "/v1/finance/journal-entries/{entry_id}" in paths
    assert "/v1/finance/journal-entries/{entry_id}/post" in paths

    finance_paths = " ".join(
        path for path in paths if path.startswith("/v1/finance/")
    ).casefold()
    for forbidden in (
        "period-close",
        "period_close",
        "enable_tax_network",
        "enable_psp_network",
    ):
        assert forbidden not in finance_paths
    assert "brain" not in finance_paths
    assert "twin" not in finance_paths

    account_schema = spec["components"]["schemas"]["GlAccountView"]
    assert account_schema["additionalProperties"] is False
    entry_schema = spec["components"]["schemas"]["JournalEntryView"]
    assert entry_schema["additionalProperties"] is False
