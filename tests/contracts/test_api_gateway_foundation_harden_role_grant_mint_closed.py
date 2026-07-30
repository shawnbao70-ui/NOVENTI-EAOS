"""Foundation harden — Role→grant mint closed response DTO."""

from __future__ import annotations

import os
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.schemas.permission import RoleGrantAutoWriteMintResponse
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    reset_permission_role_grant_map,
)
from kernel.permission.service import PermissionService

ADMIN = uuid4()
TENANT = uuid4()
PRINCIPAL = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset_env() -> None:
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
    os.environ.pop("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED", None)
    reset_permission_role_grant_map()
    yield
    reset_permission_role_grant_map()
    if previous is None:
        os.environ.pop("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED", None)
    else:
        os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = previous


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def test_role_grant_mint_matches_closed_response() -> None:
    os.environ["EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED"] = "true"
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read"), ("document", "list")})}
    )
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    client = TestClient(create_app(permission_service=service))
    response = client.post(
        "/v1/permission/role-grants",
        headers=_headers(),
        json={"principal_id": str(PRINCIPAL), "roles": ["operator"]},
    )
    assert response.status_code == 200
    envelope = RoleGrantAutoWriteMintResponse.model_validate(response.json())
    assert envelope.grant_minted is True
    assert envelope.cap_is_grant is False
    assert envelope.title_is_permission is False
    assert envelope.milestone == "PHX-G161"
    assert envelope.grant_count >= 1
    assert envelope.grants
