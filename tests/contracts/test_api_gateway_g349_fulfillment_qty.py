"""PHX-G349 fulfillment quantity HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g302_crm_delivery_order import (
    _client,
    _confirmed_sales_order,
    _headers,
)


def test_g349_partial_then_remaining_delivery_order_and_over_qty_rejected() -> None:
    client = _client()
    sales_order = _confirmed_sales_order(client)
    line = client.get(
        f"/v1/crm/sales-orders/{sales_order['id']}/lines", headers=_headers()
    ).json()["data"][0]

    partial = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "lines": [{"sales_order_line_id": line["id"], "quantity": "1.000"}],
        },
    )
    assert partial.status_code == 201
    assert partial.json()["data"]["total_amount"] == "10.00"

    over = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "lines": [{"sales_order_line_id": line["id"], "quantity": "3.000"}],
        },
    )
    assert over.status_code == 400

    # The legacy no-lines path remains available and creates all remaining
    # quantity when there is no previous shipment evidence.
    full_client = _client()
    full_so = _confirmed_sales_order(full_client)
    full = full_client.post(
        f"/v1/crm/sales-orders/{full_so['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert full.status_code == 201
    assert full.json()["data"]["total_amount"] == "20.00"
