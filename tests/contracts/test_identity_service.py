"""Identity Kernel contract tests — I-01..I-06 and isolation negatives."""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

from kernel.identity.models import AssignmentMode, ExternalRef, SubjectKind
from kernel.identity.service import IdentityService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode


def _ctx(tenant_id=None, *, platform_scope: bool = False) -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id or uuid4(),
        platform_scope=platform_scope,
    )


def test_i01_register_subject_success() -> None:
    svc = IdentityService()
    ctx = _ctx()
    result = svc.register_subject(
        ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Ada Lovelace",
    )
    assert result.ok
    assert result.data is not None
    assert result.audit_id is not None


def test_i02_duplicate_external_ref() -> None:
    svc = IdentityService()
    ctx = _ctx()
    ref = ExternalRef(system="hr", external_id="E-1")
    first = svc.register_subject(
        ctx, subject_type=SubjectKind.HUMAN, display_name="One", external_refs=[ref]
    )
    assert first.ok
    second = svc.register_subject(
        ctx, subject_type=SubjectKind.HUMAN, display_name="Two", external_refs=[ref]
    )
    assert not second.ok
    assert second.error_code == ErrorCode.IDENTITY_DUPLICATE


def test_register_subject_rejects_ai_type() -> None:
    svc = IdentityService()
    result = svc.register_subject(
        _ctx(), subject_type=SubjectKind.AI_EMPLOYEE, display_name="Bot"
    )
    assert not result.ok
    assert result.error_code == ErrorCode.IDENTITY_INVALID_TYPE


def test_i03_register_ai_employee_permanent_id() -> None:
    ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    svc = IdentityService(platform_governors={ctx.subject_id})
    result = svc.register_ai_employee(ctx, display_name="Shawn AI Assistant")
    assert result.ok
    ai_id = result.data
    assert ai_id is not None

    tenant_ctx = _ctx()
    assign = svc.assign_ai_to_tenant(tenant_ctx, ai_subject_id=ai_id)
    assert assign.ok


def test_ai_profile_is_persisted_and_governor_versioned() -> None:
    ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    svc = IdentityService(platform_governors={ctx.subject_id})
    ai = svc.register_ai_employee(
        ctx,
        display_name="Profiled AI",
        capabilities_profile="capability://profiles/analyst/v1",
        owner_policy="policy://owners/platform/v1",
    )
    assert ai.data

    initial = svc.get_ai_profile(ctx, ai_subject_id=ai.data)
    assert initial.data
    assert initial.data.capabilities_profile_ref.endswith("/analyst/v1")
    updated = svc.update_ai_profile(
        ctx,
        ai_subject_id=ai.data,
        expected_version=1,
        capabilities_profile="capability://profiles/analyst/v2",
        owner_policy="policy://owners/platform/v1",
    )
    assert updated.data and updated.data.version == 2
    stale = svc.update_ai_profile(
        ctx,
        ai_subject_id=ai.data,
        expected_version=1,
        capabilities_profile="capability://profiles/invalid",
        owner_policy="policy://owners/platform/v1",
    )
    assert stale.error_code == ErrorCode.IDENTITY_AI_PROFILE_CONFLICT


def test_i04_bind_credential_never_returns_secret() -> None:
    svc = IdentityService()
    ctx = _ctx()
    reg = svc.register_subject(ctx, subject_type=SubjectKind.HUMAN, display_name="User")
    assert reg.ok and reg.data
    bind = svc.bind_credential(
        ctx,
        subject_id=reg.data,
        credential_kind="password_hash",
        secret_handle="sha256:deadbeef",
    )
    assert bind.ok
    assert bind.data is not None
    # success payload is UUID only
    assert not hasattr(bind.data, "secret_handle")
    assert "deadbeef" not in str(bind.data)


def test_bind_credential_rejects_plaintext_prefix() -> None:
    svc = IdentityService()
    ctx = _ctx()
    reg = svc.register_subject(ctx, subject_type=SubjectKind.HUMAN, display_name="User")
    bind = svc.bind_credential(
        ctx,
        subject_id=reg.data,  # type: ignore[arg-type]
        credential_kind="password",
        secret_handle="plaintext:secret",
    )
    assert not bind.ok
    assert bind.error_code == ErrorCode.IDENTITY_SECRET_LEAK_FORBIDDEN


def test_i05_create_and_revoke_session() -> None:
    svc = IdentityService()
    ctx = _ctx()
    reg = svc.register_subject(ctx, subject_type=SubjectKind.HUMAN, display_name="User")
    assert reg.data
    subject_context = replace(ctx, subject_id=reg.data)
    credential = svc.bind_credential(
        subject_context,
        subject_id=reg.data,
        credential_kind="password_hash",
        secret_handle="vault:session-user",
    )
    assert credential.data is not None
    created = svc.create_session(subject_context, credential_id=credential.data)
    assert created.ok and created.data
    session_id = created.data["session_id"]
    revoked = svc.revoke_session(ctx, session_id=session_id, reason="logout")
    assert revoked.ok


