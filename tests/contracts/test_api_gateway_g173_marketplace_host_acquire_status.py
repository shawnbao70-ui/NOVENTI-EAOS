"""PHX-G173 marketplace host-acquire status posture contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.host_acquire import HOST_ACQUIRE_ALLOWLIST
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / "docs" / "api" / "marketplace.openapi.yaml"

def test_g173_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0192-marketplace-host-acquire-status-posture.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G173_ACCEPTANCE.md").is_file()

def test_g173_status_and_openapi() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/marketplace/status")
    assert response.status_code == 200
    product = response.json()["data"]["host_acquire_product"]
    assert product["milestone"] == "PHX-G173"
    assert product["arbitrary_scripts"] is False
    assert product["package_install"] is False
    assert product["external_psp"] is False
    assert product["allowlist"] == sorted(HOST_ACQUIRE_ALLOWLIST)
    assert "host_acquire_allowlisted" in response.json()["data"]["supported_surfaces"]

    spec = yaml.safe_load(MARKETPLACE.read_text(encoding="utf-8"))
    assert str(spec["info"]["version"]).startswith("1.2.")
    assert "HostAcquireProduct" in spec["components"]["schemas"]
    assert (
        spec["components"]["schemas"]["HostAcquireProduct"]["properties"]["milestone"][
            "const"
        ]
        == "PHX-G173"
    )

def test_g173_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "DAL-U046" in ledger
    assert "PHX-G173" in tip
    assert "PHX-G173" in manifest
