"""Workflow HTTP surface — thin transport adapter (PHX-G23)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import WorkflowGatewayService, get_workflow_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.foundation_status import WorkflowStatusEnvelope
from api.gateway.schemas.permission import VersionedReasonRequest
from api.gateway.schemas.workflow import (
    CancelInstanceRequest,
    CompensateInstanceRequest,
    CreateDefinitionRequest,
    InstanceStatusResult,
    SignalRequest,
    StartInstanceRequest,
    StartInstanceResult,
    TaskApprovalRequest,
    TaskEscalationRequest,
    TaskRejectionRequest,
    WorkflowInstanceResponse,
    WorkflowTaskResponse,
)
from api.gateway.serializers.workflow import (
    ok_response,
    serialize_instance,
    serialize_start,
    serialize_status,
    serialize_task,
    uuid_result,
)
from kernel.shared.context import ExecutionContext
from kernel.workflow.models import TaskStatus

router = APIRouter(prefix="/v1/workflow", tags=["Workflow"])


@router.get("/status", response_model=WorkflowStatusEnvelope)
def get_workflow_status() -> WorkflowStatusEnvelope:
    """Workflow posture (G104) + multi-step executable narrow deepen (PHX-G403)."""

    return WorkflowStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "approval_source_of_truth": "workflow_kernel",
                "supported_surfaces": [
                    "definition_register",
                    "definition_deprecate",
                    "instance_start",
                    "instance_get",
                    "instance_signal",
                    "instance_cancel",
                    "instance_compensate",
                    "task_list",
                    "task_approval",
                    "task_rejection",
                    "task_escalation",
                ],
                "multi_step_executable": True,
                "multi_step_scope": "kernel_task_approve_reject_escalate",
                "legacy_multi_step_implemented": False,
                "escalation_fail_closed": True,
                "compensation_engine_invent": False,
                "sla_engine_invent": False,
                "commercial_auto_write": False,
            }
        }
    )


@router.post(
    "/definitions",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def create_definition(
    body: CreateDefinitionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = workflow.register_definition(
        ctx,
        name=body.name,
        definition_document_ref=body.definition_document_ref,
        version=body.version,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/definitions/{definition_id}/deprecation", response_model=OkResponse)
def deprecate_definition(
    definition_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = workflow.deprecate_definition(ctx, definition_id=definition_id)
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post(
    "/instances",
    response_model=StartInstanceResult,
    status_code=status.HTTP_201_CREATED,
)
def start_instance(
    body: StartInstanceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> StartInstanceResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = workflow.start(
        ctx,
        definition_id=body.definition_id,
        payload=body.payload,
        business_key=body.business_key,
        approval_subject_id=body.approval_subject_id,
        approval_principal_subject_id=body.approval_principal_id,
        approval_action=body.approval_action,
        approval_resource_ref=body.approval_resource_ref,
        approval_plan_version=body.approval_plan_version,
        approval_scope=body.approval_scope,
        approval_expires_at=body.approval_expires_at,
        due_at=body.due_at,
    )
    raise_for_result(result)
    assert result.data is not None
    return StartInstanceResult.model_validate(
        serialize_start(result.data, audit_id=result.audit_id)
    )


@router.get("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
def get_instance(
    instance_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> WorkflowInstanceResponse:
    result = workflow.get_instance(ctx, instance_id=instance_id)
    raise_for_result(result)
    assert result.data is not None
    return WorkflowInstanceResponse.model_validate(serialize_instance(result.data))


@router.post("/instances/{instance_id}/signals", response_model=InstanceStatusResult)
def signal_instance(
    instance_id: UUID,
    body: SignalRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = workflow.signal(
        ctx,
        instance_id=instance_id,
        signal_name=body.signal_name,
        idempotency_key=body.idempotency_key,
        payload=body.payload,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/instances/{instance_id}/cancellation",
    response_model=InstanceStatusResult,
)
def cancel_instance(
    instance_id: UUID,
    body: CancelInstanceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump())
    result = workflow.cancel(
        ctx,
        instance_id=instance_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/instances/{instance_id}/compensation",
    response_model=InstanceStatusResult,
)
def compensate_instance(
    instance_id: UUID,
    body: CompensateInstanceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump())
    result = workflow.compensate(
        ctx,
        instance_id=instance_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/instances/{instance_id}/tasks/{task_id}/approval",
    response_model=InstanceStatusResult,
)
def approve_task(
    instance_id: UUID,
    task_id: UUID,
    body: TaskApprovalRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump(exclude_none=True))
    # expected_instance_version is closed-contract honesty; Kernel uses task version.
    _ = body.expected_instance_version
    result = workflow.approve(
        ctx,
        instance_id=instance_id,
        task_id=task_id,
        comment=body.comment,
        expected_version=body.expected_task_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/instances/{instance_id}/tasks/{task_id}/rejection",
    response_model=InstanceStatusResult,
)
def reject_task(
    instance_id: UUID,
    task_id: UUID,
    body: TaskRejectionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump())
    _ = body.expected_instance_version
    result = workflow.reject(
        ctx,
        instance_id=instance_id,
        task_id=task_id,
        reason=body.reason,
        expected_version=body.expected_task_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/instances/{instance_id}/tasks/{task_id}/escalation",
    response_model=InstanceStatusResult,
)
def escalate_task(
    instance_id: UUID,
    task_id: UUID,
    body: TaskEscalationRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
) -> InstanceStatusResult:
    reject_context_override(body.model_dump())
    _ = body.expected_instance_version
    result = workflow.escalate(
        ctx,
        instance_id=instance_id,
        task_id=task_id,
        to_subject_id=body.to_subject_id,
        reason=body.reason,
        expected_version=body.expected_task_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return InstanceStatusResult.model_validate(
        serialize_status(result.data, audit_id=result.audit_id)
    )


@router.get("/tasks", response_model=list[WorkflowTaskResponse])
def list_tasks(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    workflow: WorkflowGatewayService = Depends(get_workflow_service),
    assignee_subject_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[WorkflowTaskResponse]:
    parsed_status: TaskStatus | None = None
    if status_filter is not None:
        try:
            parsed_status = TaskStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMMON_VALIDATION_FAILED",
                    "message": "status is invalid",
                },
            ) from exc
    result = workflow.list_tasks(
        ctx,
        assignee_subject_id=assignee_subject_id,
        status=parsed_status,
    )
    raise_for_result(result)
    assert result.data is not None
    return [
        WorkflowTaskResponse.model_validate(serialize_task(item))
        for item in result.data
    ]
