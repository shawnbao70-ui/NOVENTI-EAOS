"""Marketplace payment clearing (PHX-G162 / Eng Explicit Defer `4`).

Env-gated fail-closed default OFF. Named stub returns 503 until
``EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED=true``. Live path is an
**internal audit-backed clearing record** linked to an existing invoice —
not an external payment-service-provider (PSP) rail.

Explicit Out: external PSP capture/refund, subscription metering,
external arbitration, Brain execute, Twin authorize, Cap→grant invent.
"""

from __future__ import annotations

import os
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status

from api.gateway.deps import MarketplaceGatewayService
from api.gateway.errors import raise_for_result
from kernel.shared.context import ExecutionContext

# Canonical OpenAPI /marketplace-prefix paths for clearing routes.
PAYMENT_CLEARING_ROUTES: tuple[str, ...] = (
    "/marketplace/listings/{listing_id}/payment-clearing",
)
# Back-compat alias for inventory / Terminal copy.
PAYMENT_CLEARING_STUB_ROUTES = PAYMENT_CLEARING_ROUTES

GATEWAY_PAYMENT_CLEARING_DISABLED = "GATEWAY_PAYMENT_CLEARING_DISABLED"

ClearingStep = Literal["payment_clearing"]

_DISABLED_MESSAGE = (
    "Marketplace payment clearing is disabled "
    "(set EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED=true after PHX-G162 / "
    "DAL-G007 / DAL-U035; internal record only — no external PSP)"
)


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().casefold() in {"1", "true", "yes", "on"}


def payment_clearing_enabled() -> bool:
    """Honor EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED (default false; PHX-G162)."""

    return _env_flag("EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED", default=False)


def raise_payment_clearing_disabled(
    *,
    clearing_step: ClearingStep = "payment_clearing",
) -> None:
    """Raise the canonical 503 when payment clearing env is off."""

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": GATEWAY_PAYMENT_CLEARING_DISABLED,
            "message": _DISABLED_MESSAGE,
            "clearing_step": clearing_step,
            "payment_cleared": False,
            "external_psp": False,
            "settlement_rail": "none",
            "next_action": "none",
            "milestone": "PHX-G162",
        },
    )


def payment_clearing_product_posture() -> dict[str, Any]:
    """Return desensitized Foundation payment-clearing product posture."""

    enabled = payment_clearing_enabled()
    reasons: list[str] = []
    if not enabled:
        reasons.append("payment_clearing_enabled_default_false")
        reasons.append("enable_eaos_marketplace_payment_clearing_enabled_for_internal_record")
    else:
        reasons.append("payment_clearing_internal_record_env_gated_g162")
    reasons.extend(
        [
            "external_psp_capture_still_deferred",
            "external_arbitration_still_fail_closed",
            "subscription_metering_still_fail_closed",
            "brain_execute_twin_authorize_remain_closed",
            "not_cap_to_grant_invent",
        ]
    )
    return {
        "surface": "foundation_marketplace_payment_clearing",
        "milestone": "PHX-G162",
        "payment_clearing_enabled": enabled,
        "clearing_routes": list(PAYMENT_CLEARING_ROUTES),
        "clearing_stub_observability": True,
        "settlement_rail": "internal_record_only" if enabled else "disabled",
        "external_psp": False,
        "external_arbitration": "fail_closed",
        "metering": "fail_closed",
        "fail_closed_reasons": reasons,
    }


def record_payment_clearing(
    ctx: ExecutionContext,
    marketplace: MarketplaceGatewayService,
    *,
    listing_id: UUID,
    invoice_id: UUID,
    note: str = "",
) -> dict[str, Any]:
    """Record an internal payment clearing when env is enabled."""

    if not payment_clearing_enabled():
        raise_payment_clearing_disabled(clearing_step="payment_clearing")

    result = marketplace.record_internal_payment_clearing(
        ctx,
        listing_id=listing_id,
        invoice_id=invoice_id,
        note=note or "",
    )
    raise_for_result(result)
    assert result.data is not None
    return {
        "clearing_step": "payment_clearing",
        "payment_cleared": True,
        "external_psp": False,
        "settlement_rail": "internal_record_only",
        "milestone": "PHX-G162",
        "clearing_id": str(result.data),
        "listing_id": str(listing_id),
        "invoice_id": str(invoice_id),
        "audit_id": str(result.audit_id) if result.audit_id is not None else None,
    }
