"""Read-only Sample knowledge pack product posture (PHX-G293)."""

from __future__ import annotations

from typing import Any

SAMPLE_PACK_PATH = "docs/knowledge/sample-pack"
SAMPLE_PACK_ROUTES = (
    "/v1/adapters",
    "/v1/knowledge/status",
    "/v1/demo/sample-pack/",
    "/v1/demo/bootstrap",
)


def sample_knowledge_pack_product_posture() -> dict[str, Any]:
    """Desensitized discoverability posture for the G293 sample pack (≠ CRUD)."""

    return {
        "surface": "foundation_sample_knowledge_pack",
        "milestone": "PHX-G293",
        "pack_path": SAMPLE_PACK_PATH,
        "assembles": ["PHX-G290", "PHX-G291", "PHX-G292"],
        "crud": False,
        "brain_execute": "fail_closed",
        "twin_authorize": "fail_closed",
        "usage": ["terminal_demo_walkthrough", "research_observation"],
        "discovery_routes": list(SAMPLE_PACK_ROUTES),
        "fail_closed_reasons": [
            "docs_only_assembly_not_business_module",
            "crm_sales_finance_delivery_crud_still_closed",
            "brain_execute_twin_authorize_remain_closed",
            "not_live_t2_t3_evidence",
        ],
    }
