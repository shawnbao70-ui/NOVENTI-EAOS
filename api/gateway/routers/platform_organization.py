"""Platform Organization HTTP — tenant lifecycle (PHX-G25)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_platform_context, reject_context_override
from api.gateway.deps import OrganizationGatewayService, get_organization_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.organization import CreateTenantRequest
from api.gateway.schemas.permission import VersionedReasonRequest
from api.gateway.serializers.organization import id_response, ok_response
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/platform", tags=["Platform Organization"])


@router.post("/tenants", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_tenant(
    body: CreateTenantRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = organization.create_tenant(
        ctx,
        legal_name=body.legal_name,
        region_policy_ref=body.region_policy_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        id_response(result.data, audit_id=result.audit_id)
    )


@router.post("/tenants/{tenant_id}/suspension", response_model=OkResponse)
def suspend_tenant(
    tenant_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.suspend_tenant(
        ctx,
        tenant_id=tenant_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.delete("/tenants/{tenant_id}/suspension", response_model=OkResponse)
def reactivate_tenant(
    tenant_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.reactivate_tenant(
        ctx,
        tenant_id=tenant_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))