def test_i07_validate_session_returns_bound_non_secret_view() -> None:
    svc = IdentityService()
    registration_context = _ctx()
    registered = svc.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Session User",
    )
    assert registered.data is not None
    subject_context = replace(registration_context, subject_id=registered.data)
    credential = svc.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:i07",
    )
    assert credential.data is not None
    created = svc.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    validated = svc.validate_session(
        subject_context,
        session_id=created.data["session_id"],
    )
    assert validated.data is not None
    assert validated.data.subject_id == registered.data
    assert validated.data.tenant_id == subject_context.tenant_id


def test_i08_revoked_and_expired_sessions_fail_with_specific_codes() -> None:
    svc = IdentityService()
    registration_context = _ctx()
    registered = svc.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Session User",
    )
    assert registered.data is not None
    subject_context = replace(registration_context, subject_id=registered.data)
    credential = svc.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:i08",
    )
    assert credential.data is not None
    created = svc.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    session_id = created.data["session_id"]
    assert svc.revoke_session(
        subject_context,
        session_id=session_id,
        reason="logout",
    ).ok
    revoked = svc.validate_session(subject_context, session_id=session_id)
    assert revoked.error_code == ErrorCode.IDENTITY_SESSION_REVOKED

    second = svc.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert second.data is not None
    expired_session = svc._repo.get_session(second.data["session_id"])
    assert expired_session is not None
    expired_session.expires_at = ExecutionContext.utc_now() - timedelta(seconds=1)
    expired = svc.validate_session(
        subject_context,
        session_id=expired_session.id,
    )
    assert expired.error_code == ErrorCode.IDENTITY_SESSION_EXPIRED


def test_i08_session_tenant_and_subject_mismatch_are_hidden() -> None:
    svc = IdentityService()
    registration_context = _ctx()
    registered = svc.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Session User",
    )
    assert registered.data is not None
    subject_context = replace(registration_context, subject_id=registered.data)
    credential = svc.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:i08-binding",
    )
    assert credential.data is not None
    created = svc.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    session_id = created.data["session_id"]
    wrong_subject = svc.validate_session(
        replace(subject_context, subject_id=uuid4()),
        session_id=session_id,
    )
    wrong_tenant = svc.validate_session(
        replace(subject_context, tenant_id=uuid4()),
        session_id=session_id,
    )
    assert wrong_subject.error_code == ErrorCode.IDENTITY_SESSION_NOT_FOUND
    assert wrong_tenant.error_code == ErrorCode.IDENTITY_SESSION_NOT_FOUND


def test_credential_revocation_blocks_new_sessions_not_existing_sessions() -> None:
    svc = IdentityService()
    registration_context = _ctx()
    registered = svc.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Credential User",
    )
    assert registered.data is not None
    context = replace(registration_context, subject_id=registered.data)
    bound = svc.bind_credential(
        context,
        subject_id=registered.data,
        credential_kind="key_handle",
        secret_handle="vault:credential-user",
    )
    assert bound.data is not None
    validated = svc.validate_credential(context, credential_id=bound.data)
    assert validated.data is not None
    assert not hasattr(validated.data, "secret_handle")
    existing = svc.create_session(context, credential_id=bound.data)
    assert existing.data is not None
    assert svc.revoke_credential(
        context,
        credential_id=bound.data,
        reason="rotated",
    ).ok
    denied = svc.create_session(context, credential_id=bound.data)
    assert denied.error_code == ErrorCode.IDENTITY_CREDENTIAL_REVOKED
    assert svc.validate_session(
        context,
        session_id=existing.data["session_id"],
    ).ok


def test_expired_or_wrong_subject_credential_cannot_create_session() -> None:
    svc = IdentityService()
    registration_context = _ctx()
    registered = svc.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Expired Credential User",
    )
    assert registered.data is not None
    context = replace(registration_context, subject_id=registered.data)
    expired = svc.bind_credential(
        context,
        subject_id=registered.data,
        credential_kind="key_handle",
        secret_handle="vault:expired",
        expires_at=ExecutionContext.utc_now() - timedelta(seconds=1),
    )
    assert expired.data is not None
    assert (
        svc.create_session(
            context,
            credential_id=expired.data,
        ).error_code
        == ErrorCode.IDENTITY_CREDENTIAL_INVALID
    )
    assert (
        svc.validate_credential(
            replace(context, subject_id=uuid4()),
            credential_id=expired.data,
        ).error_code
        == ErrorCode.IDENTITY_CREDENTIAL_INVALID
    )


