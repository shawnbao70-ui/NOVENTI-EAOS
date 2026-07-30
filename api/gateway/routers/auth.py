"""OIDC login + IdP status routes — Gateway authentication boundary (PHX-G40/G55/G61)."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from api.gateway.auth_jwt import extract_bearer, jwt_status_view, verify_token
from api.gateway.context import current_jwt_settings
from api.gateway.idp_status import idp_status
from api.gateway.oidc import (
    begin_oidc_login,
    complete_oidc_callback,
    logout_eaos_session,
    oidc_status,
    refresh_eaos_token,
)
from api.gateway.oidc_login_providers import oidc_login_providers_public
from api.gateway.oidc_mfa_enrollment import oidc_mfa_enrollment_url
from api.gateway.schemas.auth import (
    IdpStatusEnvelope,
    JwtStatusEnvelope,
    OidcLogoutEnvelope,
    OidcProvidersEnvelope,
    OidcStatusEnvelope,
    OidcTokenEnvelope,
)

router = APIRouter(prefix="/v1/auth/oidc", tags=["Auth"])
idp_router = APIRouter(prefix="/v1/auth/idp", tags=["Auth"])
jwt_router = APIRouter(prefix="/v1/auth/jwt", tags=["Auth"])


@router.get("/status", response_model=OidcStatusEnvelope)
def get_oidc_status() -> OidcStatusEnvelope:
    return OidcStatusEnvelope.model_validate({"data": oidc_status()})


@idp_router.get("/status", response_model=IdpStatusEnvelope)
def get_idp_status() -> IdpStatusEnvelope:
    """Read-only multi-IdP / JWT status (PHX-G55); never returns secrets."""

    return IdpStatusEnvelope.model_validate({"data": idp_status()})


@jwt_router.get("/status", response_model=JwtStatusEnvelope)
def get_jwt_status() -> JwtStatusEnvelope:
    """Read-only JWT / denylist status (PHX-G96); never lists jtis or secrets."""

    return JwtStatusEnvelope.model_validate(
        {"data": jwt_status_view(current_jwt_settings())}
    )


@router.get("/providers", response_model=OidcProvidersEnvelope)
def oidc_login_providers() -> OidcProvidersEnvelope:
    """Public desensitized login provider catalog (PHX-G84)."""

    return OidcProvidersEnvelope.model_validate(
        {"data": {"providers": oidc_login_providers_public()}}
    )


@router.get("/mfa-enrollment")
def oidc_mfa_enrollment() -> RedirectResponse:
    """Redirect to configured IdP MFA enrollment URL (PHX-G89)."""

    location = oidc_mfa_enrollment_url(raise_on_invalid=True)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_MFA_ENROLLMENT_UNCONFIGURED",
                "message": "EAOS_OIDC_MFA_ENROLLMENT_URL is not configured",
            },
        )
    return RedirectResponse(url=location, status_code=302)


@router.get("/login")
def oidc_login(
    provider: Annotated[str | None, Query()] = None,
) -> RedirectResponse:
    location = begin_oidc_login(provider=provider)
    return RedirectResponse(url=location, status_code=302)


@router.get("/callback", response_model=None)
def oidc_callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> OidcTokenEnvelope | RedirectResponse | JSONResponse:
    if error:
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "code": "GATEWAY_OIDC_DENIED",
                    "message": f"OIDC provider returned error: {error}",
                }
            },
        )
    token = complete_oidc_callback(
        code=code or "",
        state=state or "",
        jwt_settings=current_jwt_settings(),
    )
    accept = (request.headers.get("accept") or "").casefold()
    if "application/json" in accept:
        return OidcTokenEnvelope.model_validate({"data": token})
    fragment = urlencode(
        {
            "access_token": token["access_token"],
            "token_type": token["token_type"],
            "subject_id": token["subject_id"],
            "tenant_id": token["tenant_id"],
        }
    )
    return RedirectResponse(url=f"/terminal/#{fragment}", status_code=302)


@router.post("/refresh", response_model=OidcTokenEnvelope)
def oidc_refresh(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> OidcTokenEnvelope:
    """Refresh EAOS Bearer via stored IdP refresh_token (PHX-G61)."""

    bearer = extract_bearer(authorization)
    if bearer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_AUTH_REQUIRED",
                "message": "Bearer JWT is required for OIDC refresh",
            },
        )
    settings = current_jwt_settings()
    claims = verify_token(bearer, settings)
    return OidcTokenEnvelope.model_validate(
        {"data": refresh_eaos_token(claims=claims, jwt_settings=settings)}
    )


@router.post("/logout", response_model=OidcLogoutEnvelope)
def oidc_logout(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> OidcLogoutEnvelope:
    """Revoke EAOS jti locally; optional RP-Logout URL (PHX-G61)."""

    bearer = extract_bearer(authorization)
    if bearer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_AUTH_REQUIRED",
                "message": "Bearer JWT is required for OIDC logout",
            },
        )
    claims = verify_token(bearer, current_jwt_settings())
    return OidcLogoutEnvelope.model_validate(
        {"data": logout_eaos_session(claims=claims)}
    )
