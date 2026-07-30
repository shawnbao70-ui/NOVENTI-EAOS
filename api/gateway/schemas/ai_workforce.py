"""AI Workforce thin status DTOs — runtime parity with platform.openapi.yaml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AiWorkforceStatusData(_ClosedModel):
    """Honest AI Workforce posture (PHX-G379); task engine closed; distinct from DE."""

    task_engine: Literal[False] = False
    labor_write: Literal[False] = False
    commercial_auto_write: Literal[False] = False
    execution_authority: Literal["none"] = "none"
    digital_employee_identity_separate: Literal[True] = True


class AiWorkforceStatusEnvelope(_ClosedModel):
    data: AiWorkforceStatusData
