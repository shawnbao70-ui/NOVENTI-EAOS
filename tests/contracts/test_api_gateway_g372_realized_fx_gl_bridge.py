"""PHX-G372 Realized FX → GL bridge HTTP contracts."""

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
from noventi.finance.models import RealizedFxEvent, RealizedFxSide
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
    def get_ar_invoice_snapshot(
        self, _invoice_id: UUID
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
        correlation_id="corr-g372",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g372-http",
    }


def _client(
    *, grant: bool = True
) -> tuple[TestClient, InMemoryFinanceRepository]:
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
    repo = InMemoryFinanceRepository(tenant_id=TENANT)
    return (
        TestClient(
            create_app(
                finance_service=FinanceService(
                    permission,
                    repository=repo,
                    audit_log=audit,
                    ar_invoice_reader=_Invoices(),
                )
            )
        ),
        repo,
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


def _seed_map(client: TestClient) -> dict[str, str]:
    accounts = {
        "ar_control": _account(client, "1100", "asset"),
        "cash": _account(client, "1000", "asset"),
        "revenue": _account(client, "4000", "revenue"),
        "tax_payable": _account(client, "2100", "liability"),
        "commission_expense": _account(client, "5100", "expense"),
        "commission_payable": _account(client, "2200", "liability"),
        "fx_gain": _account(client, "4100", "revenue"),
        "fx_loss": _account(client, "5200", "expense"),
    }
    mapped = client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={**accounts, "expected_version": 0},
    )
    assert mapped.status_code == 200
    return accounts


def _seed_event(
    repo: InMemoryFinanceRepository,
    *,
    side: RealizedFxSide,
    amount: str = "12.50",
) -> UUID:
    event_id = uuid4()
    repo.add_realized_fx_event(
        RealizedFxEvent(
            id=event_id,
            tenant_id=TENANT,
            source_type="allocation",
            source_id=uuid4(),
            amount=Decimal(amount),
            currency="USD",
            side=side,
            receipt_id=uuid4(),
            invoice_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
    )
    return event_id


def test_g372_realized_fx_bridge_gain_and_idempotent() -> None:
    client, repo = _client()
    period_id = _period(client)
    accounts = _seed_map(client)
    event_id = _seed_event(repo, side=RealizedFxSide.GAIN)
    key = str(uuid4())
    first = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(event_id),
            "period_id": period_id,
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert first.status_code == 201
    assert first.json()["data"]["source_type"] == "realized_fx"
    again = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(event_id),
            "period_id": period_id,
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert again.status_code == 201
    assert again.json()["data"]["id"] == first.json()["data"]["id"]
    journal = client.get(
        f"/v1/finance/journal-entries/{first.json()['data']['journal_entry_id']}",
        headers=_headers(),
    )
    assert journal.status_code == 200
    lines = journal.json()["data"]["lines"]
    assert {(line["account_id"], line["debit"], line["credit"]) for line in lines} == {
        (accounts["ar_control"], "12.50", "0.00"),
        (accounts["fx_gain"], "0.00", "12.50"),
    }


def test_g372_realized_fx_bridge_loss_and_requires_fx_map() -> None:
    client, repo = _client()
    period_id = _period(client)
    accounts = {
        "ar_control": _account(client, "1100", "asset"),
        "cash": _account(client, "1000", "asset"),
        "revenue": _account(client, "4000", "revenue"),
        "tax_payable": _account(client, "2100", "liability"),
        "commission_expense": _account(client, "5100", "expense"),
        "commission_payable": _account(client, "2200", "liability"),
    }
    assert client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={**accounts, "expected_version": 0},
    ).status_code == 200
    event_id = _seed_event(repo, side=RealizedFxSide.LOSS)
    missing = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(event_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert missing.status_code == 409
    assert (
        missing.json()["detail"]["message"]
        == "gl bridge map fx accounts are incomplete"
    )
    fx_gain = _account(client, "4100", "revenue")
    fx_loss = _account(client, "5200", "expense")
    assert client.put(
        "/v1/finance/gl-bridge-map",
        headers=_headers(),
        json={
            **accounts,
            "fx_gain": fx_gain,
            "fx_loss": fx_loss,
            "expected_version": 1,
        },
    ).status_code == 200
    loss = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(event_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert loss.status_code == 201
    journal = client.get(
        f"/v1/finance/journal-entries/{loss.json()['data']['journal_entry_id']}",
        headers=_headers(),
    )
    assert journal.status_code == 200
    lines = journal.json()["data"]["lines"]
    assert {(line["account_id"], line["debit"], line["credit"]) for line in lines} == {
        (fx_loss, "12.50", "0.00"),
        (accounts["ar_control"], "0.00", "12.50"),
    }


def test_g372_rejects_zero_amount_and_closed_period() -> None:
    client, repo = _client()
    period_id = _period(client)
    _seed_map(client)
    zero_id = _seed_event(repo, side=RealizedFxSide.GAIN, amount="0.00")
    zero = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(zero_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert zero.status_code == 400
    assert zero.json()["detail"]["message"] == "amount must be positive"
    assert client.post(
        f"/v1/finance/gl-periods/{period_id}/close",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    event_id = _seed_event(repo, side=RealizedFxSide.GAIN)
    closed = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(event_id),
            "period_id": period_id,
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert closed.status_code == 409
    assert closed.json()["detail"]["message"] == "gl period is not open"


def test_g372_denies_ungranted_bridge() -> None:
    client, _repo = _client(grant=False)
    response = client.post(
        "/v1/finance/gl-bridges/realized-fx",
        headers=_headers(),
        json={
            "source_id": str(uuid4()),
            "period_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 403


def test_g372_openapi_lists_realized_fx_bridge() -> None:
    client, _repo = _client()
    paths = client.get("/openapi.json").json()["paths"]
    assert "/v1/finance/gl-bridges/realized-fx" in paths
