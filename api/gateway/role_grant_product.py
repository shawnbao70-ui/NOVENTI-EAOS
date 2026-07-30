"""Foundation Role→grant product posture (PHX-G146 / G156 / G161).

Read-only helper. Surfaces whether env-gated Role→grant live mint is
enabled (PHX-G161). Default remains disabled (503 fail-closed stub).
Manual grant write remains G128/G129; evaluate-only role map remains G83.
Cap≠grant / title≠permission stay fail-closed. Never Cap→grant invent.
"""

from __future__ import annotations

from typing import Any

from api.gateway.role_grant_auto_write import (
    ROLE_GRANT_AUTO_WRITE_STUB_ROUTES,
    role_grant_auto_write_enabled,
    role_grant_live_mint_ready,
    role_grant_map_configured,
)


def role_grant_product_posture() -> dict[str, Any]:
    """Return desensitized Foundation Role→grant product posture."""

    enabled = role_grant_auto_write_enabled()
    map_ok = role_grant_map_configured()
    mint_ready = role_grant_live_mint_ready()
    reasons: list[str] = []
    if not enabled:
        reasons.append("role_grant_auto_write_enabled_default_false")
        reasons.append("enable_eaos_role_grant_auto_write_enabled_for_live_mint")
    elif not map_ok:
        reasons.append("permission_role_grant_map_empty")
    else:
        reasons.append("role_grant_live_mint_env_gated_g161")
    reasons.extend(
        [
            "cap_is_not_grant",
            "title_is_not_permission",
            "not_cap_to_grant_invent",
            "manual_grant_relatives_g128_g129",
            "evaluate_only_relative_g83_role_grant_map",
            "payment_brain_twin_remain_closed",
        ]
    )
    return {
        "surface": "foundation_role_grant_product",
        "milestone": "PHX-G161",
        "auto_grant_from_role_enabled": enabled,
        "role_grant_map_configured": map_ok,
        "role_grant_live_mint_ready": mint_ready,
        "auto_write_routes": list(ROLE_GRANT_AUTO_WRITE_STUB_ROUTES),
        "auto_write_stub_observability": True,
        "auto_write_default_off": True,
        "manual_grant_relatives": "g128_g129",
        "evaluate_only_relative": "g83_role_grant_map",
        "fail_closed_reasons": reasons,
    }
