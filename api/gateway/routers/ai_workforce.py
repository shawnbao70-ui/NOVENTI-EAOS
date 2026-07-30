"""AI Workforce thin boundary HTTP surface (PHX-G379)."""

from __future__ import annotations

from fastapi import APIRouter

from api.gateway.schemas.ai_workforce import AiWorkforceStatusEnvelope

router = APIRouter(
    prefix="/v1/platform/ai-workforce",
    tags=["AiWorkforce"],
)


@router.get("/status", response_model=AiWorkforceStatusEnvelope)
def get_ai_workforce_status() -> AiWorkforceStatusEnvelope:
    """Read-only AI Workforce thin posture; no task engine or labor write (PHX-G379)."""

    return AiWorkforceStatusEnvelope.model_validate(
        {
            "data": {
                "task_engine": False,
                "labor_write": False,
                "commercial_auto_write": False,
                "execution_authority": "none",
                "digital_employee_identity_separate": True,
            }
        }
    )
