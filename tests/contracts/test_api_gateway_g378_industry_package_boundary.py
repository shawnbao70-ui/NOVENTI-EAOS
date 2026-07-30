"""PHX-G378 Industry Package boundary HTTP contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.industry_package import IndustryPackageStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
PLATFORM_OPENAPI = ROOT / "docs" / "api" / "platform.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(PLATFORM_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g378_industry_package_status_honest_flags() -> None:
    response = _client().get("/v1/platform/industry-package/status")
    assert response.status_code == 200, response.text
    body = response.json()
    IndustryPackageStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["industry_package_runtime"] is False
    assert data["host_install"] is False
    assert data["declaration_only"] is True
    assert data["package_type_industry_supported_in_manifest"] is True
    assert data["execution_authority"] == "none"


def test_g378_no_host_install_invent_routes() -> None:
    client = _client()
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    assert "/v1/platform/industry-package/status" in paths
    assert "get" in paths["/v1/platform/industry-package/status"]
    for path in paths:
        if "industry-package" in path and path != "/v1/platform/industry-package/status":
            raise AssertionError(f"unexpected industry-package invent path: {path}")
        lowered = path.casefold()
        assert "host-install" not in lowered
        assert "host_install" not in lowered
        assert "/industry-package/install" not in lowered


def test_g378_platform_openapi_documents_status() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    path = spec["paths"]["/platform/industry-package/status"]["get"]
    assert path["operationId"] == "getIndustryPackageStatus"
    assert "200" in path["responses"]
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("IndustryPackageStatusEnvelope")
    data = spec["components"]["schemas"]["IndustryPackageStatusData"]
    props = data["properties"]
    assert props["industry_package_runtime"]["const"] is False
    assert props["host_install"]["const"] is False
    assert props["declaration_only"]["const"] is True
    assert props["package_type_industry_supported_in_manifest"]["const"] is True
    assert props["execution_authority"]["const"] == "none"
    required = set(data["required"])
    assert {
        "industry_package_runtime",
        "host_install",
        "declaration_only",
        "package_type_industry_supported_in_manifest",
        "execution_authority",
    } <= required
