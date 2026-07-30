"""Webhook delivery URL safety checks (PHX-E21 SSRF basics)."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from kernel.shared.errors import ErrorCode, KernelError

_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "[::1]"})
_BLOCKED_HOSTS = frozenset(
    {
        "metadata.google.internal",
        "metadata",
        "169.254.169.254",
    }
)
_HOSTNAME_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
    r"(?:\.(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?))*$"
)


def validate_webhook_delivery_url(url: str) -> str:
    """Return a normalized URL or raise EVENT_SUBSCRIPTION_INVALID.

    Basics (not a complete egress firewall):
    - https required, except loopback http for local contract tests
    - no credentials in URL
    - block link-local / metadata hosts and private IP literals
    - reject userinfo, fragments used as smuggling vectors are stripped check
    """

    cleaned = url.strip()
    if not cleaned or len(cleaned) > 2048:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url is required and must be at most 2048 characters",
        )
    parsed = urlparse(cleaned)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()
    if parsed.username or parsed.password:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url must not contain credentials",
        )
    if not host:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url host is required",
        )
    if host in _BLOCKED_HOSTS:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url host is not allowed",
        )
    if scheme == "https":
        pass
    elif scheme == "http" and host in _LOOPBACK_HOSTS:
        pass
    else:
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url must use https (http allowed only for loopback)",
        )
    if parsed.port is not None and not (1 <= parsed.port <= 65535):
        raise KernelError(
            ErrorCode.EVENT_SUBSCRIPTION_INVALID,
            "delivery_url port is invalid",
        )
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        if host not in _LOOPBACK_HOSTS and not _HOSTNAME_RE.fullmatch(host):
            raise KernelError(
                ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                "delivery_url host is invalid",
            ) from None
    else:
        if ip.is_loopback:
            pass
        elif (
            ip.is_private
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise KernelError(
                ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                "delivery_url must not target private or link-local addresses",
            )
    return cleaned
