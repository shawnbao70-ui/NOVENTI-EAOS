"""Allowlisted Marketplace listing → Extension Host projection (PHX-G172).

Technical acquire remains a marketplace record. Host projection only maps
first-party allowlisted package keys onto the sandboxed Extension Host.
Never loads or executes Marketplace arbitrary scripts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID, uuid4

from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from smart_terminal.models import ExtensionStatus, TerminalExtension
from smart_terminal.signing import (
    ExtensionSigningSettings,
    sign_extension_hmac_v1,
)


class _MarketplaceHostPort(Protocol):
    def get_listing(self, ctx: ExecutionContext, *, listing_id: UUID) -> KernelResult[Any]: ...

    def acquire_listing(self, ctx: ExecutionContext, *, listing_id: UUID) -> KernelResult[UUID]: ...


class _TerminalHostPort(Protocol):
    signing_settings: ExtensionSigningSettings

    def list_extensions(self, ctx: ExecutionContext) -> KernelResult[list[TerminalExtension]]: ...

    def register_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_key: str,
        version: str,
        signature_ref: str | None,
        declared_actions: list[str],
        allowed_surfaces: list[str],
        data_scope: str,
    ) -> KernelResult[UUID]: ...

    def activate_extension(
        self, ctx: ExecutionContext, *, extension_id: UUID
    ) -> KernelResult[bool]: ...

# First-party host allowlist only — fail-closed for everything else.
HOST_ACQUIRE_ALLOWLIST = frozenset({"noventi.demo.panel"})
_HOST_ACTIONS = frozenset({"panel.render"})
_HOST_SURFACES = frozenset({"extensions"})


def acquire_listing_for_host(
    *,
    marketplace: _MarketplaceHostPort,
    terminal: _TerminalHostPort,
    ctx: ExecutionContext,
    listing_id: UUID,
) -> KernelResult[dict[str, Any]]:
    """Acquire (idempotent) then project allowlisted listing onto Extension Host."""

    try:
        listing_result = marketplace.get_listing(ctx, listing_id=listing_id)
        if not listing_result.ok or listing_result.data is None:
            return KernelResult.failure(
                listing_result.error_code or ErrorCode.COMMON_VALIDATION_FAILED,
                listing_result.error_message or "listing not found",
                details=listing_result.details,
            )
        listing = listing_result.data
        package_key = listing.package_key
        if package_key not in HOST_ACQUIRE_ALLOWLIST:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "listing package_key is not in the first-party host-acquire allowlist",
                details={"package_key": package_key},
            )

        acquisition_id: UUID | None = None
        already_acquired = False
        acquired = marketplace.acquire_listing(ctx, listing_id=listing_id)
        if acquired.ok and acquired.data is not None:
            acquisition_id = acquired.data
        elif acquired.error_code == ErrorCode.MARKETPLACE_ALREADY_ACQUIRED:
            already_acquired = True
        else:
            return KernelResult.failure(
                acquired.error_code or ErrorCode.COMMON_VALIDATION_FAILED,
                acquired.error_message or "acquire failed",
                details=acquired.details,
            )

        listed = terminal.list_extensions(ctx)
        if not listed.ok or listed.data is None:
            return KernelResult.failure(
                listed.error_code or ErrorCode.COMMON_VALIDATION_FAILED,
                listed.error_message or "list extensions failed",
                details=listed.details,
            )
        match = next(
            (
                item
                for item in listed.data
                if item.extension_key == package_key
                and item.status == ExtensionStatus.ACTIVE
            ),
            None,
        )
        if match is not None:
            return KernelResult.success(
                {
                    "listing_id": str(listing_id),
                    "package_key": package_key,
                    "package_version": listing.package_version,
                    "acquisition_id": str(acquisition_id) if acquisition_id else None,
                    "already_acquired": already_acquired,
                    "extension_id": str(match.id),
                    "extension_status": match.status.value,
                    "projected": False,
                    "host_actions": sorted(_HOST_ACTIONS),
                    "notes": [
                        "technical acquire + existing active host extension",
                        "no Marketplace arbitrary script execution",
                    ],
                },
                audit_id=acquired.audit_id or listed.audit_id,
            )

        extension_id = _project_allowlisted_extension(
            terminal,
            ctx=ctx,
            package_key=package_key,
            package_version=listing.package_version,
            data_scope=listing.capability.data_scope or "tenant.demo",
        )
        return KernelResult.success(
            {
                "listing_id": str(listing_id),
                "package_key": package_key,
                "package_version": listing.package_version,
                "acquisition_id": str(acquisition_id) if acquisition_id else None,
                "already_acquired": already_acquired,
                "extension_id": str(extension_id),
                "extension_status": ExtensionStatus.ACTIVE.value,
                "projected": True,
                "host_actions": sorted(_HOST_ACTIONS),
                "notes": [
                    "technical acquire + allowlisted first-party host projection",
                    "no Marketplace arbitrary script execution",
                    "not a package install; not a purchase settlement",
                ],
            },
            audit_id=acquired.audit_id,
        )
    except KernelError as err:
        return KernelResult.from_error(err)


def _project_allowlisted_extension(
    terminal: _TerminalHostPort,
    *,
    ctx: ExecutionContext,
    package_key: str,
    package_version: str,
    data_scope: str,
) -> UUID:
    assert ctx.tenant_id is not None
    now = datetime.now(timezone.utc)
    proto = TerminalExtension(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        extension_key=package_key,
        version=package_version,
        signature_ref=None,
        status=ExtensionStatus.REGISTERED,
        declared_capabilities=frozenset(),
        declared_actions=_HOST_ACTIONS,
        allowed_surfaces=_HOST_SURFACES,
        data_scope=data_scope,
        created_at=now,
        updated_at=now,
    )
    settings = terminal.signing_settings
    if settings.mode == "hmac" and settings.hmac_secret:
        signature_ref = sign_extension_hmac_v1(
            secret=settings.hmac_secret,
            extension=proto,
        )
    else:
        signature_ref = "sig:host-acquire:allowlisted"
    registered = terminal.register_extension(
        ctx,
        extension_key=proto.extension_key,
        version=proto.version,
        signature_ref=signature_ref,
        declared_actions=list(proto.declared_actions),
        allowed_surfaces=list(proto.allowed_surfaces),
        data_scope=proto.data_scope,
    )
    if not registered.ok or registered.data is None:
        raise KernelError(
            registered.error_code or ErrorCode.COMMON_VALIDATION_FAILED,
            registered.error_message or "host projection register failed",
            details=registered.details,
        )
    activated = terminal.activate_extension(ctx, extension_id=registered.data)
    if not activated.ok:
        raise KernelError(
            activated.error_code or ErrorCode.COMMON_VALIDATION_FAILED,
            activated.error_message or "host projection activate failed",
            details=activated.details,
        )
    return registered.data
