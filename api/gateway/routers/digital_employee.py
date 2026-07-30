"""Digital Employee thin boundary HTTP surface (PHX-G374)."""

from __future__ import annotations

from fastapi import APIRouter

from api.gateway.schemas.digital_employee import DigitalEmployeeStatusEnvelope

router = APIRouter(
    prefix="/v1/platform/digital-employee",
    tags=["Digital Employee"],
)


@router.get("/status", response_model=DigitalEmployeeStatusEnvelope)
def get_digital_employee_status() -> DigitalEmployeeStatusEnvelope:
    """Read-only Digital Employee thin posture; no labor/commercial write (PHX-G374)."""

    return DigitalEmployeeStatusEnvelope.model_validate(
        {
            "data": {
                "identity_ai_employee_surface": True,
                "labor_write": False,
                "commercial_auto_write": False,
                "execution_authority": "none",
            }
        }
    )
