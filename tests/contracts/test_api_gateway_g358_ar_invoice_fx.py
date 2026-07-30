"""PHX-G358 AR Invoice FX snapshot HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
)
from tests.contracts.test_api_gateway_g352_convert_fx_snapshot import _issued_quote


def test_g358_invoice_recomputes_functional_total_from_so_rate() -> None:
    client = _client()
    quote = _issued_quote(client)
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "functional_currency": "CNY",
            "fx_rate": "7.12345678",
        },
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    confirmed = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert confirmed.status_code == 200
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
    assert {
        key: invoice[key]
        for key in ("currency", "functional_currency", "fx_rate", "functional_total")
    } == {
        "currency": "USD",
        "functional_currency": "CNY",
        "fx_rate": "7.12345678",
        "functional_total": "142.47",
    }
    fetched = client.get(
        f"/v1/crm/ar-invoices/{invoice['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["functional_total"] == "142.47"
