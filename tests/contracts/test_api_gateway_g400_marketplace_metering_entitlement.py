"""PHX-G400 Marketplace metering/entitlement shell contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.marketplace import MarketplaceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"


def test_g400_metering_entitlement_shell_honesty() -> None:
    response = TestClient(create_app()).get("/v1/marketplace/status")
    assert response.status_code == 200, response.text
    MarketplaceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["metering"] == "fail_closed"
    metering = data["metering_product"]
    assert metering["milestone"] == "PHX-G400"
    assert metering["posture"] == "shell_fail_closed"
    assert metering["external_psp"] is False
    assert metering["network_default"] == "off"
    assert metering["commercial_auto_write"] is False
    entitlement = data["entitlement_product"]
    assert entitlement["milestone"] == "PHX-G400"
    assert entitlement["posture"] == "shell_declaration_only"
    assert entitlement["auto_grant"] is False
    assert entitlement["cap_to_grant_invent"] is False
    assert "metering_shell" in data["supported_surfaces"]
    assert "entitlement_shell" in data["supported_surfaces"]


def test_g400_no_metering_write_invent_routes() -> None:
    paths = TestClient(create_app()).get("/openapi.json").json()["paths"]
    for path in paths:
        lowered = path.casefold()
        if not lowered.startswith("/v1/marketplace"):
            continue
        assert "/metering/consume" not in lowered
        assert "/entitlement/grant" not in lowered
        assert "/subscription/charge" not in lowered


def test_g400_openapi_documents_metering_entitlement() -> None:
    spec = yaml.safe_load(MARKET.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert "metering_product" in props
    assert "entitlement_product" in props
    assert (
        spec["components"]["schemas"]["MeteringProduct"]["properties"]["network_default"][
            "const"
        ]
        == "off"
    )
