"""PHX-G362 AP write-off and close HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import _client, _headers


def _posted_bill(client):
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"G362-{uuid4().hex[:8]}", "display_name": "Supplier"},
    ).json()["data"]
    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "code": f"BILL-{uuid4().hex[:8]}",
            "currency": "USD",
            "total_amount": "25.00",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-bills/{bill['id']}/post",
        headers=_headers(),
        json={"human_confirm": True},
    ).status_code == 200
    return supplier, bill


def test_g362_write_off_closes_remaining_and_reduces_supplier_balance() -> None:
    client = _client()
    supplier, bill = _posted_bill(client)
    idempotency_key = str(uuid4())
    created = client.post(
        "/v1/purchase/ap-write-offs",
        headers=_headers(),
        json={
            "ap_bill_id": bill["id"],
            "amount": bill["total_amount"],
            "idempotency_key": idempotency_key,
            "human_confirm": True,
            "reason": "approved supplier settlement",
        },
    )
    assert created.status_code == 201
    write_off = created.json()["data"]
    assert write_off["ap_bill_id"] == bill["id"]
    assert write_off["amount"] == bill["total_amount"]
    assert created.json()["audit_id"]

    duplicate = client.post(
        "/v1/purchase/ap-write-offs",
        headers=_headers(),
        json={
            "ap_bill_id": bill["id"],
            "amount": bill["total_amount"],
            "idempotency_key": idempotency_key,
            "human_confirm": True,
            "reason": "approved supplier settlement",
        },
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["data"]["id"] == write_off["id"]

    balance = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/balances",
        headers=_headers(),
    )
    assert balance.status_code == 200
    assert balance.json()["data"]["balances"] == {"USD": "0.00"}

    closed = client.post(
        f"/v1/purchase/ap-bills/{bill['id']}/close",
        headers=_headers(),
        json={"human_confirm": True},
    )
    assert closed.status_code == 200
    assert closed.json()["data"]["status"] == "closed"
    assert closed.json()["data"]["write_off_amount"] == bill["total_amount"]
    assert closed.json()["audit_id"]


def test_g362_rejects_excess_write_off_and_close_with_balance() -> None:
    client = _client()
    _, bill = _posted_bill(client)
    response = client.post(
        "/v1/purchase/ap-write-offs",
        headers=_headers(),
        json={
            "ap_bill_id": bill["id"],
            "amount": "999.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 400
    assert client.post(
        f"/v1/purchase/ap-bills/{bill['id']}/close",
        headers=_headers(),
        json={"human_confirm": True},
    ).status_code == 409


def test_g362_closes_a_fully_paid_bill() -> None:
    client = _client()
    supplier, bill = _posted_bill(client)
    payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "amount": bill["total_amount"],
            "currency": bill["currency"],
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-payments/{payment['id']}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill["id"], "apply_key": str(uuid4())},
    ).status_code == 200
    response = client.post(
        f"/v1/purchase/ap-bills/{bill['id']}/close",
        headers=_headers(),
        json={"human_confirm": True},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "closed"
