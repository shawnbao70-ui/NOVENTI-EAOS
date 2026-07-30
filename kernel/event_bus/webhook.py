"""Webhook delivery transport for Event Bus (PHX-E21 + PHX-E22 HMAC)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol
from urllib.parse import urlparse

from kernel.event_bus.models import EventEnvelope
from kernel.event_bus.repository import EventHandler
from kernel.event_bus.url_safety import validate_webhook_delivery_url
from kernel.shared.errors import ErrorCode, KernelError

SIGNATURE_HEADER = "X-EAOS-Webhook-Signature"
TIMESTAMP_HEADER = "X-EAOS-Webhook-Timestamp"
DEFAULT_SIGNATURE_TOLERANCE_SECONDS = 300


class WebhookPoster(Protocol):
    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> None: ...


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


@dataclass
class RecordingWebhookPoster:
    """Test double that records outbound webhook attempts."""

    calls: list[dict[str, Any]] = field(default_factory=list)
    fail_with: Exception | None = None

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> None:
        self.calls.append({"url": url, "payload": payload, "headers": headers})
        if self.fail_with is not None:
            raise self.fail_with


def serialize_webhook_body(payload: dict[str, Any]) -> bytes:
    """Canonical JSON bytes for POST body and HMAC input."""

    return json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")


def normalize_signing_secret(secret: str | None) -> str | None:
    if secret is None:
        return None
    cleaned = secret.strip()
    if not cleaned:
        return None
    if len(cleaned) < 16 or len(cleaned) > 256:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "signing_secret must be between 16 and 256 characters",
        )
    return cleaned


def sign_webhook_v1(*, secret: str, timestamp: str, body: bytes) -> str:
    material = f"{timestamp}.".encode("utf-8") + body
    digest = hmac.new(secret.encode("utf-8"), material, hashlib.sha256).hexdigest()
    return f"v1={digest}"


def verify_webhook_signature(
    *,
    secret: str,
    body: bytes,
    timestamp: str,
    signature_header: str,
    tolerance_seconds: int = DEFAULT_SIGNATURE_TOLERANCE_SECONDS,
    now: int | None = None,
) -> bool:
    """Return True when v1 HMAC matches and timestamp is within tolerance."""

    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    current = int(time.time()) if now is None else int(now)
    if abs(current - ts) > max(0, tolerance_seconds):
        return False
    expected = sign_webhook_v1(secret=secret, timestamp=str(ts), body=body)
    provided = signature_header.strip()
    return hmac.compare_digest(expected, provided)


class UrllibWebhookPoster:
    """Default poster — JSON POST, no redirects, short timeout."""

    def __init__(self, *, timeout_seconds: float = 5.0) -> None:
        self._timeout = timeout_seconds
        self._opener = urllib.request.build_opener(_NoRedirect())

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> None:
        body = serialize_webhook_body(payload)
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NOVENTI-EAOS-EventBus/0.2",
                **headers,
            },
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=self._timeout) as response:
                status = getattr(response, "status", None) or response.getcode()
                if status is None or int(status) >= 300:
                    raise RuntimeError(f"webhook_http_{status}")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"webhook_http_{exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("webhook_transport_error") from exc


def envelope_to_webhook_payload(event: EventEnvelope) -> dict[str, Any]:
    return {
        "event_id": str(event.event_id),
        "event_name": event.event_name,
        "schema_version": event.schema_version,
        "tenant_id": str(event.tenant_id),
        "correlation_id": event.correlation_id,
        "timestamp": event.timestamp.astimezone().isoformat(),
        "producer": event.producer,
        "payload": _thaw(event.payload),
    }


def build_webhook_handler(
    delivery_url: str,
    *,
    poster: WebhookPoster | None = None,
    signing_secret: str | None = None,
) -> EventHandler:
    validated = validate_webhook_delivery_url(delivery_url)
    secret = normalize_signing_secret(signing_secret)
    transport = poster or UrllibWebhookPoster()
    host = urlparse(validated).hostname or ""

    def handler(event: EventEnvelope) -> None:
        payload = envelope_to_webhook_payload(event)
        headers = {
            "X-EAOS-Event-Id": str(event.event_id),
            "X-EAOS-Event-Name": event.event_name,
            "X-Correlation-Id": event.correlation_id,
            "X-EAOS-Webhook-Host": host,
        }
        if secret is not None:
            body = serialize_webhook_body(payload)
            timestamp = str(int(time.time()))
            headers[TIMESTAMP_HEADER] = timestamp
            headers[SIGNATURE_HEADER] = sign_webhook_v1(
                secret=secret,
                timestamp=timestamp,
                body=body,
            )
        transport.post_json(validated, payload, headers)

    return handler


def resolve_subscribe_target(
    *,
    handler: Callable[[EventEnvelope], None] | None,
    delivery_url: str | None,
    signing_secret: str | None = None,
) -> tuple[Callable[[EventEnvelope], None] | None, str | None, str | None]:
    """Return (in-process handler, validated delivery_url, normalized secret)."""

    cleaned_url = delivery_url.strip() if isinstance(delivery_url, str) else ""
    secret = normalize_signing_secret(signing_secret)
    if cleaned_url:
        return None, validate_webhook_delivery_url(cleaned_url), secret
    if secret is not None:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "signing_secret requires delivery_url",
        )
    if handler is not None and callable(handler):
        return handler, None, None
    raise KernelError(
        ErrorCode.EVENT_SUBSCRIPTION_INVALID,
        "callable handler or delivery_url is required",
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _thaw(item) for key, item in value.items()}
    # MappingProxyType / Mapping
    if hasattr(value, "items") and not isinstance(value, list | tuple | str | bytes):
        try:
            return {key: _thaw(item) for key, item in value.items()}
        except Exception:
            return value
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, list):
        return [_thaw(item) for item in value]
    return value
