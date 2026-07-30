"""PHX-G350 FX cash-event HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
    _issued_invoice,
)


def test_g350_receipt_defaults_and_persists_cross_currency_fx() -> None:
    client = _client()
    invoice = _issued_invoice(client)

    same_currency = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "10.00",
            "currency": invoice["currency"],
            "idempotency_key": str(uuid4()),
        },
    )
    assert same_currency.status_code == 201
    assert {
        key: same_currency.json()["data"][key]
        for key in ("functional_currency", "fx_rate", "functional_amount")
    } == {
        "functional_currency": invoice["currency"],
        "fx_rate": "1.00000000",
        "functional_amount": "10.00",
    }

    cross_currency = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "10.00",
            "currency": "USD",
            "functional_currency": "CNY",
            "fx_rate": "7.12345678",
            "functional_amount": "71.23",
            "idempotency_key": str(uuid4()),
        },
    )
    assert cross_currency.status_code == 201
    assert cross_currency.json()["data"]["functional_amount"] == "71.23"


def test_g350_rejects_missing_or_inconsistent_cross_currency_fx() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    base_payload = {
        "customer_id": invoice["customer_id"],
        "amount": "10.00",
        "currency": "USD",
        "functional_currency": "CNY",
    }
    assert client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json=base_payload | {"idempotency_key": str(uuid4())},
    ).status_code == 400
    assert client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json=base_payload
        | {
            "fx_rate": "7.12",
            "functional_amount": "71.19",
            "idempotency_key": str(uuid4()),
        },
    ).status_code == 400


def test_g350_ap_payment_persists_fx_and_rejects_missing_rate() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"FX-{uuid4().hex[:8]}", "display_name": "FX supplier"},
    ).json()["data"]
    response = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "amount": "10.00",
            "currency": "USD",
            "functional_currency": "CNY",
            "fx_rate": "7.12",
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["functional_amount"] == "71.20"
    assert client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "amount": "10.00",
            "currency": "USD",
            "functional_currency": "CNY",
            "idempotency_key": str(uuid4()),
        },
    ).status_code == 400
