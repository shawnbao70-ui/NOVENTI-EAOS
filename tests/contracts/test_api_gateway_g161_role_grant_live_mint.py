"""PHX-G161 Role→grant env-gated live mint contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.role_grant_auto_write import (
    GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED,
    GATEWAY_ROLE_GRANT_MAP_REQUIRED,
    ROLE_GRANT_AUTO_WRITE_STUB_ROUTES,
)
from api.gateway.role_grant_product import role_grant_product_posture
from eaos_sdk import __version__ as sdk_version
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    reset_permission_role_grant_map,
)
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0179-role-grant-live-mint.md"
GATE = ROOT / "docs" / "project" / "PHX-G161_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G161_ACCEPTANCE.md"
PERMISSION_OPENAPI = ROOT / "docs" / "api" / "permission.openapi.yaml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"

ADMIN = uuid4()
TENANT = uuid4()
PRINCIPAL = uuid4()
CORR = str(uuid4())

class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True

@pytest.fixture(autouse=True)
def _reset_env_and_map() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    previous = os.environ.get("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED")
    previous_map = os.environ.get("EAOS_PERMISSION_ROLE_GRANT_MAP")
    os.environ.pop("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED", None)
    os.environ.pop("EAOS_PERMISSION_ROLE_GRANT_MAP", None)
    reset_permission_role_grant_map()
    yield
    reset_permission_role_grant_map()
    if previous is None:
        os.environ.pop("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED", None)
    else:
        os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = previous
    if previous_map is None:
        os.environ.pop("EAOS_PERMISSION_ROLE_GRANT_MAP", None)
    else:
        os.environ["EAOS_PERMISSION_ROLE_GRANT_MAP"] = previous_map

def _headers(subject_id: UUID = ADMIN) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }

def _permission_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(PERMISSION_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def _client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))

def test_g161_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G161" in adr
    assert "EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED" in adr
    assert "DAL-G006" in adr
    gate = GATE.read_text(encoding="utf-8")
    assert "DAL-G006" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "Cap" in acceptance or "cap" in acceptance.casefold()

def test_g161_default_posture_and_503() -> None:
    posture = role_grant_product_posture()
    assert posture["milestone"] == "PHX-G161"
    assert posture["auto_grant_from_role_enabled"] is False
    assert posture["role_grant_live_mint_ready"] is False
    assert posture["auto_write_routes"] == list(ROLE_GRANT_AUTO_WRITE_STUB_ROUTES)

    client = _client()
    response = client.post("/v1/permission/role-grants", headers=_headers())
    assert response.status_code == 503
    detail = response.json().get("detail") or {}
    assert detail.get("code") == GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED
    assert detail.get("grant_minted") is False
    assert detail.get("cap_is_grant") is False
    assert detail.get("title_is_permission") is False
    assert detail.get("milestone") == "PHX-G161"

def test_g161_enabled_without_map_returns_map_required() -> None:
    os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = "true"
    reset_permission_role_grant_map()
    posture = role_grant_product_posture()
    assert posture["auto_grant_from_role_enabled"] is True
    assert posture["role_grant_map_configured"] is False
    assert posture["role_grant_live_mint_ready"] is False

    client = _client()
    response = client.post(
        "/v1/permission/role-grants",
        headers=_headers(),
        json={"principal_id": str(PRINCIPAL), "roles": ["operator"]},
    )
    assert response.status_code == 503
    detail = response.json().get("detail") or {}
    assert detail.get("code") == GATEWAY_ROLE_GRANT_MAP_REQUIRED
    assert detail.get("grant_minted") is False

def test_g161_live_mint_with_map() -> None:
    os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = "true"
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read"), ("document", "list")})}
    )
    posture = role_grant_product_posture()
    assert posture["role_grant_live_mint_ready"] is True

    client = _client()
    response = client.post(
        "/v1/permission/role-grants",
        headers=_headers(),
        json={"principal_id": str(PRINCIPAL), "roles": ["operator"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["grant_minted"] is True
    assert body["cap_is_grant"] is False
    assert body["title_is_permission"] is False
    assert body["milestone"] == "PHX-G161"
    assert body["grant_count"] >= 1
    assert body["grants"]
    assert body["principal_id"] == str(PRINCIPAL)
    assert "operator" in body["roles_applied"]

def test_g161_enabled_missing_body_is_422() -> None:
    os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = "true"
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    client = _client()
    missing = client.post("/v1/permission/role-grants", headers=_headers())
    assert missing.status_code == 422
    empty = client.post(
        "/v1/permission/role-grants",
        headers=_headers(),
        json={},
    )
    assert empty.status_code == 422

def test_g161_openapi_1_1_3_documents_mint() -> None:
    spec = _permission_spec()
    assert str(spec["info"]["version"]).startswith("1.1.")
    assert "/permission/role-grants" in spec["paths"]
    path = spec["paths"]["/permission/role-grants"]["post"]
    assert "200" in path["responses"]
    assert "503" in path["responses"]
    schemas = spec["components"]["schemas"]
    assert "RoleGrantAutoWriteMintResponse" in schemas
    assert "RoleGrantAutoWriteRequest" in schemas
    product = schemas["RoleGrantProductPosture"]["properties"]
    assert "const" not in product["auto_grant_from_role_enabled"]
    assert "role_grant_live_mint_ready" in product
    body = PERMISSION_OPENAPI.read_text(encoding="utf-8")
    assert "DAL-G006" in body
    assert "PHX-G161" in body

def test_g161_package_dal_terminal_manifest() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-G006" in ledger
    assert "DAL-U032" in ledger
    assert "PHX-G161" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "G161" in html or "live mint" in html.casefold()
    assert "role_grant_live_mint_ready" in js or "EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED" in js
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in manifest["milestones"]}
    assert by_id["PHX-G161"]["status"] == "fully_accepted"

def test_g161_no_payment_brain_twin_cap_grant_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "cap" in folded and "grant" in folded
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded
    assert (
        "never" in folded
        or "永不" in combined
        or "≠ Cap→grant" in combined
        or "not invent" in folded
        or "不开口" in combined
    )
