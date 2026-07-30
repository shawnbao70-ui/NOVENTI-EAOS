"""Package Platform HTTP surface — thin transport adapter (PHX-G27)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import PackageGatewayService, get_package_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import BooleanResult, UuidResult
from api.gateway.schemas.package import (
    InstallPackageRequest,
    PackageManifestResponse,
    PackageStatusEnvelope,
    PackageSurfacesEnvelope,
    RegisterManifestRequest,
    ResolveActionRequest,
    ResolvedActionResponse,
)
from api.gateway.serializers.package import (
    boolean_result,
    serialize_manifest,
    serialize_resolved_action,
    serialize_surface,
    uuid_result,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/packages", tags=["Package"])


@router.get("/status", response_model=PackageStatusEnvelope)
def get_package_status() -> PackageStatusEnvelope:
    """Package posture (G108) + Terminal resolve alignment honesty (PHX-G398)."""

    return PackageStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "manifest_register",
                    "manifest_get",
                    "manifest_publish",
                    "installation_install",
                    "installation_disable",
                    "surface_list",
                    "action_resolve",
                ],
                "action_resolve_surface": True,
                "surface_list_surface": True,
                "terminal_resolve_aligned": True,
                "terminal_holds_business_truth": False,
            }
        }
    )


@router.post("/manifests", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def register_manifest(
    body: RegisterManifestRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = packages.register_manifest(
        ctx,
        package_key=body.package_key,
        version=body.version,
        package_type=body.package_type,
        surfaces=body.surfaces_as_dicts(),
        actions=body.actions_as_dicts(),
        required_permissions=body.permissions_as_dicts(),
        declared_events=body.declared_events,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/manifests/{manifest_id}", response_model=PackageManifestResponse)
def get_manifest(
    manifest_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> PackageManifestResponse:
    result = packages.get_manifest(ctx, manifest_id=manifest_id)
    raise_for_result(result)
    assert result.data is not None
    return PackageManifestResponse.model_validate(serialize_manifest(result.data))


@router.post("/manifests/{manifest_id}/publish", response_model=BooleanResult)
def publish_manifest(
    manifest_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> BooleanResult:
    result = packages.publish_manifest(ctx, manifest_id=manifest_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/installations",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def install_package(
    body: InstallPackageRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = packages.install_package(ctx, manifest_id=body.manifest_id)
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/installations/{installation_id}/disable",
    response_model=BooleanResult,
)
def disable_installation(
    installation_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> BooleanResult:
    result = packages.disable_installation(ctx, installation_id=installation_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.get("/surfaces", response_model=PackageSurfacesEnvelope)
def list_surfaces(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> PackageSurfacesEnvelope:
    result = packages.list_surfaces(ctx)
    raise_for_result(result)
    assert result.data is not None
    return PackageSurfacesEnvelope.model_validate(
        {"data": [serialize_surface(item) for item in result.data]}
    )


@router.post("/actions/resolve", response_model=ResolvedActionResponse)
def resolve_action(
    body: ResolveActionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    packages: PackageGatewayService = Depends(get_package_service),
) -> ResolvedActionResponse:
    reject_context_override(body.model_dump())
    result = packages.resolve_action(
        ctx,
        action_key=body.action_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ResolvedActionResponse.model_validate(
        serialize_resolved_action(result.data)
    )
