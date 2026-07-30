"""Digital Employee thin status DTOs — runtime parity with platform.openapi.yaml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DigitalEmployeeStatusData(_ClosedModel):
    """Honest Digital Employee posture (PHX-G374); no labor/commercial write."""

    identity_ai_employee_surface: Literal[True] = True
    labor_write: Literal[False] = False
    commercial_auto_write: Literal[False] = False
    execution_authority: Literal["none"] = "none"


class DigitalEmployeeStatusEnvelope(_ClosedModel):
    data: DigitalEmployeeStatusData
