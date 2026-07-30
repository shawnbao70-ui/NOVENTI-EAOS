"""Deploy region identity helpers (PHX-G76 / ADR-0095)."""

from __future__ import annotations

import os
import re

# DNS-label-ish: keep ops tags short and safe for K8s labels.
_REGION_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]{0,61}[a-z0-9])?$")

_UNSET = object()
_OVERRIDE: object = _UNSET


def configure_deploy_region(region: str | None | object = _UNSET) -> None:
    """Test helper — pass None to force empty; omit/_UNSET clears override."""

    global _OVERRIDE
    _OVERRIDE = region


def deploy_region() -> str | None:
    if _OVERRIDE is not _UNSET:
        if _OVERRIDE is None:
            return None
        text = str(_OVERRIDE).strip().lower()
        return text or None
    raw = (os.environ.get("EAOS_DEPLOY_REGION") or "").strip().lower()
    if not raw:
        return None
    if not _REGION_RE.fullmatch(raw):
        raise RuntimeError(
            "EAOS_DEPLOY_REGION must be a lowercase DNS-label-like token "
            "(letters, digits, '.', '-'; max 63)"
        )
    return raw
