"""Identity Kernel service — IF-IDENTITY-001 vertical slice."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID, uuid4

from kernel.identity.models import (
    REGISTERABLE_SUBJECT_KINDS,
    AIAssignment,
    AIEmployeeProfile,
    AssignmentMode,
    Credential,
    CredentialValidationView,
    EntityStatus,
    ExternalRef,
    PlatformIdentityGovernorGrant,
    Session,
    SessionValidationView,
    Subject,
    SubjectKind,
)
from kernel.identity.repository import IdentityRepository, InMemoryIdentityRepository
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult


class IdentityService:
    """Tenant-aware Identity operations with fail-closed context checks."""

    def __init__(
        self,
        repository: IdentityRepository | None = None,
        audit_log: AuditLog | None = None,
        platform_governors: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._repo = repository or InMemoryIdentityRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._bootstrap_governors = frozenset(platform_governors or ())

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def register_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_type: SubjectKind | str,
        display_name: str,
        external_refs: Sequence[ExternalRef] | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            kind = SubjectKind(subject_type)
            if kind not in REGISTERABLE_SUBJECT_KINDS:
                raise KernelError(
                    ErrorCode.IDENTITY_INVALID_TYPE,
                    "RegisterSubject does not accept ai_employee; use RegisterAIEmployee",
                )
            if not display_name or not display_name.strip():
                raise KernelError(ErrorCode.COMMON_VALIDATION_FAILED, "display_name is required")

            refs = list(external_refs or [])
            for ref in refs:
                if self._repo.find_by_external_ref(ref) is not None:
                    raise KernelError(
                        ErrorCode.IDENTITY_DUPLICATE,
                        "external reference already registered",
                        details={"system": ref.system, "external_id": ref.external_id},
                    )

            now = datetime.now(timezone.utc)
            subject = Subject(
                id=uuid4(),
                subject_type=kind,
                display_name=display_name.strip(),
                status=EntityStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                tenant_id=ctx.tenant_id,
                external_refs=refs,
            )
            self._repo.add_subject(subject)
            audit = self._audit.record(
                ctx,
                action="Identity.RegisterSubject",
                resource=f"subject:{subject.id}",
                result="ok",
                details={"subject_type": kind.value},
            )
            return KernelResult.success(subject.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except KeyError:
            return KernelResult.failure(ErrorCode.IDENTITY_DUPLICATE, "duplicate external ref")

    def grant_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=False)
            active = self._repo.list_active_governors()
            if active:
                self._require_platform_governor(ctx)
            elif ctx.subject_id not in self._bootstrap_governors:
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "bootstrap identity governor authority is required",
                )
            if self._repo.get_active_governor(subject_id) is not None:
                raise KernelError(
                    ErrorCode.IDENTITY_GOVERNOR_CONFLICT,
                    "subject is already an active identity governor",
                )
            now = datetime.now(timezone.utc)
            grant = PlatformIdentityGovernorGrant(
                id=uuid4(),
                subject_id=subject_id,
                granted_by_subject_id=ctx.subject_id,
                granted_at=now,
            )
            self._repo.add_governor_grant(grant)
            audit = self._audit.record(
                ctx,
                action="Identity.GrantPlatformGovernor",
                resource=f"platform_identity_governor:{grant.id}",
                result="ok",
                details={"subject_id": str(subject_id)},
            )
            return KernelResult.success(grant.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            grant = self._repo.get_active_governor(subject_id)
            if grant is None:
                raise KernelError(
                    ErrorCode.IDENTITY_GOVERNOR_NOT_FOUND,
                    "active identity governor not found",
                )
            if len(self._repo.list_active_governors()) <= 1:
                raise KernelError(
                    ErrorCode.IDENTITY_GOVERNOR_LAST_ACTIVE,
                    "last active identity governor cannot be revoked",
                )
            now = datetime.now(timezone.utc)
            grant.status = EntityStatus.REVOKED
            grant.revoked_by_subject_id = ctx.subject_id
            grant.revoked_at = now
            grant.revocation_reason = reason
            self._repo.save_governor_grant(grant)
            audit = self._audit.record(
                ctx,
                action="Identity.RevokePlatformGovernor",
                resource=f"platform_identity_governor:{grant.id}",
                result="ok",
                details={"subject_id": str(subject_id), "reason": reason},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def register_ai_employee(
        self,
        ctx: ExecutionContext,
        *,
        display_name: str,
        capabilities_profile: str = "default",
        owner_policy: str = "platform",
    ) -> KernelResult[UUID]:
        try:
            # AI identity is platform-managed; allow platform_scope without tenant
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            if not display_name or not display_name.strip():
                raise KernelError(ErrorCode.COMMON_VALIDATION_FAILED, "display_name is required")
            capabilities_ref = self._require_profile_ref(
                capabilities_profile,
                "capabilities_profile",
            )
            owner_ref = self._require_profile_ref(owner_policy, "owner_policy")

            now = datetime.now(timezone.utc)
            subject = Subject(
                id=uuid4(),
                subject_type=SubjectKind.AI_EMPLOYEE,
                display_name=display_name.strip(),
                status=EntityStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                is_platform_managed=True,
                tenant_id=None,
            )
            self._repo.add_subject(subject)
            self._repo.add_ai_profile(
                AIEmployeeProfile(
                    ai_subject_id=subject.id,
                    capabilities_profile_ref=capabilities_ref,
                    owner_policy_ref=owner_ref,
                    created_at=now,
                    updated_at=now,
                )
            )
            audit = self._audit.record(
                ctx,
                action="Identity.RegisterAIEmployee",
                resource=f"subject:{subject.id}",
                result="ok",
                details={
                    "capabilities_profile": capabilities_profile,
                    "owner_policy": owner_policy,
                },
            )
            return KernelResult.success(subject.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
    ) -> KernelResult[AIEmployeeProfile]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            profile = self._repo.get_ai_profile(ai_subject_id)
            if profile is None:
                raise KernelError(
                    ErrorCode.IDENTITY_AI_PROFILE_NOT_FOUND,
                    "AI profile not found",
                )
            return KernelResult.success(profile)
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        expected_version: int,
        capabilities_profile: str,
        owner_policy: str,
    ) -> KernelResult[AIEmployeeProfile]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            profile = self._repo.get_ai_profile(ai_subject_id)
            if profile is None:
                raise KernelError(
                    ErrorCode.IDENTITY_AI_PROFILE_NOT_FOUND,
                    "AI profile not found",
                )
            if expected_version != profile.version:
                raise KernelError(
                    ErrorCode.IDENTITY_AI_PROFILE_CONFLICT,
                    "AI profile version conflict",
                )
            profile.capabilities_profile_ref = self._require_profile_ref(
                capabilities_profile,
                "capabilities_profile",
            )
            profile.owner_policy_ref = self._require_profile_ref(
                owner_policy,
                "owner_policy",
            )
            profile.version += 1
            profile.updated_at = datetime.now(timezone.utc)
            self._repo.save_ai_profile(profile)
            audit = self._audit.record(
                ctx,
                action="Identity.UpdateAIProfile",
                resource=f"subject:{ai_subject_id}",
                result="ok",
                details={"version": profile.version},
            )
            return KernelResult.success(profile, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def resolve_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        external_ref: ExternalRef | None = None,
    ) -> KernelResult[Subject]:
        try:
            require_context(ctx, tenant_data_plane=True)
            subject: Optional[Subject] = None
            if subject_id is not None:
                subject = self._repo.get_subject(subject_id)
            elif external_ref is not None:
                subject = self._repo.find_by_external_ref(external_ref)
            else:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "subject_id or external_ref is required",
                )

            if subject is None:
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "subject not found")

            # Tenant isolation: tenant-scoped subjects must match; AI may be global
            if (
                subject.tenant_id is not None
                and subject.tenant_id != ctx.tenant_id
            ):
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "subject not found")

            return KernelResult.success(subject)
        except KernelError as err:
            return KernelResult.from_error(err)

    def bind_credential(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        credential_kind: str,
        secret_handle: str,
        expires_at: datetime | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if not credential_kind or not secret_handle:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "credential_kind and secret_handle are required",
                )
            # Refuse obvious plaintext password patterns being returned later —
            # we never echo secret_handle in result data.
            if secret_handle.lower().startswith("plaintext:"):
                raise KernelError(
                    ErrorCode.IDENTITY_SECRET_LEAK_FORBIDDEN,
                    "plaintext secrets are forbidden; pass a handle or hash only",
                )

            subject = self._repo.get_subject(subject_id)
            if subject is None:
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "subject not found")
            if subject.tenant_id is not None and subject.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "subject not found")

            now = datetime.now(timezone.utc)
            credential = Credential(
                id=uuid4(),
                subject_id=subject_id,
                tenant_id=ctx.tenant_id,
                credential_kind=credential_kind,
                secret_handle=secret_handle,
                status=EntityStatus.ACTIVE,
                created_at=now,
                expires_at=expires_at,
            )
            self._repo.add_credential(credential)
            audit = self._audit.record(
                ctx,
                action="Identity.BindCredential",
                resource=f"credential:{credential.id}",
                result="ok",
                details={"credential_kind": credential_kind},
            )
            # Result contains only credential_id — never secret_handle
            return KernelResult.success(credential.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def validate_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
    ) -> KernelResult[CredentialValidationView]:
        try:
            require_context(ctx, tenant_data_plane=True)
            credential = self._require_valid_credential(ctx, credential_id)
            return KernelResult.success(
                CredentialValidationView(
                    credential_id=credential.id,
                    subject_id=credential.subject_id,
                    tenant_id=credential.tenant_id,
                    credential_kind=credential.credential_kind,
                    expires_at=credential.expires_at,
                )
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            credential = self._repo.get_credential(credential_id)
            if (
                credential is None
                or credential.tenant_id != ctx.tenant_id
                or credential.subject_id != ctx.subject_id
            ):
                raise KernelError(
                    ErrorCode.IDENTITY_CREDENTIAL_INVALID,
                    "credential not found",
                )
            if credential.status == EntityStatus.REVOKED:
                return KernelResult.success(True)
            credential.status = EntityStatus.REVOKED
            self._repo.save_credential(credential)
            audit = self._audit.record(
                ctx,
                action="Identity.RevokeCredential",
                resource=f"credential:{credential.id}",
                result="ok",
                details={"reason": reason},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_session(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        ttl_seconds: int = 3600,
    ) -> KernelResult[dict]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            credential = self._require_valid_credential(ctx, credential_id)
            if ttl_seconds <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "ttl_seconds must be positive",
                )

            now = datetime.now(timezone.utc)
            session = Session(
                id=uuid4(),
                subject_id=credential.subject_id,
                tenant_id=ctx.tenant_id,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl_seconds),
                credential_id=credential.id,
                correlation_id_at_issue=ctx.correlation_id,
            )
            self._repo.add_session(session)
            audit = self._audit.record(
                ctx,
                action="Identity.CreateSession",
                resource=f"session:{session.id}",
                result="ok",
                details={"credential_id": str(credential.id)},
            )
            return KernelResult.success(
                {"session_id": session.id, "expires_at": session.expires_at},
                audit_id=audit.id,
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def validate_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
    ) -> KernelResult[SessionValidationView]:
        try:
            require_context(ctx, tenant_data_plane=True)
            session = self._repo.get_session(session_id)
            if (
                session is None
                or session.tenant_id != ctx.tenant_id
                or session.subject_id != ctx.subject_id
            ):
                raise KernelError(
                    ErrorCode.IDENTITY_SESSION_NOT_FOUND,
                    "session not found",
                )
            if session.revoked_at is not None:
                raise KernelError(
                    ErrorCode.IDENTITY_SESSION_REVOKED,
                    "session is revoked",
                )
            if session.expires_at <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.IDENTITY_SESSION_EXPIRED,
                    "session is expired",
                )
            return KernelResult.success(
                SessionValidationView(
                    session_id=session.id,
                    subject_id=session.subject_id,
                    tenant_id=session.tenant_id,
                    expires_at=session.expires_at,
                )
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            session = self._repo.get_session(session_id)
            if session is None or session.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "session not found")
            if session.revoked_at is not None:
                return KernelResult.success(True)

            session.revoked_at = datetime.now(timezone.utc)
            self._repo.save_session(session)
            audit = self._audit.record(
                ctx,
                action="Identity.RevokeSession",
                resource=f"session:{session_id}",
                result="ok",
                details={"reason": reason},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def assign_ai_to_tenant(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None

            ai = self._repo.get_subject(ai_subject_id)
            if ai is None or ai.subject_type != SubjectKind.AI_EMPLOYEE:
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "AI employee not found")
            if ai.status != EntityStatus.ACTIVE:
                raise KernelError(ErrorCode.IDENTITY_AI_NOT_ASSIGNABLE, "AI is not assignable")

            if self._repo.list_active_assignments(ai_subject_id):
                raise KernelError(
                    ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
                    "AI already has an active tenant assignment",
                )

            now = datetime.now(timezone.utc)
            assignment = AIAssignment(
                id=uuid4(),
                ai_subject_id=ai_subject_id,
                tenant_id=ctx.tenant_id,
                mode=AssignmentMode.ASSIGN,
                management_policy=management_policy,
                created_at=now,
                effective_from=now,
            )
            self._repo.add_assignment(assignment)
            audit = self._audit.record(
                ctx,
                action="Identity.AssignAIToTenant",
                resource=f"assignment:{assignment.id}",
                result="ok",
                details={"ai_subject_id": str(ai_subject_id)},
            )
            return KernelResult.success(assignment.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def reassign_ai(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        to_tenant_id: UUID | None = None,
        mode: AssignmentMode | str = AssignmentMode.REASSIGN,
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            mode_enum = AssignmentMode(mode)
            ai = self._repo.get_subject(ai_subject_id)
            if ai is None or ai.subject_type != SubjectKind.AI_EMPLOYEE:
                raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "AI employee not found")

            now = datetime.now(timezone.utc)
            active_assignments = self._repo.list_active_assignments(ai_subject_id)
            if len(active_assignments) > 1:
                raise KernelError(
                    ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
                    "AI has multiple active assignments",
                )
            if mode_enum != AssignmentMode.ARCHIVE and to_tenant_id is None:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "to_tenant_id is required for reassignment",
                )
            if mode_enum != AssignmentMode.ARCHIVE and not active_assignments:
                raise KernelError(
                    ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
                    "AI has no active assignment to move",
                )
            for existing in active_assignments:
                existing.status = EntityStatus.ENDED
                existing.effective_to = now
                self._repo.save_assignment(existing)

            if mode_enum == AssignmentMode.ARCHIVE:
                ai.status = EntityStatus.ARCHIVED
                ai.updated_at = now
                self._repo.save_subject(ai)
                audit = self._audit.record(
                    ctx,
                    action="Identity.ReassignAI",
                    resource=f"subject:{ai_subject_id}",
                    result="ok",
                    details={"mode": mode_enum.value},
                )
                return KernelResult.success(ai_subject_id, audit_id=audit.id)

            assert to_tenant_id is not None
            predecessor_id = (
                active_assignments[0].id
                if mode_enum == AssignmentMode.INHERIT
                else None
            )
            assignment = AIAssignment(
                id=uuid4(),
                ai_subject_id=ai_subject_id,
                tenant_id=to_tenant_id,
                mode=mode_enum,
                management_policy=management_policy,
                created_at=now,
                effective_from=now,
                predecessor_assignment_id=predecessor_id,
            )
            self._repo.add_assignment(assignment)
            # Knowledge must not be deleted on reassignment — Identity does not touch knowledge stores.
            audit = self._audit.record(
                ctx,
                action="Identity.ReassignAI",
                resource=f"assignment:{assignment.id}",
                result="ok",
                details={"mode": mode_enum.value, "to_tenant_id": str(to_tenant_id)},
            )
            return KernelResult.success(assignment.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "invalid reassignment mode",
            )

    def _require_valid_credential(
        self,
        ctx: ExecutionContext,
        credential_id: UUID,
    ) -> Credential:
        credential = self._repo.get_credential(credential_id)
        if (
            credential is None
            or credential.tenant_id != ctx.tenant_id
            or credential.subject_id != ctx.subject_id
        ):
            raise KernelError(
                ErrorCode.IDENTITY_CREDENTIAL_INVALID,
                "credential is invalid",
            )
        if credential.status == EntityStatus.REVOKED:
            raise KernelError(
                ErrorCode.IDENTITY_CREDENTIAL_REVOKED,
                "credential is revoked",
            )
        if credential.status != EntityStatus.ACTIVE:
            raise KernelError(
                ErrorCode.IDENTITY_CREDENTIAL_INVALID,
                "credential is not active",
            )
        if (
            credential.expires_at is not None
            and credential.expires_at <= datetime.now(timezone.utc)
        ):
            raise KernelError(
                ErrorCode.IDENTITY_CREDENTIAL_INVALID,
                "credential is expired",
            )
        return credential

    @staticmethod
    def _require_profile_ref(value: str, field_name: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized or len(normalized) > 255:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field_name} must be 1-255 characters",
            )
        return normalized

    def _require_platform_governor(self, ctx: ExecutionContext) -> None:
        if not ctx.platform_scope:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "platform identity governance authority is required",
            )
        active = self._repo.list_active_governors()
        if active:
            authorized = self._repo.get_active_governor(ctx.subject_id) is not None
        else:
            authorized = ctx.subject_id in self._bootstrap_governors
        if not authorized:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "platform identity governance authority is required",
            )
