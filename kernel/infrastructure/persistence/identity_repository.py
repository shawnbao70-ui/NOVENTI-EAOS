"""Tenant-bound SQLAlchemy adapter for the Identity Repository port."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import overload
from uuid import UUID, uuid4

from sqlalchemy import Select, or_, select, update
from sqlalchemy.orm import Session as ORMSession

from kernel.identity.models import (
    AIAssignment,
    AIEmployeeProfile,
    AssignmentMode,
    Credential,
    EntityStatus,
    ExternalRef,
    PlatformIdentityGovernorGrant,
    Session,
    Subject,
    SubjectKind,
)
from kernel.infrastructure.persistence.identity_models import (
    AIAssignmentRecord,
    AIEmployeeProfileRecord,
    CredentialRecord,
    PlatformIdentityGovernorRecord,
    SessionRecord,
    SubjectExternalRefRecord,
    SubjectRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyIdentityRepository:
    """Identity persistence scoped to one tenant or explicit platform access."""

    def __init__(
        self,
        session: ORMSession,
        *,
        tenant_id: UUID | None,
        platform_scope: bool = False,
    ) -> None:
        if platform_scope == (tenant_id is not None):
            raise ValueError("provide either tenant_id or platform_scope")
        self._session = session
        self._tenant_id = tenant_id
        self._platform_scope = platform_scope

    def add_subject(self, subject: Subject) -> None:
        self._require_write_scope(subject.tenant_id)
        self._session.add(
            SubjectRecord(
                id=subject.id,
                tenant_id=subject.tenant_id,
                subject_type=subject.subject_type.value,
                display_name=subject.display_name,
                status=subject.status.value,
                is_platform_managed=subject.is_platform_managed,
                created_at=subject.created_at,
                updated_at=subject.updated_at,
                version=subject.version,
            )
        )
        self._session.add_all(
            [
                SubjectExternalRefRecord(
                    id=uuid4(),
                    subject_id=subject.id,
                    system=ref.system,
                    external_id=ref.external_id,
                    created_at=subject.created_at,
                )
                for ref in subject.external_refs
            ]
        )

    def get_subject(self, subject_id: UUID) -> Subject | None:
        statement = self._visible_subjects().where(SubjectRecord.id == subject_id)
        record = self._session.scalar(statement)
        return self._to_subject(record) if record is not None else None

    def save_subject(self, subject: Subject) -> None:
        self._require_write_scope(subject.tenant_id)
        record = self._session.scalar(
            self._visible_subjects().where(SubjectRecord.id == subject.id)
        )
        if record is None:
            raise KernelError(ErrorCode.IDENTITY_NOT_FOUND, "subject not found")
        record.display_name = subject.display_name
        record.status = subject.status.value
        record.updated_at = subject.updated_at
        record.version = subject.version

    def add_ai_profile(self, profile: AIEmployeeProfile) -> None:
        self._require_platform_scope()
        self._session.flush()
        self._session.add(
            AIEmployeeProfileRecord(
                ai_subject_id=profile.ai_subject_id,
                capabilities_profile_ref=profile.capabilities_profile_ref,
                owner_policy_ref=profile.owner_policy_ref,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
                version=profile.version,
            )
        )

    def get_ai_profile(self, ai_subject_id: UUID) -> AIEmployeeProfile | None:
        self._require_platform_scope()
        record = self._session.get(AIEmployeeProfileRecord, ai_subject_id)
        return None if record is None else self._to_ai_profile(record)

    def save_ai_profile(self, profile: AIEmployeeProfile) -> None:
        self._require_platform_scope()
        result = self._session.execute(
            update(AIEmployeeProfileRecord)
            .where(
                AIEmployeeProfileRecord.ai_subject_id == profile.ai_subject_id,
                AIEmployeeProfileRecord.version == profile.version - 1,
            )
            .values(
                capabilities_profile_ref=profile.capabilities_profile_ref,
                owner_policy_ref=profile.owner_policy_ref,
                updated_at=profile.updated_at,
                version=profile.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.IDENTITY_AI_PROFILE_CONFLICT,
                "AI profile version conflict",
            )

    def find_by_external_ref(self, ref: ExternalRef) -> Subject | None:
        statement = (
            self._visible_subjects()
            .join(
                SubjectExternalRefRecord,
                SubjectExternalRefRecord.subject_id == SubjectRecord.id,
            )
            .where(
                SubjectExternalRefRecord.system == ref.system,
                SubjectExternalRefRecord.external_id == ref.external_id,
            )
        )
        record = self._session.scalar(statement)
        return self._to_subject(record) if record is not None else None

    def add_credential(self, credential: Credential) -> None:
        self._require_write_scope(credential.tenant_id)
        self._session.add(
            CredentialRecord(
                id=credential.id,
                tenant_id=credential.tenant_id,
                subject_id=credential.subject_id,
                credential_kind=credential.credential_kind,
                secret_handle=credential.secret_handle,
                status=credential.status.value,
                created_at=credential.created_at,
                expires_at=credential.expires_at,
            )
        )

    def get_credential(self, credential_id: UUID) -> Credential | None:
        statement = select(CredentialRecord).where(CredentialRecord.id == credential_id)
        if not self._platform_scope:
            statement = statement.where(CredentialRecord.tenant_id == self._tenant_id)
        record = self._session.scalar(statement)
        if record is None:
            return None
        return Credential(
            id=record.id,
            subject_id=record.subject_id,
            tenant_id=record.tenant_id,
            credential_kind=record.credential_kind,
            secret_handle=record.secret_handle,
            status=EntityStatus(record.status),
            created_at=self._as_utc(record.created_at),
            expires_at=self._as_utc(record.expires_at),
        )

    def save_credential(self, credential: Credential) -> None:
        self._require_write_scope(credential.tenant_id)
        record = self._session.scalar(
            select(CredentialRecord).where(
                CredentialRecord.id == credential.id,
                CredentialRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            raise KernelError(
                ErrorCode.IDENTITY_CREDENTIAL_INVALID,
                "credential not found",
            )
        record.status = credential.status.value
        record.expires_at = credential.expires_at

    def add_session(self, session: Session) -> None:
        self._require_write_scope(session.tenant_id)
        self._session.add(
            SessionRecord(
                id=session.id,
                tenant_id=session.tenant_id,
                subject_id=session.subject_id,
                credential_id=session.credential_id,
                created_at=session.created_at,
                expires_at=session.expires_at,
                revoked_at=session.revoked_at,
                correlation_id_at_issue=session.correlation_id_at_issue,
            )
        )

    def get_session(self, session_id: UUID) -> Session | None:
        statement = select(SessionRecord).where(SessionRecord.id == session_id)
        if not self._platform_scope:
            statement = statement.where(SessionRecord.tenant_id == self._tenant_id)
        record = self._session.scalar(statement)
        return self._to_session(record) if record is not None else None

    def save_session(self, session: Session) -> None:
        self._require_write_scope(session.tenant_id)
        statement = select(SessionRecord).where(SessionRecord.id == session.id)
        if not self._platform_scope:
            statement = statement.where(SessionRecord.tenant_id == self._tenant_id)
        record = self._session.scalar(statement)
        if record is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "session not found")
        record.revoked_at = session.revoked_at

    def add_assignment(self, assignment: AIAssignment) -> None:
        self._require_write_scope(assignment.tenant_id)
        self._session.add(
            AIAssignmentRecord(
                id=assignment.id,
                tenant_id=assignment.tenant_id,
                ai_subject_id=assignment.ai_subject_id,
                mode=assignment.mode.value,
                management_policy=assignment.management_policy,
                created_at=assignment.created_at,
                effective_from=assignment.effective_from,
                predecessor_assignment_id=assignment.predecessor_assignment_id,
                effective_to=assignment.effective_to,
                status=assignment.status.value,
            )
        )

    def save_assignment(self, assignment: AIAssignment) -> None:
        self._require_write_scope(assignment.tenant_id)
        statement = select(AIAssignmentRecord).where(
            AIAssignmentRecord.id == assignment.id
        )
        if not self._platform_scope:
            statement = statement.where(
                AIAssignmentRecord.tenant_id == self._tenant_id
            )
        record = self._session.scalar(statement)
        if record is None:
            raise KernelError(
                ErrorCode.IDENTITY_NOT_FOUND,
                "AI assignment not found",
            )
        record.mode = assignment.mode.value
        record.management_policy = assignment.management_policy
        record.effective_from = assignment.effective_from
        record.effective_to = assignment.effective_to
        record.status = assignment.status.value

    def list_active_assignments(self, ai_subject_id: UUID) -> list[AIAssignment]:
        statement = select(AIAssignmentRecord).where(
            AIAssignmentRecord.ai_subject_id == ai_subject_id,
            AIAssignmentRecord.status == EntityStatus.ACTIVE.value,
        )
        if not self._platform_scope:
            statement = statement.where(
                AIAssignmentRecord.tenant_id == self._tenant_id
            )
        return [
            self._to_assignment(record)
            for record in self._session.scalars(statement).all()
        ]

    def add_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None:
        self._require_platform_scope()
        self._session.add(
            PlatformIdentityGovernorRecord(
                id=grant.id,
                subject_id=grant.subject_id,
                granted_by_subject_id=grant.granted_by_subject_id,
                granted_at=grant.granted_at,
                status=grant.status.value,
                revoked_by_subject_id=grant.revoked_by_subject_id,
                revoked_at=grant.revoked_at,
                revocation_reason=grant.revocation_reason,
            )
        )

    def save_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None:
        self._require_platform_scope()
        record = self._session.get(PlatformIdentityGovernorRecord, grant.id)
        if record is None:
            raise KernelError(
                ErrorCode.IDENTITY_GOVERNOR_NOT_FOUND,
                "identity governor grant not found",
            )
        record.status = grant.status.value
        record.revoked_by_subject_id = grant.revoked_by_subject_id
        record.revoked_at = grant.revoked_at
        record.revocation_reason = grant.revocation_reason

    def get_active_governor(
        self,
        subject_id: UUID,
    ) -> PlatformIdentityGovernorGrant | None:
        self._require_platform_scope()
        record = self._session.scalar(
            select(PlatformIdentityGovernorRecord).where(
                PlatformIdentityGovernorRecord.subject_id == subject_id,
                PlatformIdentityGovernorRecord.status == EntityStatus.ACTIVE.value,
            )
        )
        return self._to_governor_grant(record) if record is not None else None

    def list_active_governors(self) -> list[PlatformIdentityGovernorGrant]:
        self._require_platform_scope()
        return [
            self._to_governor_grant(record)
            for record in self._session.scalars(
                select(PlatformIdentityGovernorRecord).where(
                    PlatformIdentityGovernorRecord.status == EntityStatus.ACTIVE.value
                )
            ).all()
        ]

    def _visible_subjects(self) -> Select[tuple[SubjectRecord]]:
        statement = select(SubjectRecord)
        if not self._platform_scope:
            statement = statement.where(
                or_(
                    SubjectRecord.tenant_id == self._tenant_id,
                    SubjectRecord.tenant_id.is_(None),
                )
            )
        return statement

    def _require_write_scope(self, tenant_id: UUID | None) -> None:
        if self._platform_scope:
            return
        if tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.IDENTITY_CROSS_TENANT_FORBIDDEN,
                "identity write is outside repository tenant scope",
            )

    def _require_platform_scope(self) -> None:
        if not self._platform_scope:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "platform identity governor access requires platform scope",
            )

    def _to_subject(self, record: SubjectRecord) -> Subject:
        refs = self._session.scalars(
            select(SubjectExternalRefRecord).where(
                SubjectExternalRefRecord.subject_id == record.id
            )
        ).all()
        return Subject(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_type=SubjectKind(record.subject_type),
            display_name=record.display_name,
            status=EntityStatus(record.status),
            is_platform_managed=record.is_platform_managed,
            created_at=self._as_utc(record.created_at),
            updated_at=self._as_utc(record.updated_at),
            version=record.version,
            external_refs=[
                ExternalRef(system=ref.system, external_id=ref.external_id)
                for ref in refs
            ],
        )

    @classmethod
    def _to_ai_profile(
        cls,
        record: AIEmployeeProfileRecord,
    ) -> AIEmployeeProfile:
        return AIEmployeeProfile(
            ai_subject_id=record.ai_subject_id,
            capabilities_profile_ref=record.capabilities_profile_ref,
            owner_policy_ref=record.owner_policy_ref,
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_session(cls, record: SessionRecord) -> Session:
        return Session(
            id=record.id,
            subject_id=record.subject_id,
            tenant_id=record.tenant_id,
            created_at=cls._as_utc(record.created_at),
            expires_at=cls._as_utc(record.expires_at),
            credential_id=record.credential_id,
            revoked_at=cls._as_utc(record.revoked_at),
            correlation_id_at_issue=record.correlation_id_at_issue,
        )

    @classmethod
    def _to_assignment(cls, record: AIAssignmentRecord) -> AIAssignment:
        return AIAssignment(
            id=record.id,
            ai_subject_id=record.ai_subject_id,
            tenant_id=record.tenant_id,
            mode=AssignmentMode(record.mode),
            management_policy=record.management_policy,
            created_at=cls._as_utc(record.created_at),
            effective_from=cls._as_utc(record.effective_from),
            predecessor_assignment_id=record.predecessor_assignment_id,
            effective_to=cls._as_utc(record.effective_to),
            status=EntityStatus(record.status),
        )

    @classmethod
    def _to_governor_grant(
        cls,
        record: PlatformIdentityGovernorRecord,
    ) -> PlatformIdentityGovernorGrant:
        return PlatformIdentityGovernorGrant(
            id=record.id,
            subject_id=record.subject_id,
            granted_by_subject_id=record.granted_by_subject_id,
            granted_at=cls._as_utc(record.granted_at),
            status=EntityStatus(record.status),
            revoked_by_subject_id=record.revoked_by_subject_id,
            revoked_at=cls._as_utc(record.revoked_at),
            revocation_reason=record.revocation_reason,
        )

    @staticmethod
    @overload
    def _as_utc(value: datetime) -> datetime: ...

    @staticmethod
    @overload
    def _as_utc(value: None) -> None: ...

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
