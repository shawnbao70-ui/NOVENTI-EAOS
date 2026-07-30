"""PHX-G346 party balance authority HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g310_finance_ar_receipt import (
    _client,
    _headers,
    _issued_invoice,
)


def test_g346_customer_balance_excludes_unallocated_receipts() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    receipt = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "30.00",
            "currency": invoice["currency"],
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    allocation = client.post(
        f"/v1/finance/receipts/{receipt['id']}/allocations",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "10.00",
            "allocation_key": str(uuid4()),
        },
    )
    assert allocation.status_code == 200

    response = client.get(
        f"/v1/crm/customers/{invoice['customer_id']}/balances",
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["data"] == {
        "customer_id": invoice["customer_id"],
        "balances": {invoice["currency"]: "10.00"},
        "unallocated_receipts": {invoice["currency"]: "20.00"},
        "unallocated_receipts_note": "NOT part of cleared balance",
    }
    assert response.json()["audit_id"]


def test_g346_supplier_balance_sums_only_open_posted_bills() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"G346-{uuid4().hex[:8]}", "display_name": "Supplier"},
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
    payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "amount": "5.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-payments/{payment['id']}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill["id"], "apply_key": str(uuid4())},
    ).status_code == 200

    response = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/balances",
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["data"] == {
        "supplier_id": supplier["id"],
        "balances": {"USD": "20.00"},
    }
    assert response.json()["audit_id"]
