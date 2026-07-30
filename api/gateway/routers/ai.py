"""AI Runtime HTTP surface — thin transport adapter (PHX-G29)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import AIRuntimeGatewayService, get_ai_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.ai import (
    AgentRunResponse,
    CommitActionRequest,
    CreateAgentRunRequest,
    InvokeToolRequest,
    MemoryEntryResponse,
    RegisterToolRequest,
    RequestAIApprovalRequest,
    ToolInvocationResult,
    WriteMemoryRequest,
)
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.foundation_status import AIStatusEnvelope
from api.gateway.serializers.ai import (
    ok_response,
    serialize_memory,
    serialize_run,
    serialize_tool_invocation,
    uuid_result,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/ai", tags=["AI"])


@router.get("/status", response_model=AIStatusEnvelope)
def get_ai_status() -> AIStatusEnvelope:
    """Read-only AI Runtime Foundation posture (PHX-G117)."""

    return AIStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "ai_subject_required": True,
                "commit_requires_approval": True,
                "supported_surfaces": [
                    "run_create",
                    "run_get",
                    "tool_register",
                    "tool_invoke",
                    "memory_write",
                    "memory_read",
                    "approval_request",
                    "commit_action",
                ],
            }
        }
    )


@router.post("/runs", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_agent_run(
    body: CreateAgentRunRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = ai.create_agent_run(
        ctx,
        goal=body.goal,
        plan_summary=body.plan_summary,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
def get_agent_run(
    run_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> AgentRunResponse:
    result = ai.get_agent_run(ctx, run_id=run_id)
    raise_for_result(result)
    assert result.data is not None
    return AgentRunResponse.model_validate(serialize_run(result.data))


@router.post("/tools", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def register_tool(
    body: RegisterToolRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = ai.register_tool(
        ctx,
        name=body.name,
        description=body.description,
        high_impact=body.high_impact,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/runs/{run_id}/tools/invocations",
    response_model=ToolInvocationResult,
)
def invoke_tool(
    run_id: UUID,
    body: InvokeToolRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> ToolInvocationResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = ai.invoke_tool(
        ctx,
        run_id=run_id,
        tool_name=body.tool_name,
        arguments=body.arguments,
        plan_version=body.plan_version,
        scope=body.scope,
    )
    raise_for_result(result)
    assert result.data is not None
    return ToolInvocationResult.model_validate(
        serialize_tool_invocation(result.data, audit_id=result.audit_id)
    )


@router.post("/runs/{run_id}/memory", response_model=UuidResult)
def write_memory(
    run_id: UUID,
    body: WriteMemoryRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = ai.write_memory(
        ctx,
        run_id=run_id,
        key=body.key,
        value=body.value,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/runs/{run_id}/memory/{key}", response_model=MemoryEntryResponse)
def read_memory(
    run_id: UUID,
    key: str,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> MemoryEntryResponse:
    result = ai.read_memory(ctx, run_id=run_id, key=key)
    raise_for_result(result)
    assert result.data is not None
    return MemoryEntryResponse.model_validate(serialize_memory(result.data))


@router.post(
    "/runs/{run_id}/approvals",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def request_approval(
    run_id: UUID,
    body: RequestAIApprovalRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = ai.request_approval(
        ctx,
        run_id=run_id,
        definition_id=body.definition_id,
        approval_subject_id=body.approval_subject_id,
        action=body.action,
        resource_ref=body.resource_ref,
        plan_version=body.plan_version,
        scope=body.scope,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/runs/{run_id}/commits", response_model=OkResponse)
def commit_action(
    run_id: UUID,
    body: CommitActionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    ai: AIRuntimeGatewayService = Depends(get_ai_service),
) -> OkResponse:
    reject_context_override(body.model_dump(exclude_none=True))
    result = ai.commit_action(
        ctx,
        run_id=run_id,
        action=body.action,
        resource_ref=body.resource_ref,
        plan_version=body.plan_version,
        scope=body.scope,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))
