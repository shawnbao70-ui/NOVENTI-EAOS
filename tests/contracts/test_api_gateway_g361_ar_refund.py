"""PHX-G361 AR refund HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from tests.contracts.test_api_gateway_g312_finance_ar_credit_note import (
    _client,
    _headers,
    _issued_invoice,
)


def _issued_credit_note(client, *, amount: str = "10.00") -> dict:
    invoice = _issued_invoice(client)
    created = client.post(
        "/v1/finance/credit-notes",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": amount,
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201, created.json()
    credit_note = created.json()["data"]
    issued = client.post(
        f"/v1/finance/credit-notes/{credit_note['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200, issued.json()
    return issued.json()["data"]


def test_g361_creates_and_posts_refund_against_issued_credit_note() -> None:
    client = _client()
    credit_note = _issued_credit_note(client)
    create_key = str(uuid4())

    created = client.post(
        "/v1/finance/ar-refunds",
        headers=_headers(),
        json={
            "credit_note_id": credit_note["id"],
            "amount": "5.00",
            "currency": credit_note["currency"],
            "idempotency_key": create_key,
        },
    )
    assert created.status_code == 201, created.json()
    refund = created.json()["data"]
    assert {
        key: refund[key]
        for key in ("credit_note_id", "customer_id", "amount", "currency", "status")
    } == {
        "credit_note_id": credit_note["id"],
        "customer_id": credit_note["customer_id"],
        "amount": "5.00",
        "currency": credit_note["currency"],
        "status": "draft",
    }
    replay = client.post(
        "/v1/finance/ar-refunds",
        headers=_headers(),
        json={
            "credit_note_id": credit_note["id"],
            "amount": "5.00",
            "currency": credit_note["currency"],
            "idempotency_key": create_key,
        },
    )
    assert replay.status_code == 201, replay.json()
    assert replay.json()["data"]["id"] == refund["id"]

    posted = client.post(
        f"/v1/finance/ar-refunds/{refund['id']}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert posted.status_code == 200, posted.json()
    assert posted.json()["data"]["status"] == "posted"


def test_g361_rejects_draft_cn_excess_or_currency_mismatch() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    draft = client.post(
        "/v1/finance/credit-notes",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert draft.status_code == 201, draft.json()
    draft_note = draft.json()["data"]
    assert (
        client.post(
            "/v1/finance/ar-refunds",
            headers=_headers(),
            json={
                "credit_note_id": draft_note["id"],
                "amount": "5.00",
                "currency": draft_note["currency"],
                "idempotency_key": str(uuid4()),
            },
        ).status_code
        == 409
    )

    issued = _issued_credit_note(client, amount="10.00")
    for amount, currency in (("10.01", issued["currency"]), ("5.00", "EUR")):
        response = client.post(
            "/v1/finance/ar-refunds",
            headers=_headers(),
            json={
                "credit_note_id": issued["id"],
                "amount": amount,
                "currency": currency,
                "idempotency_key": str(uuid4()),
            },
        )
        assert response.status_code == 400, response.json()


def test_g361_post_requires_human_confirmation() -> None:
    client = _client()
    credit_note = _issued_credit_note(client)
    refund = client.post(
        "/v1/finance/ar-refunds",
        headers=_headers(),
        json={
            "credit_note_id": credit_note["id"],
            "amount": "5.00",
            "currency": credit_note["currency"],
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    response = client.post(
        f"/v1/finance/ar-refunds/{refund['id']}/post",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": False},
    )
    assert response.status_code == 422
