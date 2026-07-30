"""OIDC authorize acr_values/prompt step-up params (PHX-G87 / ADR-0106)."""

from __future__ import annotations

import os

_UNSET = object()
_ACR_VALUES_OVERRIDE: object = _UNSET
_PROMPT_OVERRIDE: object = _UNSET


def configure_oidc_authorize_stepup(
    *,
    acr_values: str | None | object = _UNSET,
    prompt: str | None | object = _UNSET,
) -> None:
    """Test helper — pass values to override; omit/_UNSET leaves that override unchanged."""

    global _ACR_VALUES_OVERRIDE, _PROMPT_OVERRIDE
    if acr_values is not _UNSET:
        _ACR_VALUES_OVERRIDE = acr_values
    if prompt is not _UNSET:
        _PROMPT_OVERRIDE = prompt


def reset_oidc_authorize_stepup() -> None:
    global _ACR_VALUES_OVERRIDE, _PROMPT_OVERRIDE
    _ACR_VALUES_OVERRIDE = _UNSET
    _PROMPT_OVERRIDE = _UNSET


def oidc_authorize_acr_values() -> str | None:
    if _ACR_VALUES_OVERRIDE is not _UNSET:
        if _ACR_VALUES_OVERRIDE is None:
            return None
        text = str(_ACR_VALUES_OVERRIDE).strip()
        return text or None
    raw = (os.environ.get("EAOS_OIDC_AUTHORIZE_ACR_VALUES") or "").strip()
    return raw or None


def oidc_authorize_prompt() -> str | None:
    if _PROMPT_OVERRIDE is not _UNSET:
        if _PROMPT_OVERRIDE is None:
            return None
        text = str(_PROMPT_OVERRIDE).strip()
        return text or None
    raw = (os.environ.get("EAOS_OIDC_AUTHORIZE_PROMPT") or "").strip()
    return raw or None


def oidc_authorize_stepup_enabled() -> bool:
    return oidc_authorize_acr_values() is not None or oidc_authorize_prompt() is not None


def oidc_authorize_stepup_params() -> dict[str, str]:
    """Extra authorize query params; empty when disabled."""

    params: dict[str, str] = {}
    acr_values = oidc_authorize_acr_values()
    if acr_values is not None:
        params["acr_values"] = acr_values
    prompt = oidc_authorize_prompt()
    if prompt is not None:
        params["prompt"] = prompt
    return params
