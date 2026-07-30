"""Role→grant auto-write routes (PHX-G156 stub → PHX-G161 env-gated mint).

Default: POST role-grants → 503. With EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED +
EAOS_PERMISSION_ROLE_GRANT_MAP: expand roles into Permission grants.
Cap≠grant / title≠permission; never Cap→grant invent.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from api.gateway.context import derive_tenant_context
from api.gateway.deps import PermissionGatewayService, get_permission_service
from api.gateway.role_grant_auto_write import (
    mint_grants_from_roles,
    raise_role_grant_auto_write_disabled,
    raise_role_grant_map_required,
    role_grant_auto_write_enabled,
    role_grant_map_configured,
)
from api.gateway.schemas.permission import (
    RoleGrantAutoWriteMintResponse,
    RoleGrantAutoWriteRequest,
)

router = APIRouter(prefix="/v1/permission", tags=["Permission"])


@router.post("/role-grants", response_model=RoleGrantAutoWriteMintResponse)
def role_grants_auto_write(
    body: RoleGrantAutoWriteRequest | None = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias="X-EAOS-Subject-Id")] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias="X-EAOS-Subject-Type")] = None,
    x_eaos_tenant_id: Annotated[str | None, Header(alias="X-EAOS-Tenant-Id")] = None,
    x_correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> RoleGrantAutoWriteMintResponse:
    """Mint Permission grants from roles when live mint env is enabled.

    Body stays optional so default-off empty POST remains 503 (FastAPI validates
    typed bodies before the handler). When mint is enabled, missing body → 422
    via a ValidationError-shaped detail for closed-DTO honesty.
    Closed DTO forbids tenant_id / platform_scope. Do not call
    reject_context_override — domain field ``roles`` collides with its denylist.
    """

    # Env gates first so default-off stubs stay 503 even with empty body.
    if not role_grant_auto_write_enabled():
        raise_role_grant_auto_write_disabled(auto_write_step="role_grants")
    if not role_grant_map_configured():
        raise_role_grant_map_required(auto_write_step="role_grants")
    if body is None:
        raise HTTPException(
            status_code=getattr(
                status,
                "HTTP_422_UNPROCESSABLE_CONTENT",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            detail=[
                {
                    "type": "missing",
                    "loc": ["body"],
                    "msg": "Field required",
                    "input": None,
                }
            ],
        )
    ctx = derive_tenant_context(
        authorization=authorization,
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_eaos_tenant_id=x_eaos_tenant_id,
        x_correlation_id=x_correlation_id,
    )
    return RoleGrantAutoWriteMintResponse.model_validate(
        mint_grants_from_roles(ctx, permission, body)
    )
