"""Foundation commercial policy constants and validators (PHX-M17 / ADR-0054)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from kernel.shared.errors import ErrorCode, KernelError

PRICING_MODEL_FIXED = "fixed"
DEFAULT_CURRENCY = "CNY"
DEFAULT_PLATFORM_SHARE_BPS = 2000
MAX_PLATFORM_SHARE_BPS = 5000
BILLING_CYCLE_IMMEDIATE = "immediate"

_PRICE_RE = re.compile(r"^\d+(\.\d{1,2})?$")
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


def normalize_currency(currency: str | None) -> str:
    value = (currency or DEFAULT_CURRENCY).strip().upper()
    if not _CURRENCY_RE.fullmatch(value):
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "currency must be a 3-letter ISO 4217 code",
            details={"currency": currency},
        )
    return value


def normalize_fixed_price(price: str) -> str:
    cleaned = price.strip()
    if not cleaned or not _PRICE_RE.fullmatch(cleaned):
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "price must be a non-negative decimal with up to 2 fractional digits",
            details={"price": price},
        )
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "price is not a valid decimal",
            details={"price": price},
        ) from exc
    if amount < 0:
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "price must be non-negative",
            details={"price": price},
        )
    return format(amount, "f")


def normalize_platform_share_bps(share_bps: int | None) -> int:
    value = DEFAULT_PLATFORM_SHARE_BPS if share_bps is None else int(share_bps)
    if value < 0 or value > MAX_PLATFORM_SHARE_BPS:
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            f"platform_share_bps must be between 0 and {MAX_PLATFORM_SHARE_BPS}",
            details={"platform_share_bps": value},
        )
    return value
