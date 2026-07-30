"""OIDC multi-provider login catalog (PHX-G84/G86 / ADR-0103/0105)."""

from __future__ import annotations

import os
from dataclasses import dataclass

_UNSET = object()
_PROVIDERS_OVERRIDE: object = _UNSET


@dataclass(frozen=True, slots=True)
class OidcLoginProvider:
    key: str
    issuer: str
    client_id: str
    client_secret: str | None
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    end_session_endpoint: str | None = None


def configure_oidc_login_providers(
    providers: dict[str, OidcLoginProvider] | None | object = _UNSET,
) -> None:
    """Test helper — pass mapping to override; omit/_UNSET leaves override unchanged."""

    global _PROVIDERS_OVERRIDE
    if providers is not _UNSET:
        _PROVIDERS_OVERRIDE = providers


def reset_oidc_login_providers() -> None:
    global _PROVIDERS_OVERRIDE
    _PROVIDERS_OVERRIDE = _UNSET


def parse_oidc_login_providers(raw: str) -> dict[str, OidcLoginProvider]:
    """Parse ``key|issuer|client_id|client_secret[:|authorize|token|end_session],...``.

    ``client_secret`` may be empty. Optional 5th–7th fields override authorize/token/end_session.
    Empty middle fields are allowed (e.g. ``key|iss|cid|sec|||https://logout``).
    """

    text = (raw or "").strip()
    if not text:
        return {}
    mapping: dict[str, OidcLoginProvider] = {}
    for part in text.split(","):
        piece = part.strip()
        if not piece:
            continue
        fields = [item.strip() for item in piece.split("|")]
        if len(fields) < 3:
            continue
        key = fields[0]
        issuer = fields[1]
        client_id = fields[2]
        client_secret = fields[3] if len(fields) > 3 and fields[3] else None
        authorize = fields[4] if len(fields) > 4 and fields[4] else None
        token = fields[5] if len(fields) > 5 and fields[5] else None
        end_session = fields[6] if len(fields) > 6 and fields[6] else None
        if not key or not issuer or not client_id:
            continue
        mapping[key] = OidcLoginProvider(
            key=key,
            issuer=issuer.rstrip("/"),
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint=authorize,
            token_endpoint=token,
            end_session_endpoint=end_session,
        )
    return mapping


def oidc_login_providers() -> dict[str, OidcLoginProvider]:
    if _PROVIDERS_OVERRIDE is not _UNSET:
        if _PROVIDERS_OVERRIDE is None:
            return {}
        return dict(_PROVIDERS_OVERRIDE)  # type: ignore[arg-type]
    return parse_oidc_login_providers(
        os.environ.get("EAOS_OIDC_LOGIN_PROVIDERS") or ""
    )


def oidc_login_providers_enabled() -> bool:
    return bool(oidc_login_providers())


def get_oidc_login_provider(key: str) -> OidcLoginProvider | None:
    needle = (key or "").strip()
    if not needle:
        return None
    return oidc_login_providers().get(needle)


def oidc_login_providers_public() -> list[dict[str, str | bool]]:
    """Desensitized catalog for status / providers API."""

    rows: list[dict[str, str | bool]] = []
    for item in sorted(oidc_login_providers().values(), key=lambda row: row.key):
        row: dict[str, str | bool] = {
            "key": item.key,
            "issuer": item.issuer,
            "has_end_session": bool(item.end_session_endpoint),
        }
        if item.end_session_endpoint:
            row["end_session_endpoint"] = item.end_session_endpoint
        rows.append(row)
    return rows
