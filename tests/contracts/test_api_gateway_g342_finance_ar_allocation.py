"""PHX-G342 AR receipt allocation HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
    _issued_invoice,
)


def test_g342_partial_and_multi_allocation_round_trip() -> None:
    client = _client()
    first_invoice = _issued_invoice(client)
    receipt = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": first_invoice["customer_id"],
            "amount": "20.00",
            "currency": first_invoice["currency"],
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    first = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": first_invoice["id"],
            "amount": "10.00",
            "allocation_key": str(uuid4()),
        },
    )
    assert first.status_code == 200
    assert first.json()["data"]["status"] == "draft"
    assert first.json()["data"]["unallocated_amount"] == "10.00"
    second = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": first_invoice["id"],
            "amount": "10.00",
            "allocation_key": str(uuid4()),
        },
    )
    assert second.status_code == 200
    assert second.json()["data"]["status"] == "applied"
    allocations = client.get(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
    )
    assert allocations.status_code == 200
    assert len(allocations.json()["data"]) == 2


def test_g342_rejects_over_allocation_and_exposes_openapi() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    receipt = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "1.00",
            "currency": invoice["currency"],
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    response = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "1.01",
            "allocation_key": str(uuid4()),
        },
    )
    assert response.status_code == 400
    assert "/v1/finance/receipts/{receipt_id}/allocations" in client.get(
        "/openapi.json"
    ).json()["paths"]
