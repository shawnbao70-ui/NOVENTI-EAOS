"""PHX-G352 Convert FX snapshot HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
)


def _issued_quote(client):
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"G352-{uuid4().hex[:8]}", "display_name": "G352 customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G352 opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "G352 requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"], "currency": "USD"},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "FX line", "quantity": "2", "unit_price": "10.00"},
    ).status_code == 201
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    return quote


def test_g352_convert_snapshots_cross_currency_fx_on_conversion_and_so() -> None:
    client = _client()
    quote = _issued_quote(client)
    conversion_response = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "functional_currency": "CNY",
            "fx_rate": "7.12345678",
        },
    )
    assert conversion_response.status_code == 201
    conversion = conversion_response.json()["data"]
    assert {
        key: conversion[key]
        for key in ("currency", "functional_currency", "fx_rate", "functional_total")
    } == {
        "currency": "USD",
        "functional_currency": "CNY",
        "fx_rate": "7.12345678",
        "functional_total": "142.47",
    }

    sales_order_response = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert sales_order_response.status_code == 201
    sales_order = sales_order_response.json()["data"]
    assert {
        key: sales_order[key]
        for key in ("functional_currency", "fx_rate", "functional_total")
    } == {
        "functional_currency": "CNY",
        "fx_rate": "7.12345678",
        "functional_total": "142.47",
    }


def test_g352_rejects_cross_currency_convert_without_fx_rate() -> None:
    client = _client()
    quote = _issued_quote(client)
    response = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "functional_currency": "CNY",
        },
    )
    assert response.status_code == 400
