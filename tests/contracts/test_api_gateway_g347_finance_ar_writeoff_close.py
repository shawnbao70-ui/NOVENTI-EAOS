"""PHX-G347 AR write-off and close HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
    _issued_invoice,
)


def test_g347_write_off_closes_remaining_and_reduces_party_balance() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    created = client.post(
        "/v1/finance/ar-write-offs",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": invoice["total_amount"],
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
            "reason": "approved bad debt",
        },
    )
    assert created.status_code == 201
    write_off = created.json()["data"]
    assert write_off["ar_invoice_id"] == invoice["id"]
    assert write_off["amount"] == invoice["total_amount"]
    assert created.json()["audit_id"]

    balance = client.get(
        f"/v1/crm/customers/{invoice['customer_id']}/balances",
        headers=_headers(),
    )
    assert balance.status_code == 200
    assert balance.json()["data"]["balances"] == {invoice["currency"]: "0.00"}

    closed = client.post(
        f"/v1/finance/ar-invoices/{invoice['id']}/close",
        headers=_headers(),
        json={"human_confirm": True},
    )
    assert closed.status_code == 200
    assert closed.json()["data"]["status"] == "closed"
    assert closed.json()["audit_id"]


def test_g347_rejects_write_off_larger_than_remaining_and_close_with_balance() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    response = client.post(
        "/v1/finance/ar-write-offs",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "999.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 400
    assert client.post(
        f"/v1/finance/ar-invoices/{invoice['id']}/close",
        headers=_headers(),
        json={"human_confirm": True},
    ).status_code == 409

