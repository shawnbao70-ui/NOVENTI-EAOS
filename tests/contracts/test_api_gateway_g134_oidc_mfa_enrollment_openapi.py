"""PHX-G134 OIDC MFA Enrollment OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"


def _spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_auth_openapi_documents_mfa_enrollment_redirect() -> None:
    spec = _spec()
    assert str(spec["info"]["version"]).startswith("1.3.")
    operation = spec["paths"]["/auth/oidc/mfa-enrollment"]["get"]
    assert operation["operationId"] == "redirectOidcMfaEnrollment"
    assert operation.get("security") == []
    assert "302" in operation["responses"]
    assert "503" in operation["responses"]
    assert "Location" in operation["responses"]["302"]["headers"]
    description = (operation.get("description") or "") + (spec["info"].get("description") or "")
    assert "WebAuthn" in description


def test_mfa_enrollment_openapi_is_not_a_registration_product_surface() -> None:
    spec = _spec()
    paths = set(spec["paths"])
    assert "/auth/oidc/mfa-enrollment" in paths
    assert "/auth/webauthn/register" not in paths
    assert "/auth/mfa/register" not in paths
    body = AUTH_OPENAPI.read_text(encoding="utf-8")
    assert "not a WebAuthn registration product page" in body
