"""Organization HTTP surface — thin transport adapter (PHX-G21 / G32)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import OrganizationGatewayService, get_organization_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.foundation_status import FoundationStatusEnvelope
from api.gateway.schemas.organization import (
    AddMembershipRequest,
    CreateEnterpriseRequest,
    EnterpriseResponse,
    MembershipResponse,
    OrganizationUnitResponse,
    SetUnitStatusRequest,
    TenantResponse,
    TransferMembershipUnitRequest,
    UpsertUnitRequest,
)
from api.gateway.schemas.permission import VersionedReasonRequest
from api.gateway.serializers.organization import (
    id_response,
    ok_response,
    serialize_enterprise,
    serialize_membership,
    serialize_tenant,
    serialize_unit,
)
from kernel.organization.models import OrganizationStatus
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1", tags=["Organization"])


@router.get("/organization/status", response_model=FoundationStatusEnvelope)
def get_organization_status() -> FoundationStatusEnvelope:
    """Read-only Organization Foundation posture (PHX-G122)."""

    return FoundationStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "tenant_get",
                    "enterprise_create",
                    "enterprise_list",
                    "enterprise_get",
                    "unit_upsert",
                    "unit_tree",
                    "membership_add",
                    "membership_list",
                ],
            }
        }
    )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> TenantResponse:
    result = organization.get_tenant(ctx, tenant_id=tenant_id)
    raise_for_result(result)
    assert result.data is not None
    return TenantResponse.model_validate(serialize_tenant(result.data))


@router.post(
    "/enterprises",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def create_enterprise(
    body: CreateEnterpriseRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = organization.create_enterprise(
        ctx,
        legal_name=body.legal_name,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        id_response(result.data, audit_id=result.audit_id)
    )


@router.get("/enterprises", response_model=list[EnterpriseResponse])
def list_enterprises(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> list[EnterpriseResponse]:
    result = organization.list_enterprises(ctx)
    raise_for_result(result)
    assert result.data is not None
    return [
        EnterpriseResponse.model_validate(serialize_enterprise(item))
        for item in result.data
    ]


@router.get("/enterprises/{enterprise_id}", response_model=EnterpriseResponse)
def get_enterprise(
    enterprise_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> EnterpriseResponse:
    result = organization.get_enterprise(ctx, enterprise_id=enterprise_id)
    raise_for_result(result)
    assert result.data is not None
    return EnterpriseResponse.model_validate(serialize_enterprise(result.data))


@router.delete("/enterprises/{enterprise_id}", response_model=OkResponse)
def close_enterprise(
    enterprise_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.close_enterprise(
        ctx,
        enterprise_id=enterprise_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/enterprises/{enterprise_id}/suspension", response_model=OkResponse)
def suspend_enterprise(
    enterprise_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.suspend_enterprise(
        ctx,
        enterprise_id=enterprise_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.delete("/enterprises/{enterprise_id}/suspension", response_model=OkResponse)
def reactivate_enterprise(
    enterprise_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.reactivate_enterprise(
        ctx,
        enterprise_id=enterprise_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.put("/organization-units", response_model=UuidResult)
def upsert_organization_unit(
    body: UpsertUnitRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = organization.upsert_unit(
        ctx,
        unit_type=body.unit_type,
        name=body.name,
        unit_id=body.unit_id,
        enterprise_id=body.enterprise_id,
        parent_unit_id=body.parent_unit_id,
        status=body.status,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        id_response(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/organization-units/tree",
    response_model=list[OrganizationUnitResponse],
)
def get_organization_unit_tree(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
    root_unit_id: UUID | None = Query(default=None),
) -> list[OrganizationUnitResponse]:
    result = organization.get_unit_tree(ctx, root_unit_id=root_unit_id)
    raise_for_result(result)
    assert result.data is not None
    return [
        OrganizationUnitResponse.model_validate(serialize_unit(item))
        for item in result.data
    ]


@router.put("/organization-units/{unit_id}/status", response_model=OkResponse)
def set_organization_unit_status(
    unit_id: UUID,
    body: SetUnitStatusRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.set_unit_status(
        ctx,
        unit_id=unit_id,
        status=body.status,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post(
    "/memberships",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def add_membership(
    body: AddMembershipRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = organization.add_membership(
        ctx,
        subject_id=body.subject_id,
        enterprise_id=body.enterprise_id,
        org_unit_id=body.org_unit_id,
        membership_role_label=body.membership_role_label,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        id_response(result.data, audit_id=result.audit_id)
    )


@router.get("/memberships", response_model=list[MembershipResponse])
def list_memberships(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
    subject_id: UUID | None = Query(default=None),
    org_unit_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[MembershipResponse]:
    parsed_status: OrganizationStatus | None = None
    if status_filter is not None:
        try:
            parsed_status = OrganizationStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMMON_VALIDATION_FAILED",
                    "message": "status is invalid",
                },
            ) from exc
    result = organization.list_memberships(
        ctx,
        subject_id=subject_id,
        org_unit_id=org_unit_id,
        status=parsed_status,
    )
    raise_for_result(result)
    assert result.data is not None
    return [
        MembershipResponse.model_validate(serialize_membership(item))
        for item in result.data
    ]


@router.delete("/memberships/{membership_id}", response_model=OkResponse)
def end_membership(
    membership_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.remove_membership(
        ctx,
        membership_id=membership_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.put("/memberships/{membership_id}/unit", response_model=OkResponse)
def transfer_membership_unit(
    membership_id: UUID,
    body: TransferMembershipUnitRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.transfer_membership_unit(
        ctx,
        membership_id=membership_id,
        to_org_unit_id=body.to_org_unit_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/memberships/{membership_id}/suspension", response_model=OkResponse)
def suspend_membership(
    membership_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.suspend_membership(
        ctx,
        membership_id=membership_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.delete("/memberships/{membership_id}/suspension", response_model=OkResponse)
def reactivate_membership(
    membership_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    organization: OrganizationGatewayService = Depends(get_organization_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = organization.reactivate_membership(
        ctx,
        membership_id=membership_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))
