"""Foundation harden — domain `/status` closed response envelopes."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.event import EventStatusEnvelope
from api.gateway.schemas.finance import FinanceStatusEnvelope
from api.gateway.schemas.foundation_status import (
    AIStatusEnvelope,
    BrainStatusEnvelope,
    FoundationStatusEnvelope,
    TwinStatusEnvelope,
    WorkflowStatusEnvelope,
)
from api.gateway.schemas.knowledge import KnowledgeStatusEnvelope
from api.gateway.schemas.marketplace import MarketplaceStatusEnvelope
from api.gateway.schemas.package import PackageStatusEnvelope
from api.gateway.schemas.terminal import TerminalStatusEnvelope


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.parametrize(
    ("path", "model"),
    [
        ("/v1/packages/status", PackageStatusEnvelope),
        ("/v1/terminal/status", TerminalStatusEnvelope),
        ("/v1/finance/status", FinanceStatusEnvelope),
        ("/v1/identity/status", FoundationStatusEnvelope),
        ("/v1/permission/status", FoundationStatusEnvelope),
        ("/v1/events/status", EventStatusEnvelope),
        ("/v1/knowledge/status", KnowledgeStatusEnvelope),
        ("/v1/organization/status", FoundationStatusEnvelope),
        ("/v1/workflow/status", WorkflowStatusEnvelope),
        ("/v1/ai/status", AIStatusEnvelope),
        ("/v1/brain/status", BrainStatusEnvelope),
        ("/v1/twin/status", TwinStatusEnvelope),
        ("/v1/marketplace/status", MarketplaceStatusEnvelope),
    ],
)
def test_domain_status_matches_closed_envelope(
    client: TestClient,
    path: str,
    model: type,
) -> None:
    response = client.get(path)
    assert response.status_code == 200
    envelope = model.model_validate(response.json())
    assert envelope.data.writable is False
    assert envelope.data.supported_surfaces
