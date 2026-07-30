"""PHX-G371 Treasury transfer + FX HTTP contracts."""

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
    TREASURY_TRANSFER_RESOURCE,
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
        correlation_id="corr-g371",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g371-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=TREASURY_TRANSFER_RESOURCE,
        actions={"create", "read", "post"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    return TestClient(
        create_app(
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=_Invoices(),
            ),
        )
    )


def test_g371_creates_posts_and_reads_treasury_transfer_with_fx() -> None:
    client = _client()
    create_key = str(uuid4())
    created = client.post(
        "/v1/finance/treasury-transfers",
        headers=_headers(),
        json={
            "from_account_ref": "BANK-USD-1",
            "to_account_ref": "BANK-CNY-1",
            "amount": "10.00",
            "currency": "USD",
            "functional_currency": "CNY",
            "fx_rate": "7.12345678",
            "functional_amount": "71.23",
            "idempotency_key": create_key,
        },
    )
    assert created.status_code == 201, created.json()
    transfer = created.json()["data"]
    assert {
        key: transfer[key]
        for key in (
            "from_account_ref",
            "to_account_ref",
            "amount",
            "currency",
            "functional_currency",
            "fx_rate",
            "functional_amount",
            "status",
        )
    } == {
        "from_account_ref": "BANK-USD-1",
        "to_account_ref": "BANK-CNY-1",
        "amount": "10.00",
        "currency": "USD",
        "functional_currency": "CNY",
        "fx_rate": "7.12345678",
        "functional_amount": "71.23",
        "status": "draft",
    }

    replay = client.post(
        "/v1/finance/treasury-transfers",
        headers=_headers(),
        json={
            "from_account_ref": "BANK-USD-1",
            "to_account_ref": "BANK-CNY-1",
            "amount": "10.00",
            "currency": "USD",
            "functional_currency": "CNY",
            "fx_rate": "7.12345678",
            "functional_amount": "71.23",
            "idempotency_key": create_key,
        },
    )
    assert replay.status_code == 201, replay.json()
    assert replay.json()["data"]["id"] == transfer["id"]

    same_currency = client.post(
        "/v1/finance/treasury-transfers",
        headers=_headers(),
        json={
            "from_account_ref": str(uuid4()),
            "to_account_ref": "CASH-CNY",
            "amount": "5.00",
            "currency": "CNY",
            "idempotency_key": str(uuid4()),
        },
    )
    assert same_currency.status_code == 201, same_currency.json()
    assert {
        key: same_currency.json()["data"][key]
        for key in ("functional_currency", "fx_rate", "functional_amount")
    } == {
        "functional_currency": "CNY",
        "fx_rate": "1.00000000",
        "functional_amount": "5.00",
    }

    posted = client.post(
        f"/v1/finance/treasury-transfers/{transfer['id']}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert posted.status_code == 200, posted.json()
    assert posted.json()["data"]["status"] == "posted"

    fetched = client.get(
        f"/v1/finance/treasury-transfers/{transfer['id']}",
        headers=_headers(),
    )
    assert fetched.status_code == 200, fetched.json()
    assert fetched.json()["data"]["status"] == "posted"


def test_g371_rejects_missing_fx_same_account_and_post_without_confirm() -> None:
    client = _client()
    assert (
        client.post(
            "/v1/finance/treasury-transfers",
            headers=_headers(),
            json={
                "from_account_ref": "BANK-A",
                "to_account_ref": "BANK-B",
                "amount": "10.00",
                "currency": "USD",
                "functional_currency": "CNY",
                "idempotency_key": str(uuid4()),
            },
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/v1/finance/treasury-transfers",
            headers=_headers(),
            json={
                "from_account_ref": "BANK-A",
                "to_account_ref": "BANK-A",
                "amount": "10.00",
                "currency": "CNY",
                "idempotency_key": str(uuid4()),
            },
        ).status_code
        == 400
    )

    draft = client.post(
        "/v1/finance/treasury-transfers",
        headers=_headers(),
        json={
            "from_account_ref": "BANK-A",
            "to_account_ref": "BANK-B",
            "amount": "10.00",
            "currency": "CNY",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    response = client.post(
        f"/v1/finance/treasury-transfers/{draft['id']}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": False},
    )
    assert response.status_code == 422


def test_g371_openapi_exposes_treasury_transfer_routes() -> None:
    client = _client()
    paths = client.get("/openapi.json").json()["paths"]
    assert "/v1/finance/treasury-transfers" in paths
    assert "/v1/finance/treasury-transfers/{transfer_id}" in paths
    assert "/v1/finance/treasury-transfers/{transfer_id}/post" in paths
