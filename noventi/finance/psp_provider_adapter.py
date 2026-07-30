"""PSP provider adapter — stub + optional live HTTP (PHX-G326 / PHX-G331)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from kernel.shared.errors import ErrorCode, KernelError
from noventi.finance.models import ARReceipt
from noventi.finance.service import (
    ARInvoiceSnapshot,
    InMemoryFakePsp,
    PspPort,
    PspReceiptResult,
    RejectAllPsp,
)

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_KNOWN_PROVIDERS = frozenset({"off", "fake", "stripe_like"})
_DEFAULT_TIMEOUT_SEC = 5.0


def psp_network_enabled() -> bool:
    """Read EAOS_PSP_NETWORK or ENABLE_PSP_NETWORK; default False."""
    for name in ("EAOS_PSP_NETWORK", "ENABLE_PSP_NETWORK"):
        raw = os.environ.get(name)
        if raw is None or not str(raw).strip():
            continue
        return str(raw).strip().casefold() in _TRUTHY
    return False


def psp_provider() -> str:
    """Read EAOS_PSP_PROVIDER: off | fake | stripe_like (default off)."""
    raw = os.environ.get("EAOS_PSP_PROVIDER")
    if raw is None or not str(raw).strip():
        return "off"
    value = str(raw).strip().casefold()
    if value in _KNOWN_PROVIDERS:
        return value
    return "off"


def psp_endpoint_url() -> str | None:
    """Return EAOS_PSP_URL when non-empty; else None."""
    raw = os.environ.get("EAOS_PSP_URL")
    if raw is None:
        return None
    url = str(raw).strip()
    return url or None


def psp_bearer() -> str | None:
    """Optional EAOS_PSP_BEARER; never log the value."""
    raw = os.environ.get("EAOS_PSP_BEARER")
    if raw is None:
        return None
    token = str(raw).strip()
    return token or None


def psp_timeout_sec() -> float:
    """Optional EAOS_PSP_TIMEOUT_SEC; default ~5s."""
    raw = os.environ.get("EAOS_PSP_TIMEOUT_SEC")
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
class PspAdapterStatus:
    provider: str
    network_flag_enabled: bool
    adapter_kind: str  # "reject_all" | "fake" | "stripe_like_stub" | "http_live"
    live_transport: bool  # True only when stripe_like + network ON + URL
    endpoint_configured: bool


class StripeLikePspAdapter:
    """Stub: implements PspPort but never performs live I/O.

    Returned for EAOS_PSP_PROVIDER=stripe_like when network is OFF, or when
    network is ON without EAOS_PSP_URL. Raises COMMON_CONFLICT — no live HTTP.
    """

    def apply_receipt(
        self, *, receipt: ARReceipt, invoice: ARInvoiceSnapshot
    ) -> PspReceiptResult:
        raise KernelError(
            ErrorCode.COMMON_CONFLICT,
            "PSP network transport is not configured",
        )


class HttpPspAdapter:
    """Live PSP transport via stdlib urllib (PHX-G331).

    Fail-closed on network errors, non-2xx, or JSON missing psp_ref.
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

    def apply_receipt(
        self, *, receipt: ARReceipt, invoice: ARInvoiceSnapshot
    ) -> PspReceiptResult:
        payload = {
            "receipt_id": str(receipt.id),
            "invoice_id": str(invoice.id),
            "amount": str(receipt.amount),
            "currency": receipt.currency,
            "customer_id": str(receipt.customer_id),
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NOVENTI-EAOS-Finance-PSP/1.0",
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
                "PSP network request failed",
            ) from None
        except Exception:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "PSP network request failed",
            ) from None

        if status is None or int(status) < 200 or int(status) >= 300:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "PSP network request failed",
            )

        try:
            data: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "PSP network response is invalid",
            ) from None

        if not isinstance(data, dict):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "PSP network response is invalid",
            )

        psp_ref = data.get("psp_ref")
        if not isinstance(psp_ref, str) or not psp_ref.strip():
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "PSP network response is invalid",
            )

        psp_status = data.get("psp_status", "applied")
        if not isinstance(psp_status, str) or not psp_status.strip():
            psp_status = "applied"

        return PspReceiptResult(
            psp_ref=psp_ref.strip(),
            psp_status=psp_status.strip(),
        )


def resolve_psp_port() -> PspPort:
    provider = psp_provider()
    if provider == "fake":
        return InMemoryFakePsp()
    if provider == "stripe_like":
        if not psp_network_enabled():
            return StripeLikePspAdapter()
        url = psp_endpoint_url()
        if url is None:
            return StripeLikePspAdapter()
        return HttpPspAdapter(
            url=url,
            bearer=psp_bearer(),
            timeout_sec=psp_timeout_sec(),
        )
    return RejectAllPsp()


def psp_adapter_status() -> PspAdapterStatus:
    provider = psp_provider()
    network = psp_network_enabled()
    endpoint = psp_endpoint_url() is not None
    if provider == "fake":
        kind = "fake"
        live = False
    elif provider == "stripe_like":
        if network and endpoint:
            kind = "http_live"
            live = True
        else:
            kind = "stripe_like_stub"
            live = False
    else:
        kind = "reject_all"
        live = False
    return PspAdapterStatus(
        provider=provider,
        network_flag_enabled=network,
        adapter_kind=kind,
        live_transport=live,
        endpoint_configured=endpoint,
    )
