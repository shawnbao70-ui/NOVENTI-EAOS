"""PHX-G44 Terminal Extension signature cryptography contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.service import WorkflowService
from smart_terminal.models import ExtensionStatus, TerminalExtension
from smart_terminal.service import SmartTerminalService
from smart_terminal.signing import (
    ExtensionSigningSettings,
    sign_extension_ed25519_v1,
    sign_extension_hmac_v1,
)

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()
HMAC_SECRET = "extension-signing-secret-32bxx"


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ACTOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _services(signing: ExtensionSigningSettings) -> SmartTerminalService:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    admin = ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert permission.grant(
        admin,
        principal_subject_id=ACTOR,
        resource_type="terminal_extension",
        actions={"register", "activate", "revoke", "read", "invoke"},
    ).ok
    return SmartTerminalService(
        permission,
        WorkflowService(permission),
        signing=signing,
    )


def _proto(
    *,
    extension_key: str,
    version: str = "1.0.0",
    data_scope: str = "tenant.demo",
) -> TerminalExtension:
    now = datetime.now(timezone.utc)
    return TerminalExtension(
        id=uuid4(),
        tenant_id=TENANT,
        extension_key=extension_key,
        version=version,
        signature_ref=None,
        status=ExtensionStatus.REGISTERED,
        declared_capabilities=frozenset(),
        declared_actions=frozenset({"panel.render"}),
        allowed_surfaces=frozenset({"extensions"}),
        data_scope=data_scope,
        created_at=now,
        updated_at=now,
    )


def test_hmac_activate_accepts_valid_and_rejects_invalid() -> None:
    terminal = _services(
        ExtensionSigningSettings(mode="hmac", required=True, hmac_secret=HMAC_SECRET)
    )
    ctx = _ctx()
    proto = _proto(extension_key="noventi.signed.ok")
    good = sign_extension_hmac_v1(secret=HMAC_SECRET, extension=proto)
    created = terminal.register_extension(
        ctx,
        extension_key=proto.extension_key,
        version=proto.version,
        signature_ref=good,
        declared_actions=list(proto.declared_actions),
        allowed_surfaces=list(proto.allowed_surfaces),
        data_scope=proto.data_scope,
    )
    assert created.data is not None
    assert terminal.activate_extension(ctx, extension_id=created.data).ok

    bad_proto = _proto(extension_key="noventi.signed.bad")
    created_bad = terminal.register_extension(
        ctx,
        extension_key=bad_proto.extension_key,
        version=bad_proto.version,
        signature_ref="v1:hmac-sha256:" + ("0" * 64),
        declared_actions=list(bad_proto.declared_actions),
        allowed_surfaces=list(bad_proto.allowed_surfaces),
        data_scope=bad_proto.data_scope,
    )
    assert created_bad.data is not None
    denied = terminal.activate_extension(ctx, extension_id=created_bad.data)
    assert denied.error_code == ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID


def test_required_unconfigured_fail_closed() -> None:
    terminal = _services(ExtensionSigningSettings(mode="off", required=True))
    ctx = _ctx()
    created = terminal.register_extension(
        ctx,
        extension_key="noventi.req",
        version="1.0.0",
        signature_ref="sig:opaque",
        declared_actions=["panel.render"],
        allowed_surfaces=["extensions"],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    denied = terminal.activate_extension(ctx, extension_id=created.data)
    assert denied.error_code == ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED


def test_ed25519_activate_round_trip() -> None:
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    private_key = ed25519.Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    terminal = _services(
        ExtensionSigningSettings(
            mode="ed25519",
            required=True,
            ed25519_public_key_pem=public_pem,
        )
    )
    ctx = _ctx()
    proto = _proto(extension_key="noventi.ed.panel")
    sig = sign_extension_ed25519_v1(private_key_pem=private_pem, extension=proto)
    created = terminal.register_extension(
        ctx,
        extension_key=proto.extension_key,
        version=proto.version,
        signature_ref=sig,
        declared_actions=list(proto.declared_actions),
        allowed_surfaces=list(proto.allowed_surfaces),
        data_scope=proto.data_scope,
    )
    assert created.data is not None
    assert terminal.activate_extension(ctx, extension_id=created.data).ok
