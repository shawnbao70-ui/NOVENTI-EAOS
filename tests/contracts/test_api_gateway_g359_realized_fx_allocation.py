"""PHX-G359 realized FX allocation HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
)
from tests.contracts.test_api_gateway_g352_convert_fx_snapshot import _issued_quote


def _issued_fx_invoice(client) -> dict:
    quote = _issued_quote(client)
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "functional_currency": "CNY",
            "fx_rate": "7.00000000",
        },
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    delivery_order = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/release",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    response = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/ar-invoice",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert response.status_code == 201
    invoice = response.json()["data"]
    issued = client.post(
        f"/v1/crm/ar-invoices/{invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    return issued.json()["data"]


def test_g359_records_gain_for_cross_currency_allocation() -> None:
    client = _client()
    invoice = _issued_fx_invoice(client)
    receipt = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "20.00",
            "currency": "EUR",
            "functional_currency": "CNY",
            "fx_rate": "8.00000000",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]

    allocated = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "20.00",
            "allocation_key": str(uuid4()),
        },
    )

    assert allocated.status_code == 200, allocated.json()
    allocations = client.get(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
    )
    assert allocations.status_code == 200
    assert {
        key: allocations.json()["data"][0][key]
        for key in ("realized_fx_amount", "realized_fx_side")
    } == {"realized_fx_amount": "20.00", "realized_fx_side": "gain"}


def test_g359_rejects_cross_currency_allocation_without_common_functional_currency() -> None:
    client = _client()
    invoice = _issued_fx_invoice(client)
    receipt = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "20.00",
            "currency": "EUR",
            "functional_currency": "USD",
            "fx_rate": "1.00000000",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]

    response = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "20.00",
            "allocation_key": str(uuid4()),
        },
    )

    assert response.status_code == 409