def test_n01_register_without_tenant_fails() -> None:
    svc = IdentityService()
    ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=None,
    )
    result = svc.register_subject(ctx, subject_type=SubjectKind.HUMAN, display_name="X")
    assert not result.ok
    assert result.error_code == ErrorCode.CTX_MISSING_TENANT


def test_n02_cross_tenant_resolve_denied() -> None:
    svc = IdentityService()
    tenant_a = uuid4()
    tenant_b = uuid4()
    ctx_a = _ctx(tenant_a)
    reg = svc.register_subject(ctx_a, subject_type=SubjectKind.HUMAN, display_name="A")
    assert reg.data
    ctx_b = _ctx(tenant_b)
    resolved = svc.resolve_subject(ctx_b, subject_id=reg.data)
    assert not resolved.ok
    assert resolved.error_code == ErrorCode.IDENTITY_NOT_FOUND


def test_i06_reassign_ai_ends_prior_assignment() -> None:
    platform_ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    svc = IdentityService(platform_governors={platform_ctx.subject_id})
    ai = svc.register_ai_employee(platform_ctx, display_name="Assist")
    assert ai.data
    t1 = uuid4()
    t2 = uuid4()
    a1 = svc.assign_ai_to_tenant(_ctx(t1), ai_subject_id=ai.data)
    assert a1.ok
    moved = svc.reassign_ai(
        platform_ctx,
        ai_subject_id=ai.data,
        to_tenant_id=t2,
        mode=AssignmentMode.REASSIGN,
    )
    assert moved.ok
    # AI subject still resolvable as platform entity via assign path existence
    assert svc._repo.get_subject(ai.data) is not None


def test_ai_assignment_is_globally_exclusive() -> None:
    platform_ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    svc = IdentityService(platform_governors={platform_ctx.subject_id})
    ai = svc.register_ai_employee(platform_ctx, display_name="Exclusive")
    assert ai.data
    assert svc.assign_ai_to_tenant(_ctx(), ai_subject_id=ai.data).ok

    duplicate = svc.assign_ai_to_tenant(_ctx(), ai_subject_id=ai.data)

    assert not duplicate.ok
    assert duplicate.error_code == ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT


def test_inherit_records_lineage_and_archive_needs_no_target() -> None:
    platform_ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    svc = IdentityService(platform_governors={platform_ctx.subject_id})
    ai = svc.register_ai_employee(platform_ctx, display_name="Inherited")
    assert ai.data
    first = svc.assign_ai_to_tenant(_ctx(), ai_subject_id=ai.data)
    assert first.data

    inherited = svc.reassign_ai(
        platform_ctx,
        ai_subject_id=ai.data,
        to_tenant_id=uuid4(),
        mode=AssignmentMode.INHERIT,
    )

    assert inherited.data
    assignment = svc._repo.list_active_assignments(ai.data)[0]
    assert assignment.id == inherited.data
    assert assignment.predecessor_assignment_id == first.data
    archived = svc.reassign_ai(
        platform_ctx,
        ai_subject_id=ai.data,
        mode=AssignmentMode.ARCHIVE,
    )
    assert archived.ok
    assert svc._repo.list_active_assignments(ai.data) == []


def test_tenant_subject_cannot_reassign_ai_cross_tenant() -> None:
    svc = IdentityService()
    result = svc.reassign_ai(
        _ctx(),
        ai_subject_id=uuid4(),
        to_tenant_id=uuid4(),
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_platform_scope_without_identity_governor_is_denied() -> None:
    platform_ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    result = IdentityService().register_ai_employee(
        platform_ctx,
        display_name="Unauthorized AI",
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_persisted_governor_replaces_bootstrap_authority_and_prevents_lockout() -> None:
    bootstrap_context = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
        tenant_id=None,
    )
    service = IdentityService(
        platform_governors={bootstrap_context.subject_id},
    )
    governor_id = uuid4()
    assert service.grant_platform_governor(
        bootstrap_context,
        subject_id=governor_id,
    ).ok
    assert (
        service.register_ai_employee(
            bootstrap_context,
            display_name="Denied after bootstrap",
        ).error_code
        == ErrorCode.PERMISSION_DENIED
    )
    governor_context = replace(bootstrap_context, subject_id=governor_id)
    assert service.register_ai_employee(
        governor_context,
        display_name="Persisted Governor AI",
    ).ok
    second_governor = uuid4()
    assert service.grant_platform_governor(
        governor_context,
        subject_id=second_governor,
    ).ok
    assert service.revoke_platform_governor(
        governor_context,
        subject_id=second_governor,
        reason="rotation",
    ).ok
    last = service.revoke_platform_governor(
        governor_context,
        subject_id=governor_id,
        reason="would lock out",
    )
    assert last.error_code == ErrorCode.IDENTITY_GOVERNOR_LAST_ACTIVE
