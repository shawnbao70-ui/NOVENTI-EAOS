"""OIDC refresh session store — memory|sql + optional encrypt (PHX-G61/G63/G64)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session, sessionmaker

from api.gateway.oidc_refresh_crypto import (
    KeyProvider,
    ciphertext_needs_primary_rotation,
    configure_oidc_refresh_encrypt,
    open_token,
    refresh_encrypt_key_count,
    refresh_encrypt_label,
    refresh_key_provider,
    refresh_reencrypt_on_read_enabled,
    seal_token,
)
from kernel.infrastructure.persistence.oidc_refresh_repository import (
    SQLAlchemyOidcRefreshRepository,
)
from kernel.infrastructure.persistence.session import create_session_factory

StoreKind = Literal["memory", "sql"]


@dataclass(slots=True)
class OidcSessionBinding:
    refresh_token: str | None
    id_token: str | None
    created_at: float


_SESSIONS: dict[str, OidcSessionBinding] = {}
_STORE_OVERRIDE: StoreKind | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None
_SQL_REPO: SQLAlchemyOidcRefreshRepository | None = None


def configure_oidc_refresh_store(
    *,
    store: StoreKind | None = None,
    session_factory: sessionmaker[Session] | None = None,
    encrypt: bool | None = None,
    reencrypt_on_read: bool | None = None,
    key_provider: KeyProvider | None = None,
) -> None:
    global _STORE_OVERRIDE, _SESSION_FACTORY, _SQL_REPO
    _STORE_OVERRIDE = store
    _SESSION_FACTORY = session_factory
    _SQL_REPO = None
    _SESSIONS.clear()
    configure_oidc_refresh_encrypt(
        enabled=encrypt,
        reencrypt_on_read=reencrypt_on_read,
        key_provider=key_provider,
    )


def clear_oidc_refresh_store() -> None:
    _SESSIONS.clear()
    global _SQL_REPO
    if refresh_store_kind() == "sql":
        try:
            _sql_repo().clear()
        except RuntimeError:
            pass
    _SQL_REPO = None


def refresh_store_kind() -> StoreKind:
    if _STORE_OVERRIDE is not None:
        return _STORE_OVERRIDE
    raw = (os.environ.get("EAOS_OIDC_REFRESH_STORE") or "memory").strip().lower()
    if raw in ("", "memory"):
        return "memory"
    if raw == "sql":
        return "sql"
    raise RuntimeError("EAOS_OIDC_REFRESH_STORE must be memory or sql")


def refresh_store_label() -> str:
    return "process_memory" if refresh_store_kind() == "memory" else "sql"


def put_oidc_session(jti: str, binding: OidcSessionBinding) -> None:
    sealed = OidcSessionBinding(
        refresh_token=seal_token(binding.refresh_token),
        id_token=seal_token(binding.id_token),
        created_at=binding.created_at,
    )
    if refresh_store_kind() == "sql":
        try:
            _sql_repo().put(
                eaos_jti=jti,
                refresh_token=sealed.refresh_token,
                id_token=sealed.id_token,
            )
        except RuntimeError as exc:
            msg = str(exc)
            if "EAOS_OIDC_REFRESH_ENCRYPT" in msg or "FERNET" in msg:
                raise
            raise RuntimeError(
                "EAOS_OIDC_REFRESH_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        return
    _SESSIONS[jti] = sealed


def get_oidc_session(jti: str) -> OidcSessionBinding | None:
    sealed = _load_sealed(jti)
    if sealed is None:
        return None
    opened = OidcSessionBinding(
        refresh_token=open_token(sealed.refresh_token),
        id_token=open_token(sealed.id_token),
        created_at=sealed.created_at,
    )
    if refresh_reencrypt_on_read_enabled() and (
        ciphertext_needs_primary_rotation(sealed.refresh_token)
        or ciphertext_needs_primary_rotation(sealed.id_token)
    ):
        put_oidc_session(jti, opened)
    return opened


def _load_sealed(jti: str) -> OidcSessionBinding | None:
    if refresh_store_kind() == "sql":
        try:
            row = _sql_repo().get(jti)
        except RuntimeError as exc:
            raise RuntimeError(
                "EAOS_OIDC_REFRESH_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        if row is None:
            return None
        return OidcSessionBinding(
            refresh_token=row.refresh_token,
            id_token=row.id_token,
            created_at=row.created_at.timestamp(),
        )
    return _SESSIONS.get(jti)


def pop_oidc_session(jti: str) -> OidcSessionBinding | None:
    if refresh_store_kind() == "sql":
        try:
            tokens = _sql_repo().pop_detached(jti)
        except RuntimeError as exc:
            raise RuntimeError(
                "EAOS_OIDC_REFRESH_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        if tokens is None:
            return None
        refresh_token, id_token = tokens
        return OidcSessionBinding(
            refresh_token=open_token(refresh_token),
            id_token=open_token(id_token),
            created_at=time.time(),
        )
    raw = _SESSIONS.pop(jti, None)
    if raw is None:
        return None
    return OidcSessionBinding(
        refresh_token=open_token(raw.refresh_token),
        id_token=open_token(raw.id_token),
        created_at=raw.created_at,
    )


# re-export for status / tests
__all__ = [
    "OidcSessionBinding",
    "clear_oidc_refresh_store",
    "configure_oidc_refresh_store",
    "get_oidc_session",
    "pop_oidc_session",
    "put_oidc_session",
    "refresh_encrypt_key_count",
    "refresh_encrypt_label",
    "refresh_key_provider",
    "refresh_reencrypt_on_read_enabled",
    "refresh_store_kind",
    "refresh_store_label",
]


def _sql_repo() -> SQLAlchemyOidcRefreshRepository:
    global _SQL_REPO
    if _SQL_REPO is not None:
        return _SQL_REPO
    try:
        factory = (
            _SESSION_FACTORY
            if _SESSION_FACTORY is not None
            else create_session_factory()
        )
    except RuntimeError as exc:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
        ) from exc
    _SQL_REPO = SQLAlchemyOidcRefreshRepository(factory)
    return _SQL_REPO
