"""Industry Package boundary HTTP surface (PHX-G378)."""

from __future__ import annotations

from fastapi import APIRouter

from api.gateway.schemas.industry_package import IndustryPackageStatusEnvelope

router = APIRouter(
    prefix="/v1/platform/industry-package",
    tags=["IndustryPackage"],
)


@router.get("/status", response_model=IndustryPackageStatusEnvelope)
def get_industry_package_status() -> IndustryPackageStatusEnvelope:
    """Read-only Industry Package boundary posture; no host install (PHX-G378)."""

    return IndustryPackageStatusEnvelope.model_validate(
        {
            "data": {
                "industry_package_runtime": False,
                "host_install": False,
                "declaration_only": True,
                "package_type_industry_supported_in_manifest": True,
                "execution_authority": "none",
            }
        }
    )
