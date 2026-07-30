"""Industry Package boundary status DTOs — runtime parity with platform.openapi.yaml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IndustryPackageStatusData(_ClosedModel):
    """Honest Industry Package posture (PHX-G378); declaration only, no host install."""

    industry_package_runtime: Literal[False] = False
    host_install: Literal[False] = False
    declaration_only: Literal[True] = True
    package_type_industry_supported_in_manifest: Literal[True] = True
    execution_authority: Literal["none"] = "none"


class IndustryPackageStatusEnvelope(_ClosedModel):
    data: IndustryPackageStatusData
