"""Closed Foundation `/status` response envelopes (runtime ↔ OpenAPI parity)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FoundationStatusData(_ClosedModel):
    writable: Literal[False] = False
    supported_surfaces: list[str] = Field(min_length=1)


class FoundationStatusEnvelope(_ClosedModel):
    data: FoundationStatusData


class BrainStatusData(_ClosedModel):
    """Brain status with confidence/bias honesty (PHX-G389)."""

    writable: Literal[False] = False
    execute_execution: Literal["permission_gated"] = "permission_gated"
    advisory_required: Literal[True] = True
    supported_surfaces: list[str] = Field(min_length=1)
    confidence_field_required: Literal[True] = True
    bias_notes_surface: Literal["insight_payload"] = "insight_payload"
    confidence_drives_execution: Literal[False] = False
    commercial_auto_write: Literal[False] = False


class BrainStatusEnvelope(_ClosedModel):
    data: BrainStatusData


class TwinStatusData(_ClosedModel):
    """Twin status with sync thin honesty (PHX-G388)."""

    writable: Literal[False] = False
    authorize_execution: Literal["permission_gated"] = "permission_gated"
    supported_surfaces: list[str] = Field(min_length=1)
    continuous_sync_daemon: Literal[False] = False
    sync_mode: Literal["snapshot_upsert"] = "snapshot_upsert"
    commercial_auto_write: Literal[False] = False


class TwinStatusEnvelope(_ClosedModel):
    data: TwinStatusData


class WorkflowStatusData(_ClosedModel):
    """Workflow status with multi-step executable honesty (PHX-G403 / Batch-H)."""

    writable: Literal[False] = False
    approval_source_of_truth: str = Field(min_length=1)
    supported_surfaces: list[str] = Field(min_length=1)
    multi_step_executable: Literal[True] = True
    multi_step_scope: Literal["kernel_task_approve_reject_escalate"] = (
        "kernel_task_approve_reject_escalate"
    )
    legacy_multi_step_implemented: Literal[False] = False
    escalation_fail_closed: Literal[True] = True
    compensation_engine_invent: Literal[False] = False
    sla_engine_invent: Literal[False] = False
    commercial_auto_write: Literal[False] = False


class WorkflowStatusEnvelope(_ClosedModel):
    data: WorkflowStatusData


class AIStatusData(_ClosedModel):
    writable: Literal[False] = False
    ai_subject_required: Literal[True] = True
    commit_requires_approval: Literal[True] = True
    supported_surfaces: list[str] = Field(min_length=1)


class AIStatusEnvelope(_ClosedModel):
    data: AIStatusData
