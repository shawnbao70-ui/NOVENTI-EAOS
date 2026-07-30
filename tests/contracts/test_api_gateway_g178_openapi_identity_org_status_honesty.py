"""PHX-G178 OpenAPI Identity/Organization status-code honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "docs" / "api" / "identity.openapi.yaml"
ORG = ROOT / "docs" / "api" / "organization.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _assert_named(responses: dict, *codes: str) -> None:
    for code in codes:
        assert code in responses
        ref = responses[code]["content"]["application/json"]["schema"]["$ref"]
        assert "GatewayDetailError" in ref

def test_g178_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0197-openapi-identity-org-status-code-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G178_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G178_ARCHITECTURE_GATE.md").is_file()

def test_g178_identity_named_status_codes() -> None:
    spec = _load(IDENTITY)
    assert str(spec["info"]["version"]).startswith("1.0.")
    paths = spec["paths"]
    _assert_named(paths["/identity/subjects"]["post"]["responses"], "400", "409", "503")
    _assert_named(
        paths["/identity/credentials"]["post"]["responses"], "400", "403", "404", "503"
    )
    _assert_named(
        paths["/identity/credentials/{credentialId}/revocation"]["post"]["responses"],
        "400",
        "409",
        "503",
    )
    _assert_named(paths["/identity/sessions"]["post"]["responses"], "400", "409", "503")
    _assert_named(
        paths["/identity/platform-governors"]["post"]["responses"],
        "400",
        "403",
        "409",
        "503",
    )
    _assert_named(
        paths["/identity/platform-governors/{subjectId}/revocation"]["post"]["responses"],
        "400",
        "403",
        "503",
    )
    _assert_named(
        paths["/identity/ai-employees/{aiSubjectId}/profile"]["patch"]["responses"],
        "400",
        "403",
        "503",
    )

def test_g178_organization_named_status_codes() -> None:
    spec = _load(ORG)
    assert str(spec["info"]["version"]).startswith("1.0.")
    paths = spec["paths"]
    _assert_named(
        paths["/platform/tenants"]["post"]["responses"], "400", "403", "409", "503"
    )
    _assert_named(
        paths["/platform/tenants/{tenantId}/suspension"]["post"]["responses"],
        "400",
        "403",
        "404",
        "409",
        "503",
    )
    _assert_named(paths["/enterprises"]["post"]["responses"], "400", "409", "503")
    _assert_named(
        paths["/organization-units"]["put"]["responses"],
        "400",
        "403",
        "404",
        "409",
        "503",
    )
    _assert_named(
        paths["/memberships"]["post"]["responses"], "400", "403", "404", "409", "503"
    )
    _assert_named(
        paths["/memberships/{membershipId}/unit"]["put"]["responses"],
        "400",
        "403",
        "404",
        "409",
        "503",
    )

def test_g178_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g178" in reasons or "g179" in reasons or "g180" in reasons or "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g178_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U051" in ledger
    assert "PHX-G178" in tip
    assert "PHX-G178" in manifest
    assert "PHX-G178" in status or "PHX-G18" in status
