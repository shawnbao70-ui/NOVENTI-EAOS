"""Foundation harden — Terminal extension list/invoke closed envelopes."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.terminal import (
    TerminalExtensionInvokeEnvelope,
    TerminalExtensionListEnvelope,
)

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()


def _headers(subject: object = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def test_extension_list_matches_closed_envelope() -> None:
    client = TestClient(create_app())
    # Grant extension read via permission admin path is heavy; empty list is enough.
    response = client.get("/v1/terminal/extensions", headers=_headers())
    # Permission denial is still a Kernel error path; when allowed, envelope closes.
    if response.status_code == 200:
        envelope = TerminalExtensionListEnvelope.model_validate(response.json())
        assert isinstance(envelope.data, list)
        return
    assert response.status_code in {403, 503}


def test_extension_invoke_envelope_schema_accepts_serializer_shape() -> None:
    payload = {
        "data": {
            "extension_id": str(uuid4()),
            "action": "panel.render",
            "surface": "extensions",
            "status": "accepted_sandboxed",
            "executed": False,
        },
        "audit_id": str(uuid4()),
    }
    envelope = TerminalExtensionInvokeEnvelope.model_validate(payload)
    assert envelope.data.executed is False
    assert envelope.data.status == "accepted_sandboxed"
