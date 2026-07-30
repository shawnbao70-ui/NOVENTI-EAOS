"""PHX-G398 Package surface ↔ Terminal resolve alignment contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.package import PackageStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_OPENAPI = ROOT / "docs" / "api" / "package.openapi.yaml"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(PACKAGE_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g398_package_status_resolve_alignment() -> None:
    response = TestClient(create_app()).get("/v1/packages/status")
    assert response.status_code == 200, response.text
    PackageStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["action_resolve_surface"] is True
    assert data["surface_list_surface"] is True
    assert data["terminal_resolve_aligned"] is True
    assert data["terminal_holds_business_truth"] is False
    assert "action_resolve" in data["supported_surfaces"]
    assert "surface_list" in data["supported_surfaces"]


def test_g398_terminal_paths_align_with_package_surfaces() -> None:
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert 'packageActionResolve: "/v1/packages/actions/resolve"' in js
    assert 'packageSurfaces: "/v1/packages/surfaces"' in js
    assert "async function loadPackageResolveAlignStatus" in js
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    assert 'id="btnAdminPackageResolveAlignStatus"' in html
    assert 'id="packageResolveAlignStatus"' in html


def test_g398_openapi_documents_alignment_flags() -> None:
    props = _load_openapi()["components"]["schemas"]["PackageStatusData"]["properties"]
    assert props["terminal_resolve_aligned"]["const"] is True
    assert props["terminal_holds_business_truth"]["const"] is False
