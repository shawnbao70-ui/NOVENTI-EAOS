"""Foundation harden — OpenAPI 422 documents FastAPI HTTPValidationError envelope."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"


def _load(name: str) -> dict:
    return yaml.safe_load((API / name).read_text(encoding="utf-8"))


def _assert_422(responses: dict) -> None:
    assert "422" in responses
    ref = responses["422"]["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("/HTTPValidationError"), ref


def test_http_validation_error_schema_present_on_body_specs() -> None:
    for path in sorted(API.glob("*.openapi.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        has_body = any(
            isinstance(op, dict) and "requestBody" in op
            for methods in (doc.get("paths") or {}).values()
            for op in (methods or {}).values()
        )
        if not has_body:
            continue
        schemas = (doc.get("components") or {}).get("schemas") or {}
        assert "HTTPValidationError" in schemas, path.name
        assert "ValidationErrorItem" in schemas, path.name
        assert schemas["HTTPValidationError"].get("additionalProperties") is False


def test_request_body_ops_document_422_http_validation_error() -> None:
    missing: list[str] = []
    wrong: list[str] = []
    for path in sorted(API.glob("*.openapi.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        for api_path, methods in (doc.get("paths") or {}).items():
            for method, op in (methods or {}).items():
                if not isinstance(op, dict) or "requestBody" not in op:
                    continue
                responses = op.get("responses") or {}
                if "422" not in responses:
                    missing.append(f"{path.name} {method.upper()} {api_path}")
                    continue
                try:
                    ref = responses["422"]["content"]["application/json"]["schema"][
                        "$ref"
                    ]
                except (KeyError, TypeError):
                    wrong.append(f"{path.name} {method.upper()} {api_path}")
                    continue
                if not ref.endswith("/HTTPValidationError"):
                    wrong.append(f"{path.name} {method.upper()} {api_path} -> {ref}")
    assert not missing, missing[:20]
    assert not wrong, wrong[:20]


def test_known_closed_body_surfaces_document_422() -> None:
    cases = [
        ("terminal.openapi.yaml", "/terminal/sessions", "post"),
        ("package.openapi.yaml", "/packages/actions/resolve", "post"),
        ("permission.openapi.yaml", "/permission/role-grants", "post"),
        ("auth.openapi.yaml", "/auth/webauthn/register/options", "post"),
        ("marketplace.openapi.yaml", "/marketplace/listings", "post"),
        ("organization.openapi.yaml", "/enterprises", "post"),
        ("brain.openapi.yaml", "/brain/insights", "post"),
        ("brain.openapi.yaml", "/twin/snapshots", "post"),
    ]
    for spec, api_path, method in cases:
        _assert_422(_load(spec)["paths"][api_path][method]["responses"])
