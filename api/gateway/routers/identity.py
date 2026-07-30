"""Identity HTTP surface — thin transport adapter (PHX-G20)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.gateway.context import (
    derive_platform_context,
    derive_tenant_context,
    reject_context_override,
)
from api.gateway.deps import IdentityGatewayService, get_identity_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import UuidResult
from api.gateway.schemas.foundation_status import FoundationStatusEnvelope
from api.gateway.schemas.identity import (
    AIEmployeeProfileResponse,
    AssignAIRequest,
    BindCredentialRequest,
    CreateSessionRequest,
    CredentialValidationResponse,
    GovernorGrantRequest,
    ReasonRequest,
    ReassignAIRequest,
    RegisterAIEmployeeRequest,
    RegisterSubjectRequest,
    SessionCreatedResponse,
    SessionValidationResponse,
    SubjectResponse,
    UpdateAIProfileRequest,
)
from api.gateway.serializers.identity import (
    serialize_ai_profile,
    serialize_credential_validation,
    serialize_session_created,
    serialize_session_validation,
    serialize_subject,
    uuid_created,
)
from kernel.identity.models import ExternalRef
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/identity", tags=["Identity"])


@router.get("/status", response_model=FoundationStatusEnvelope)
def get_identity_status() -> FoundationStatusEnvelope:
    """Read-only Identity Foundation posture (PHX-G120)."""

    return FoundationStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "subject_register",
                    "subject_resolve",
                    "credential_bind",
                    "credential_validate",
                    "credential_revoke",
                    "session_create",
                    "session_validate",
                    "session_revoke",
                    "platform_governor_grant",
                    "platform_governor_revoke",
                    "ai_employee_register",
                    "ai_employee_profile",
                    "ai_employee_assign",
                    "ai_employee_reassign",
                ],
            }
        }
    )


@router.post("/subjects", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def register_subject(
    body: RegisterSubjectRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    refs = None
    if body.external_refs:
        refs = [
            ExternalRef(system=item.system, external_id=item.external_id)
            for item in body.external_refs
        ]
    result = identity.register_subject(
        ctx,
        subject_type=body.subject_type,
        display_name=body.display_name,
        external_refs=refs,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def resolve_subject(
    subject_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> SubjectResponse:
    result = identity.resolve_subject(ctx, subject_id=subject_id)
    raise_for_result(result)
    assert result.data is not None
    return SubjectResponse.model_validate(serialize_subject(result.data))


@router.post(
    "/credentials",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def bind_credential(
    body: BindCredentialRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = identity.bind_credential(
        ctx,
        subject_id=body.subject_id,
        credential_kind=body.credential_kind,
        secret_handle=body.secret_handle,
        expires_at=body.expires_at,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/credentials/{credential_id}/validation",
    response_model=CredentialValidationResponse,
)
def validate_credential(
    credential_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> CredentialValidationResponse:
    result = identity.validate_credential(ctx, credential_id=credential_id)
    raise_for_result(result)
    assert result.data is not None
    return CredentialValidationResponse.model_validate(
        serialize_credential_validation(result.data)
    )


@router.post(
    "/credentials/{credential_id}/revocation",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_credential(
    credential_id: UUID,
    body: ReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> Response:
    reject_context_override(body.model_dump())
    result = identity.revoke_credential(
        ctx,
        credential_id=credential_id,
        reason=body.reason,
    )
    raise_for_result(result)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions",
    response_model=SessionCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    body: CreateSessionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> SessionCreatedResponse:
    reject_context_override(body.model_dump())
    result = identity.create_session(
        ctx,
        credential_id=body.credential_id,
        ttl_seconds=body.ttl_minutes * 60,
    )
    raise_for_result(result)
    assert result.data is not None
    return SessionCreatedResponse.model_validate(
        serialize_session_created(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/sessions/{session_id}/validation",
    response_model=SessionValidationResponse,
)
def validate_session(
    session_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> SessionValidationResponse:
    result = identity.validate_session(ctx, session_id=session_id)
    raise_for_result(result)
    assert result.data is not None
    return SessionValidationResponse.model_validate(
        serialize_session_validation(result.data)
    )


@router.post(
    "/sessions/{session_id}/revocation",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_session(
    session_id: UUID,
    body: ReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> Response:
    reject_context_override(body.model_dump())
    result = identity.revoke_session(ctx, session_id=session_id, reason=body.reason)
    raise_for_result(result)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/platform-governors",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def grant_platform_governor(
    body: GovernorGrantRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = identity.grant_platform_governor(ctx, subject_id=body.subject_id)
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/platform-governors/{subject_id}/revocation",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_platform_governor(
    subject_id: UUID,
    body: ReasonRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> Response:
    reject_context_override(body.model_dump())
    result = identity.revoke_platform_governor(
        ctx,
        subject_id=subject_id,
        reason=body.reason,
    )
    raise_for_result(result)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/ai-employees",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def register_ai_employee(
    body: RegisterAIEmployeeRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = identity.register_ai_employee(
        ctx,
        display_name=body.display_name,
        capabilities_profile=body.capabilities_profile,
        owner_policy=body.owner_policy,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/ai-employees/{ai_subject_id}/profile",
    response_model=AIEmployeeProfileResponse,
)
def get_ai_profile(
    ai_subject_id: UUID,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> AIEmployeeProfileResponse:
    result = identity.get_ai_profile(ctx, ai_subject_id=ai_subject_id)
    raise_for_result(result)
    assert result.data is not None
    return AIEmployeeProfileResponse.model_validate(
        serialize_ai_profile(result.data)
    )


@router.patch(
    "/ai-employees/{ai_subject_id}/profile",
    response_model=AIEmployeeProfileResponse,
)
def update_ai_profile(
    ai_subject_id: UUID,
    body: UpdateAIProfileRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> AIEmployeeProfileResponse:
    reject_context_override(body.model_dump())
    result = identity.update_ai_profile(
        ctx,
        ai_subject_id=ai_subject_id,
        expected_version=body.expected_version,
        capabilities_profile=body.capabilities_profile,
        owner_policy=body.owner_policy,
    )
    raise_for_result(result)
    assert result.data is not None
    return AIEmployeeProfileResponse.model_validate(
        serialize_ai_profile(result.data)
    )


@router.post(
    "/ai-employees/{ai_subject_id}/assignments",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def assign_ai_to_tenant(
    ai_subject_id: UUID,
    body: AssignAIRequest | None = None,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    payload = body or AssignAIRequest()
    reject_context_override(payload.model_dump())
    result = identity.assign_ai_to_tenant(
        ctx,
        ai_subject_id=ai_subject_id,
        management_policy=payload.management_policy,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/ai-employees/{ai_subject_id}/reassignments",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def reassign_ai(
    ai_subject_id: UUID,
    body: ReassignAIRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    if body.mode != "archive" and body.to_tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "COMMON_VALIDATION_FAILED",
                "message": "to_tenant_id is required unless mode=archive",
            },
        )
    result = identity.reassign_ai(
        ctx,
        ai_subject_id=ai_subject_id,
        to_tenant_id=body.to_tenant_id,
        mode=body.mode,
        management_policy=body.management_policy,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_created(result.data, audit_id=result.audit_id)
    )
