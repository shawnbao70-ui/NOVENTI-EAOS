"""PHX-G322 Finance GL4 FX revaluation HTTP contracts."""

from __future__ import annotations

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
    GL_FX_REVALUATION_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakeFxRate,
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
        correlation_id="corr-g322",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g322-http",
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
        (GL_FX_REVALUATION_RESOURCE, {"create", "read", "post"}),
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
                fx_rate_port=InMemoryFakeFxRate(),
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


def test_g322_http_fx_revaluation_create_post() -> None:
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
    accounts = {
        key: _create_account(client, code, typ)
        for key, code, typ in (
            ("ar", "1100", "asset"),
            ("cash", "1000", "asset"),
            ("rev", "4000", "revenue"),
            ("tax", "2100", "liability"),
            ("cexp", "5100", "expense"),
            ("cpay", "2200", "liability"),
            ("fxg", "7100", "revenue"),
            ("fxl", "7200", "expense"),
        )
    }
    mapped = client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={
            "ar_control": accounts["ar"],
            "cash": accounts["cash"],
            "revenue": accounts["rev"],
            "tax_payable": accounts["tax"],
            "commission_expense": accounts["cexp"],
            "commission_payable": accounts["cpay"],
            "fx_gain": accounts["fxg"],
            "fx_loss": accounts["fxl"],
            "expected_version": 0,
        },
    )
    assert mapped.status_code == 200

    created = client.post(
        "/v1/finance/gl-fx-revaluations",
        headers=_headers(),
        json={
            "period_id": period_id,
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": "8.00",
            "side": "gain",
            "idempotency_key": str(uuid4()),
            "rate": "0.91000000",
        },
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["status"] == "draft"
    revaluation_id = body["id"]

    got = client.get(
        f"/v1/finance/gl-fx-revaluations/{revaluation_id}",
        headers=_headers(),
    )
    assert got.status_code == 200

    posted = client.post(
        f"/v1/finance/gl-fx-revaluations/{revaluation_id}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert posted.status_code == 200
    assert posted.json()["data"]["status"] == "posted"
    assert posted.json()["data"]["journal_entry_id"] is not None


def test_g322_openapi_exposes_gl4_and_forbids_later_slices() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/finance/gl-fx-revaluations" in paths
    assert "/v1/finance/gl-fx-revaluations/{revaluation_id}" in paths
    assert "/v1/finance/gl-fx-revaluations/{revaluation_id}/post" in paths

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
    schema = spec["components"]["schemas"]["GlFxRevaluationView"]
    assert schema["additionalProperties"] is False
