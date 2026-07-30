"""PHX-G360 tax red-credit HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g316_finance_tax_invoice import (
    _client,
    _headers,
    _issued_invoice,
)


def _issued_tax_invoice(client) -> dict:
    invoice = _issued_invoice(client)
    created = client.post(
        "/v1/finance/tax-invoices",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "20.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201, created.json()
    tax_invoice = created.json()["data"]
    issued = client.post(
        f"/v1/finance/tax-invoices/{tax_invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200, issued.json()
    return issued.json()["data"]


def test_g360_creates_idempotent_draft_red_credit_linked_to_issued_original() -> None:
    client = _client()
    original = _issued_tax_invoice(client)
    idempotency_key = str(uuid4())

    created = client.post(
        f"/v1/finance/tax-invoices/{original['id']}/red-credits",
        headers=_headers(),
        json={"idempotency_key": idempotency_key, "human_confirm": True},
    )

    assert created.status_code == 201, created.json()
    red_credit = created.json()["data"]
    assert {
        key: red_credit[key]
        for key in (
            "status",
            "amount",
            "original_tax_invoice_id",
            "is_red_credit",
        )
    } == {
        "status": "draft",
        "amount": "20.00",
        "original_tax_invoice_id": original["id"],
        "is_red_credit": True,
    }
    replay = client.post(
        f"/v1/finance/tax-invoices/{original['id']}/red-credits",
        headers=_headers(),
        json={"idempotency_key": idempotency_key, "human_confirm": True},
    )
    assert replay.status_code == 201
    assert replay.json()["data"]["id"] == red_credit["id"]


def test_g360_rejects_draft_or_voided_original_and_preserves_void() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    draft = client.post(
        "/v1/finance/tax-invoices",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "20.00",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    draft_credit = client.post(
        f"/v1/finance/tax-invoices/{draft['id']}/red-credits",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert draft_credit.status_code == 409

    original = _issued_tax_invoice(client)
    voided = client.post(
        f"/v1/finance/tax-invoices/{original['id']}/void",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
            "reason": "regression coverage",
        },
    )
    assert voided.status_code == 200, voided.json()
    assert voided.json()["data"]["status"] == "voided"
    voided_credit = client.post(
        f"/v1/finance/tax-invoices/{original['id']}/red-credits",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert voided_credit.status_code == 409
