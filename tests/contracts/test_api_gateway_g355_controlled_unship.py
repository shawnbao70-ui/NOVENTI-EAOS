"""PHX-G355 controlled-unship HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from tests.contracts.test_api_gateway_g311_inventory_do_ship import (
    _client,
    _headers,
    _released_delivery_order,
)


def _stock_and_ship(client, delivery_order: dict, lines: list[dict]) -> None:
    for line in lines:
        assert client.post(
            "/v1/inventory/stock/adjust",
            headers=_headers(),
            json={
                "sales_order_line_id": line["id"],
                "quantity_delta": line["quantity"],
                "idempotency_key": str(uuid4()),
            },
        ).status_code == 200
    assert client.post(
        f"/v1/inventory/delivery-orders/{delivery_order['id']}/ship",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200


def test_g355_ship_unship_restores_stock_and_remaining_quantity() -> None:
    client = _client()
    delivery_order, lines = _released_delivery_order(client)
    _stock_and_ship(client, delivery_order, lines)

    unship = client.post(
        f"/v1/inventory/delivery-orders/{delivery_order['id']}/unship",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert unship.status_code == 200
    assert unship.json()["data"]["status"] == "unshipped"
    assert unship.json()["data"]["unshipped_at"] is not None
    for line in lines:
        stock = client.get(
            f"/v1/inventory/stock/{line['id']}", headers=_headers()
        ).json()["data"]
        assert Decimal(stock["on_hand"]) == Decimal(line["quantity"])
    delivery_order_after = client.get(
        f"/v1/crm/delivery-orders/{delivery_order['id']}", headers=_headers()
    ).json()["data"]
    assert delivery_order_after["status"] == "released"
    sales_order = client.get(
        f"/v1/crm/sales-orders/{delivery_order_after['sales_order_id']}",
        headers=_headers(),
    ).json()["data"]
    assert Decimal(sales_order["shipped_quantity"]) == Decimal("0")
    assert Decimal(sales_order["remaining_quantity"]) == sum(
        (Decimal(line["quantity"]) for line in lines), start=Decimal("0")
    )


def test_g355_unship_is_idempotent_and_rejects_other_key() -> None:
    client = _client()
    delivery_order, lines = _released_delivery_order(client)
    _stock_and_ship(client, delivery_order, lines)
    key = str(uuid4())
    path = f"/v1/inventory/delivery-orders/{delivery_order['id']}/unship"
    body = {"idempotency_key": key, "human_confirm": True}
    assert client.post(path, headers=_headers(), json=body).status_code == 200
    assert client.post(path, headers=_headers(), json=body).status_code == 200
    assert client.post(
        path,
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 409


def test_g355_rejects_unship_of_draft_and_does_not_create_rma() -> None:
    client = _client()
    delivery_order, _ = _released_delivery_order(client, release=False)
    response = client.post(
        f"/v1/inventory/delivery-orders/{delivery_order['id']}/unship",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 409
    assert "return_authorization_id" not in response.json()
