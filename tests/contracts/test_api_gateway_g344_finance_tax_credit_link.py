"""PHX-G344 Tax Invoice ↔ Credit Note HTTP contracts."""

from __future__ import annotations

from uuid import uuid4

from kernel.permission.models import ScopeLevel
from tests.contracts import test_api_gateway_g312_finance_ar_credit_note as g312
from noventi.finance.service import TAX_CREDIT_LINK_RESOURCE, TAX_INVOICE_RESOURCE


def _client():
    client = g312._client()
    permission = client.app.state.finance._permission
    for resource, actions in (
        (TAX_CREDIT_LINK_RESOURCE, {"create", "read"}),
        (TAX_INVOICE_RESOURCE, {"create", "read", "issue"}),
    ):
        assert permission.grant(
            g312._ctx(),
            principal_subject_id=g312.SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return client


def _issued_tax_invoice(client, invoice_id: str) -> dict:
    created = client.post(
        "/v1/finance/tax-invoices",
        headers=g312._headers(),
        json={
            "invoice_id": invoice_id,
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    tax_invoice = created.json()["data"]
    issued = client.post(
        f"/v1/finance/tax-invoices/{tax_invoice['id']}/issue",
        headers=g312._headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    return issued.json()["data"]


def _draft_credit_note(client, invoice_id: str) -> dict:
    created = client.post(
        "/v1/finance/credit-notes",
        headers=g312._headers(),
        json={
            "invoice_id": invoice_id,
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    return created.json()["data"]


def test_g344_link_round_trip_and_idempotency() -> None:
    client = _client()
    invoice = g312._issued_invoice(client)
    tax_invoice = _issued_tax_invoice(client, invoice["id"])
    credit_note = _draft_credit_note(client, invoice["id"])
    idempotency_key = str(uuid4())

    linked = client.post(
        "/v1/finance/tax-credit-links",
        headers=g312._headers(),
        json={
            "tax_invoice_id": tax_invoice["id"],
            "credit_note_id": credit_note["id"],
            "idempotency_key": idempotency_key,
        },
    )
    assert linked.status_code == 201
    link = linked.json()["data"]
    assert link["status"] == "linked"
    assert link["tax_invoice_id"] == tax_invoice["id"]
    assert link["credit_note_id"] == credit_note["id"]

    repeated = client.post(
        "/v1/finance/tax-credit-links",
        headers=g312._headers(),
        json={
            "tax_invoice_id": tax_invoice["id"],
            "credit_note_id": credit_note["id"],
            "idempotency_key": idempotency_key,
        },
    )
    assert repeated.status_code == 201
    assert repeated.json()["data"]["id"] == link["id"]
    assert (
        client.get(
            f"/v1/finance/tax-credit-links/{link['id']}",
            headers=g312._headers(),
        ).json()["data"]["id"]
        == link["id"]
    )


def test_g344_rejects_unissued_tax_invoice() -> None:
    client = _client()
    invoice = g312._issued_invoice(client)
    drafted_tax_invoice = client.post(
        "/v1/finance/tax-invoices",
        headers=g312._headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    credit_note = _draft_credit_note(client, invoice["id"])

    response = client.post(
        "/v1/finance/tax-credit-links",
        headers=g312._headers(),
        json={
            "tax_invoice_id": drafted_tax_invoice["id"],
            "credit_note_id": credit_note["id"],
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 409


def test_g344_rejects_customer_or_invoice_lineage_mismatch() -> None:
    client = _client()
    first_invoice = g312._issued_invoice(client)
    second_invoice = g312._issued_invoice(client)
    tax_invoice = _issued_tax_invoice(client, first_invoice["id"])
    credit_note = _draft_credit_note(client, second_invoice["id"])

    response = client.post(
        "/v1/finance/tax-credit-links",
        headers=g312._headers(),
        json={
            "tax_invoice_id": tax_invoice["id"],
            "credit_note_id": credit_note["id"],
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 409


def test_g344_openapi_exposes_only_link_endpoints() -> None:
    paths = _client().get("/openapi.json").json()["paths"]
    assert "/v1/finance/tax-credit-links" in paths
    assert "/v1/finance/tax-credit-links/{link_id}" in paths
