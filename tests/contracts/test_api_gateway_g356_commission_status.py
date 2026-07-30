"""PHX-G356 Commission status transition HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from kernel.shared.errors import ErrorCode
from tests.contracts.test_api_gateway_g314_finance_commission_ledger import (
    _client,
    _ctx,
    _headers,
)
from tests.contracts.test_finance_z2_commission_ledger import (
    _issued_invoice,
    _services,
)


def _accrued_commission():
    client, crm = _client()
    invoice = _issued_invoice(crm, _ctx())
    created = client.post(
        "/v1/finance/commissions",
        headers=_headers(),
        json={
            "invoice_id": str(invoice.id),
            "beneficiary_subject_id": _headers()["X-EAOS-Subject-Id"],
            "amount": "3.00",
            "currency": invoice.currency,
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    return client, created.json()["data"]


def test_g356_commission_transitions_only_follow_accrued_payable_paid() -> None:
    client, commission = _accrued_commission()

    paid_too_soon = client.post(
        f"/v1/finance/commissions/{commission['id']}/paid", headers=_headers()
    )
    assert paid_too_soon.status_code == 409

    payable = client.post(
        f"/v1/finance/commissions/{commission['id']}/payable", headers=_headers()
    )
    assert payable.status_code == 200
    assert payable.json()["data"]["status"] == "payable"

    cannot_repeat = client.post(
        f"/v1/finance/commissions/{commission['id']}/payable", headers=_headers()
    )
    assert cannot_repeat.status_code == 409

    paid = client.post(
        f"/v1/finance/commissions/{commission['id']}/paid", headers=_headers()
    )
    assert paid.status_code == 200
    assert paid.json()["data"]["status"] == "paid"

    fetched = client.get(
        f"/v1/finance/commissions/{commission['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["status"] == "paid"


def test_g356_openapi_exposes_only_explicit_status_commands() -> None:
    client, _ = _client()
    paths = client.get("/openapi.json").json()["paths"]
    assert "/v1/finance/commissions/{commission_id}/payable" in paths
    assert "/v1/finance/commissions/{commission_id}/paid" in paths
    surface = str(
        paths["/v1/finance/commissions/{commission_id}/payable"]
    ).casefold()
    surface += str(
        paths["/v1/finance/commissions/{commission_id}/paid"]
    ).casefold()
    for forbidden in ("payout", "payroll", "psp", "clawback", "brain", "twin"):
        assert forbidden not in surface


def test_g356_transition_requires_update_permission_and_audits_denial() -> None:
    ctx = _ctx()
    crm, finance, audit = _services(ctx)
    invoice = _issued_invoice(crm, ctx)
    accrued = finance.accrue_commission(
        ctx,
        invoice_id=invoice.id,
        beneficiary_subject_id=ctx.subject_id,
        amount=Decimal("3.00"),
        currency=invoice.currency,
        idempotency_key=uuid4(),
    )
    assert accrued.data is not None

    denied = finance.mark_commission_payable(
        ctx, commission_id=accrued.data.id
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Finance.Commission.MarkPayable")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
