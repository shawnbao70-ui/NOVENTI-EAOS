"""Foundation Extension iframe/Worker bridge + CSP policy (PHX-G42/G43)."""

from __future__ import annotations

from typing import Any, Mapping

from kernel.shared.errors import ErrorCode, KernelError

ALLOWED_BRIDGE_MESSAGE_TYPES = frozenset({"eaos.extension.invoke"})

ALLOWED_BRIDGE_CHANNELS = frozenset({"iframe", "worker"})

FORBIDDEN_BRIDGE_KEYS = frozenset(
    {
        "tenant_id",
        "subject_id",
        "platform_scope",
        "session_id",
    }
)

DEMO_PANEL_PATH = "/terminal/extensions/demo-panel.html"
DEMO_WORKER_PATH = "/terminal/extensions/demo-worker.js"

# Applied by Gateway to /terminal/extensions/* responses.
EXTENSION_PANEL_CSP = (
    "default-src 'none'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'none'; "
    "font-src 'none'; "
    "connect-src 'none'; "
    "frame-ancestors 'self'; "
    "base-uri 'none'; "
    "form-action 'none'"
)

IFRAME_SANDBOX_TOKENS = frozenset({"allow-scripts"})


def validate_bridge_message(payload: Mapping[str, Any] | None) -> tuple[str, str]:
    """Validate iframe/Worker → host bridge payload for declared invoke."""

    if not isinstance(payload, Mapping):
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
            "extension bridge payload must be an object",
        )
    forbidden = sorted(key for key in FORBIDDEN_BRIDGE_KEYS if key in payload)
    if forbidden:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
            "extension bridge cannot elevate trusted context",
            details={"keys": forbidden},
        )
    message_type = str(payload.get("type") or "").strip()
    if message_type not in ALLOWED_BRIDGE_MESSAGE_TYPES:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
            "extension bridge message type is not allowlisted",
            details={"type": message_type},
        )
    if "channel" in payload:
        channel = str(payload.get("channel") or "").strip()
        if channel not in ALLOWED_BRIDGE_CHANNELS:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
                "extension bridge channel is not allowlisted",
                details={"channel": channel},
            )
    action = str(payload.get("action") or "").strip()
    surface = str(payload.get("surface") or "").strip()
    if not action or not surface:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_INVALID,
            "extension bridge requires action and surface",
        )
    return action, surface
