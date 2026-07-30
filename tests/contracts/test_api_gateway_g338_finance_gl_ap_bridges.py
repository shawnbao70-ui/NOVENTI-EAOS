"""PHX-G338 Finance GL AP bridge HTTP contracts."""

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
    ApBillSnapshot,
    ApPaymentSnapshot,
    GL_ACCOUNT_RESOURCE,
    GL_BRIDGE_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Invoices:
    def get_ar_invoice_snapshot(self, _invoice_id: UUID) -> ARInvoiceSnapshot | None:
        return None


class _Bills:
    def __init__(self) -> None:
        self.items: dict[UUID, ApBillSnapshot] = {}

    def get_ap_bill_snapshot(self, bill_id: UUID) -> ApBillSnapshot | None:
        return self.items.get(bill_id)


class _Payments:
    def __init__(self) -> None:
        self.items: dict[UUID, ApPaymentSnapshot] = {}

    def get_ap_payment_snapshot(
        self, payment_id: UUID
    ) -> ApPaymentSnapshot | None:
        return self.items.get(payment_id)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g338",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g338-http",
    }


def _client(
    *, grant: bool = True
) -> tuple[TestClient, _Bills, _Payments]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
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
    bills, payments = _Bills(), _Payments()
    return (
        TestClient(
            create_app(
                finance_service=FinanceService(
                    permission,
                    repository=InMemoryFinanceRepository(tenant_id=TENANT),
                    audit_log=audit,
                    ar_invoice_reader=_Invoices(),
                    ap_bill_reader=bills,
                    ap_payment_reader=payments,
                )
            )
        ),
        bills,
        payments,
    )


def _account(client: TestClient, code: str, account_type: str) -> str:
    response = client.post(
        "/v1/finance/gl-accounts",
        headers=_headers(),
        json={"code": code, "name": code, "account_type": account_type},
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _period(client: TestClient) -> str:
    response = client.post(
        "/v1/finance/gl-periods",
        headers=_headers(),
        json={
            "code": "2026-Q1",
            "name": "2026 Q1",
            "start_at": "2026-01-01T00:00:00Z",
            "end_at": "2026-04-01T00:00:00Z",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_g338_ap_bridges_post_and_apply_idempotently() -> None:
    client, bills, payments = _client()
    period_id = _period(client)
    accounts = {
        "ar_control": _account(client, "1100", "asset"),
        "cash": _account(client, "1000", "asset"),
        "revenue": _account(client, "4000", "revenue"),
        "tax_payable": _account(client, "2100", "liability"),
        "commission_expense": _account(client, "5100", "expense"),
        "commission_payable": _account(client, "2200", "liability"),
        "ap_control": _account(client, "2000", "liability"),
        "ap_expense": _account(client, "5000", "expense"),
    }
    mapped = client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={**accounts, "expected_version": 0},
    )
    assert mapped.status_code == 200
    assert mapped.json()["data"]["ap_control"] == accounts["ap_control"]

    bill_id, payment_id = uuid4(), uuid4()
    bills.items[bill_id] = ApBillSnapshot(
        id=bill_id,
        tenant_id=TENANT,
        currency="USD",
        total_amount=Decimal("50.00"),
        status="posted",
    )
    payments.items[payment_id] = ApPaymentSnapshot(
        id=payment_id,
        tenant_id=TENANT,
        currency="USD",
        amount=Decimal("50.00"),
        status="applied",
    )
    bill_key, payment_key = str(uuid4()), str(uuid4())
    bill = client.post(
        "/v1/finance/gl-bridges/ap-bill-post",
        headers=_headers(),
        json={
            "source_id": str(bill_id),
            "period_id": period_id,
            "idempotency_key": bill_key,
            "human_confirm": True,
        },
    )
    assert bill.status_code == 201
    assert bill.json()["data"]["source_type"] == "ap_bill"
    payment = client.post(
        "/v1/finance/gl-bridges/ap-payment-apply",
        headers=_headers(),
        json={
            "source_id": str(payment_id),
            "period_id": period_id,
            "idempotency_key": payment_key,
            "human_confirm": True,
        },
    )
    assert payment.status_code == 201
    assert payment.json()["data"]["source_type"] == "ap_payment"
    again = client.post(
        "/v1/finance/gl-bridges/ap-bill-post",
        headers=_headers(),
        json={
            "source_id": str(bill_id),
            "period_id": period_id,
            "idempotency_key": bill_key,
            "human_confirm": True,
        },
    )
    assert again.status_code == 201
    assert again.json()["data"]["id"] == bill.json()["data"]["id"]

    journal = client.get(
        f"/v1/finance/journal-entries/{bill.json()['data']['journal_entry_id']}",
        headers=_headers(),
    )
    assert journal.status_code == 200
    lines = journal.json()["data"]["lines"]
    assert {(line["account_id"], line["debit"], line["credit"]) for line in lines} == {
        (accounts["ap_expense"], "50.00", "0.00"),
        (accounts["ap_control"], "0.00", "50.00"),
    }


def test_g338_denies_draft_bill_and_requires_open_period() -> None:
    client, bills, _payments = _client()
    period_id = _period(client)
    accounts = {
        "ar_control": _account(client, "1100", "asset"),
        "cash": _account(client, "1000", "asset"),
        "revenue": _account(client, "4000", "revenue"),
        "tax_payable": _account(client, "2100", "liability"),
        "commission_expense": _account(client, "5100", "expense"),
        "commission_payable": _account(client, "2200", "liability"),
        "ap_control": _account(client, "2000", "liability"),
        "ap_expense": _account(client, "5000", "expense"),
    }
    assert client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={**accounts, "expected_version": 0},
    ).status_code == 200
    draft_id = uuid4()
    bills.items[draft_id] = ApBillSnapshot(
        id=draft_id,
        tenant_id=TENANT,
        currency="USD",
        total_amount=Decimal("10.00"),
        status="draft",
    )
    draft = client.post(
        "/v1/finance/gl-bridges/ap-bill-post",
        headers=_headers(),
        json={
            "source_id": str(draft_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert draft.status_code == 409
    assert draft.json()["detail"]["message"] == "ap bill is not posted"
    assert client.post(
        f"/v1/finance/gl-periods/{period_id}/close",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    closed = client.post(
        "/v1/finance/gl-bridges/ap-bill-post",
        headers=_headers(),
        json={
            "source_id": str(draft_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert closed.status_code == 409
    assert closed.json()["detail"]["message"] == "gl period is not open"


def test_g338_denies_ungranted_bridge() -> None:
    client, _bills, _payments = _client(grant=False)
    response = client.post(
        "/v1/finance/gl-bridges/ap-bill-post",
        headers=_headers(),
        json={
            "source_id": str(uuid4()),
            "period_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 403
