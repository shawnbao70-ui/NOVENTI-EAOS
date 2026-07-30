"""PHX-G412 production auth fail-closed contracts."""

from __future__ import annotations

import os

import pytest

from api.gateway.auth_jwt import JwtSettings
from api.gateway.production_auth import (
    ProductionAuthError,
    production_profile_active,
    validate_production_auth,
)


def test_g412_dev_profile_allows_insecure_defaults() -> None:
    env = {"EAOS_ENV": "development"}
    assert production_profile_active(env) is False
    validate_production_auth(
        settings=JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        ),
        environ=env,
    )


def test_g412_production_rejects_missing_jwt_enforcement() -> None:
    env = {"EAOS_ENV": "production"}
    with pytest.raises(ProductionAuthError) as exc:
        validate_production_auth(
            settings=JwtSettings(
                secret="secret",
                issuer="iss",
                audience="aud",
                allow_dev_headers=False,
                require_jwt=False,
            ),
            environ=env,
        )
    assert "EAOS_REQUIRE_JWT" in str(exc.value)


def test_g412_production_rejects_dev_context_headers() -> None:
    env = {"EAOS_PROFILE": "prod"}
    with pytest.raises(ProductionAuthError) as exc:
        validate_production_auth(
            settings=JwtSettings(
                secret="secret",
                issuer="iss",
                audience="aud",
                allow_dev_headers=True,
                require_jwt=True,
            ),
            environ=env,
        )
    assert "EAOS_ALLOW_DEV_CONTEXT_HEADERS" in str(exc.value)


def test_g412_production_rejects_missing_secret() -> None:
    env = {"EAOS_ENV": "production"}
    with pytest.raises(ProductionAuthError) as exc:
        validate_production_auth(
            settings=JwtSettings(
                secret="",
                issuer="iss",
                audience="aud",
                allow_dev_headers=False,
                require_jwt=True,
            ),
            environ=env,
        )
    assert "EAOS_JWT_SECRET" in str(exc.value)


def test_g412_create_app_fails_closed_under_production_misconfig(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ENV", "production")
    monkeypatch.delenv("EAOS_REQUIRE_JWT", raising=False)
    monkeypatch.delenv("EAOS_ALLOW_DEV_CONTEXT_HEADERS", raising=False)
    monkeypatch.delenv("EAOS_JWT_SECRET", raising=False)
    from api.gateway.app import create_app

    with pytest.raises(ProductionAuthError):
        create_app()
