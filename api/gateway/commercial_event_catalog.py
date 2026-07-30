"""Commercial domain-event catalog read projection (PHX-G386)."""

from __future__ import annotations

from typing import Any


def commercial_event_catalog_projection() -> dict[str, Any]:
    """Read-only projection of EVT-COMMERCIAL-001 wired events."""

    return {
        "writable": False,
        "catalog_id": "EVT-COMMERCIAL-001",
        "milestone": "PHX-G386",
        "events": [
            {
                "event_name": "crm.sales_order.confirmed",
                "producer": "crm.package",
                "trigger": "confirm_sales_order",
            },
            {
                "event_name": "inventory.delivery_order.shipped",
                "producer": "inventory.package",
                "trigger": "ship_delivery_order",
            },
            {
                "event_name": "crm.quote.converted",
                "producer": "crm.package",
                "trigger": "convert_quote",
            },
            {
                "event_name": "crm.delivery_order.released",
                "producer": "crm.package",
                "trigger": "release_delivery_order",
            },
        ],
    }
