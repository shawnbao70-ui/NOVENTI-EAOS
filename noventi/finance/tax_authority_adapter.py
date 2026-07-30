"""Tax authority adapter — stub + optional live HTTP (PHX-G318 / PHX-G328)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from kernel.shared.errors import ErrorCode, KernelError
from noventi.finance.models import TaxInvoice, TaxRate
from noventi.finance.service import (
    RejectAllTaxAuthority,
    TaxAuthorityPort,
    TaxAuthorityResult,
)

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_DEFAULT_TIMEOUT_SEC = 5.0


def tax_network_enabled() -> bool:
    """Read EAOS_TAX_NETWORK or ENABLE_TAX_NETWORK; default False."""
    for name in ("EAOS_TAX_NETWORK", "ENABLE_TAX_NETWORK"):
        raw = os.environ.get(name)
        if raw is None or not str(raw).strip():
            continue
        return str(raw).strip().casefold() in _TRUTHY
    return False


def tax_authority_endpoint_url() -> str | None:
    """Return EAOS_TAX_AUTHORITY_URL when non-empty; else None."""
    raw = os.environ.get("EAOS_TAX_AUTHORITY_URL")
    if raw is None:
        return None
    url = str(raw).strip()
    return url or None


def tax_authority_bearer() -> str | None:
    """Optional EAOS_TAX_AUTHORITY_BEARER; never log the value."""
    raw = os.environ.get("EAOS_TAX_AUTHORITY_BEARER")
    if raw is None:
        return None
    token = str(raw).strip()
    return token or None


def tax_authority_timeout_sec() -> float:
    """Optional EAOS_TAX_AUTHORITY_TIMEOUT_SEC; default ~5s."""
    raw = os.environ.get("EAOS_TAX_AUTHORITY_TIMEOUT_SEC")
    if raw is None or not str(raw).strip():
        return _DEFAULT_TIMEOUT_SEC
    try:
        value = float(str(raw).strip())
    except ValueError:
        return _DEFAULT_TIMEOUT_SEC
    if value <= 0:
        return _DEFAULT_TIMEOUT_SEC
    return value


@dataclass(frozen=True, slots=True)
class TaxAuthorityAdapterStatus:
    network_flag_enabled: bool
    adapter_kind: str  # "reject_all" | "network_stub" | "http_live"
    live_transport: bool  # True only when flag ON and URL configured
    endpoint_configured: bool


class NetworkTaxAuthorityAdapter:
    """Stub: implements TaxAuthorityPort but never performs live I/O.

    When the network flag is ON without EAOS_TAX_AUTHORITY_URL, raises
    COMMON_CONFLICT explaining that endpoint/transport is not configured.
    """

    def validate_rate(
        self, *, tax_invoice: TaxInvoice, tax_rate: TaxRate
    ) -> TaxAuthorityResult:
        raise KernelError(
            ErrorCode.COMMON_CONFLICT,
            "Tax authority network transport is not configured",
        )


class HttpTaxAuthorityAdapter:
    """Live tax authority transport via stdlib urllib (PHX-G328).

    Fail-closed on network errors, non-2xx, or JSON missing authority_ref.
    Bearer token is never included in error messages or logs.
    """

    def __init__(
        self,
        *,
        url: str,
        bearer: str | None = None,
        timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
    ) -> None:
        self._url = url
        self._bearer = bearer
        self._timeout_sec = timeout_sec

    def validate_rate(
        self, *, tax_invoice: TaxInvoice, tax_rate: TaxRate
    ) -> TaxAuthorityResult:
        payload = {
            "tax_invoice_id": str(tax_invoice.id),
            "tax_code": tax_rate.tax_code,
            "rate_percent": str(tax_rate.rate_percent),
            "amount": str(tax_invoice.amount),
            "currency": tax_invoice.currency,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NOVENTI-EAOS-Finance-TaxAuthority/1.0",
        }
        if self._bearer:
            headers["Authorization"] = f"Bearer {self._bearer}"
        request = urllib.request.Request(
            self._url,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(  # noqa: S310
                request, timeout=self._timeout_sec
            ) as response:
                status = getattr(response, "status", None) or response.getcode()
                raw = response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network request failed",
            ) from None
        except Exception:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network request failed",
            ) from None

        if status is None or int(status) < 200 or int(status) >= 300:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network request failed",
            )

        try:
            data: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network response is invalid",
            ) from None

        if not isinstance(data, dict):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network response is invalid",
            )

        authority_ref = data.get("authority_ref")
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "Tax authority network response is invalid",
            )

        authority_status = data.get("authority_status", "validated")
        if not isinstance(authority_status, str) or not authority_status.strip():
            authority_status = "validated"

        return TaxAuthorityResult(
            authority_ref=authority_ref.strip(),
            authority_status=authority_status.strip(),
        )


def resolve_tax_authority_port() -> TaxAuthorityPort:
    if not tax_network_enabled():
        return RejectAllTaxAuthority()
    url = tax_authority_endpoint_url()
    if url is None:
        return NetworkTaxAuthorityAdapter()
    return HttpTaxAuthorityAdapter(
        url=url,
        bearer=tax_authority_bearer(),
        timeout_sec=tax_authority_timeout_sec(),
    )


def tax_authority_adapter_status() -> TaxAuthorityAdapterStatus:
    enabled = tax_network_enabled()
    endpoint = tax_authority_endpoint_url() is not None
    if not enabled:
        kind = "reject_all"
        live = False
    elif not endpoint:
        kind = "network_stub"
        live = False
    else:
        kind = "http_live"
        live = True
    return TaxAuthorityAdapterStatus(
        network_flag_enabled=enabled,
        adapter_kind=kind,
        live_transport=live,
        endpoint_configured=endpoint,
    )
