"""PHX-G370 controlled-reship HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from tests.contracts.test_api_gateway_g311_inventory_do_ship import (
    _client,
    _headers,
    _released_delivery_order,
)


def _stock(client, lines: list[dict]) -> None:
    for line in lines:
        assert (
            client.post(
                "/v1/inventory/stock/adjust",
                headers=_headers(),
                json={
                    "sales_order_line_id": line["id"],
                    "quantity_delta": line["quantity"],
                    "idempotency_key": str(uuid4()),
                },
            ).status_code
            == 200
        )


def test_g370_ship_unship_reship_with_new_key_succeeds_and_old_key_conflicts() -> None:
    client = _client()
    delivery_order, lines = _released_delivery_order(client)
    _stock(client, lines)
    ship_path = f"/v1/inventory/delivery-orders/{delivery_order['id']}/ship"
    unship_path = f"/v1/inventory/delivery-orders/{delivery_order['id']}/unship"
    old_key = str(uuid4())

    first_ship = client.post(
        ship_path,
        headers=_headers(),
        json={"idempotency_key": old_key, "human_confirm": True},
    )
    assert first_ship.status_code == 200
    assert first_ship.json()["data"]["status"] == "shipped"
    first_posting_id = first_ship.json()["data"]["id"]

    for line in lines:
        stock = client.get(
            f"/v1/inventory/stock/{line['id']}", headers=_headers()
        ).json()["data"]
        assert Decimal(stock["on_hand"]) == Decimal("0")

    unship = client.post(
        unship_path,
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert unship.status_code == 200
    assert unship.json()["data"]["status"] == "unshipped"
    for line in lines:
        stock = client.get(
            f"/v1/inventory/stock/{line['id']}", headers=_headers()
        ).json()["data"]
        assert Decimal(stock["on_hand"]) == Decimal(line["quantity"])

    reuse_old = client.post(
        ship_path,
        headers=_headers(),
        json={"idempotency_key": old_key, "human_confirm": True},
    )
    assert reuse_old.status_code == 409

    new_key = str(uuid4())
    reship = client.post(
        ship_path,
        headers=_headers(),
        json={"idempotency_key": new_key, "human_confirm": True},
    )
    assert reship.status_code == 200
    assert reship.json()["data"]["status"] == "shipped"
    assert reship.json()["data"]["id"] != first_posting_id
    assert (
        client.post(
            ship_path,
            headers=_headers(),
            json={"idempotency_key": new_key, "human_confirm": True},
        ).status_code
        == 200
    )

    for line in lines:
        stock = client.get(
            f"/v1/inventory/stock/{line['id']}", headers=_headers()
        ).json()["data"]
        assert Decimal(stock["on_hand"]) == Decimal("0")

    delivery_order_after = client.get(
        f"/v1/crm/delivery-orders/{delivery_order['id']}", headers=_headers()
    ).json()["data"]
    assert delivery_order_after["status"] == "shipped"


def test_g370_active_ship_still_blocks_different_key() -> None:
    client = _client()
    delivery_order, lines = _released_delivery_order(client)
    _stock(client, lines)
    ship_path = f"/v1/inventory/delivery-orders/{delivery_order['id']}/ship"
    key = str(uuid4())
    assert (
        client.post(
            ship_path,
            headers=_headers(),
            json={"idempotency_key": key, "human_confirm": True},
        ).status_code
        == 200
    )
    assert (
        client.post(
            ship_path,
            headers=_headers(),
            json={"idempotency_key": key, "human_confirm": True},
        ).status_code
        == 200
    )
    assert (
        client.post(
            ship_path,
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 409
    )
