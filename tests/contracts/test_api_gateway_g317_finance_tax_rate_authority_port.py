"""PHX-G317 Finance tax-rate + tax-authority-policy HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
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
    TAX_AUTHORITY_POLICY_RESOURCE,
    TAX_INVOICE_RESOURCE,
    TAX_RATE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakeTaxAuthority,
)

SUBJECT, TENANT, CUSTOMER, INVOICE = uuid4(), uuid4(), uuid4(), uuid4()


class _Invoices:
    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        if invoice_id != INVOICE:
            return None
        return ARInvoiceSnapshot(
            id=INVOICE,
            tenant_id=TENANT,
            customer_id=CUSTOMER,
            currency="USD",
            total_amount=Decimal("10.00"),
            status="issued",
            version=1,
        )


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g317",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g317-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (TAX_INVOICE_RESOURCE, {"create", "read", "issue", "void"}),
        (TAX_RATE_RESOURCE, {"create", "read", "archive"}),
        (TAX_AUTHORITY_POLICY_RESOURCE, {"read", "update"}),
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
                tax_authority_port=InMemoryFakeTaxAuthority(),
            )
        )
    )


def test_g317_policy_and_tax_rate_endpoints_and_issue_with_fake() -> None:
    client = _client()
    default = client.get(
        "/v1/finance/policies/tax-authority", headers=_headers()
    )
    assert default.status_code == 200
    assert default.json()["data"]["tax_authority_required"] is False
    updated = client.put(
        "/v1/finance/policies/tax-authority",
        headers=_headers(),
        json={"tax_authority_required": True, "expected_version": 0},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["version"] == 1
    assert (
        client.put(
            "/v1/finance/policies/tax-authority",
            headers=_headers(),
            json={
                "tax_authority_required": True,
                "expected_version": 1,
                "tenant_id": str(uuid4()),
            },
        ).status_code
        == 422
    )

    created_rate = client.post(
        "/v1/finance/tax-rates",
        headers=_headers(),
        json={
            "tax_code": "CN_VAT",
            "tax_name": "CN VAT",
            "rate_percent": "13.0000",
        },
    )
    assert created_rate.status_code == 201
    rate = created_rate.json()["data"]
    assert rate["tax_code"] == "CN_VAT"
    fetched_rate = client.get(
        f"/v1/finance/tax-rates/{rate['id']}", headers=_headers()
    )
    assert fetched_rate.status_code == 200
    assert fetched_rate.json()["data"]["status"] == "active"

    created = client.post(
        "/v1/finance/tax-invoices",
        headers=_headers(),
        json={
            "invoice_id": str(INVOICE),
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
            "tax_code": "CN_VAT",
        },
    )
    assert created.status_code == 201
    tax_invoice = created.json()["data"]
    issued = client.post(
        f"/v1/finance/tax-invoices/{tax_invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    body = issued.json()["data"]
    assert body["authority_status"] == "validated"
    assert body["authority_ref"].startswith("fake-authority-")
    assert body["tax_code"] == "CN_VAT"


def test_g317_openapi_exposes_tax2_without_filing_or_network() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/policies/tax-authority" in spec["paths"]
    assert "/v1/finance/tax-rates" in spec["paths"]
    assert "/v1/finance/tax-rates/{tax_rate_id}" in spec["paths"]
    paths = " ".join(spec["paths"]).casefold()
    for forbidden in (
        "tax-filing",
        "tax_filing",
        "enable_tax_network",
        "enable-tax-network",
        "live-authority",
        "live_authority",
        "gl",
        "journal",
        "coa",
    ):
        assert forbidden not in paths
    tax_invoice_paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/finance/tax-invoices")
    ).casefold()
    for forbidden in ("authority", "rate-port", "rate_port"):
        assert forbidden not in tax_invoice_paths
    assert (
        spec["components"]["schemas"]["CreateTaxRateRequest"][
            "additionalProperties"
        ]
        is False
    )
    assert (
        spec["components"]["schemas"]["SetTaxAuthorityPolicyRequest"][
            "additionalProperties"
        ]
        is False
    )
