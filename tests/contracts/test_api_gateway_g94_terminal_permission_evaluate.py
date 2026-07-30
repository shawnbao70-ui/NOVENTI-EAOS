"""PHX-G94 Terminal Permission Evaluate Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:  # type: ignore[no-untyped-def]
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_permission_evaluate_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEvaluate"' in html
    assert 'id="btnAdminExplainDecision"' in html
    assert 'id="evalResourceType"' in html
    assert 'id="evalAction"' in html
    assert 'id="evalResourceId"' in html
    assert 'id="evalDecisionId"' in html
    assert "权限 evaluate 薄探针（G94）" in html
    assert 'evaluations: "/v1/permission/evaluations"' in js
    assert "decisionExplanation" in js
    assert "adminEvaluatePermission" in js
    assert "adminExplainLastDecision" in js
    start = js.index("async function adminEvaluatePermission")
    end = js.index("async function adminExplainLastDecision")
    assert "principal_id" not in js[start:end]


def test_gateway_serves_evaluate_ui_and_api() -> None:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    client = TestClient(create_app(permission_service=service))
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Evaluate permission" in page.text
    assert "Explain last decision" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminEvaluatePermission" in script.text

    evaluated = client.post(
        "/v1/permission/evaluations",
        headers=_tenant_headers(),
        json={"action": "read", "resource_type": "document"},
    )
    assert evaluated.status_code == 200
    body = evaluated.json()
    assert "effect" in body
    assert "decision_id" in body
    explained = client.get(
        f"/v1/permission/decisions/{body['decision_id']}/explanation",
        headers=_tenant_headers(),
    )
    assert explained.status_code == 200
