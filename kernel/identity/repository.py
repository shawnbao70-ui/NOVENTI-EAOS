"""In-memory Identity repository (ADR-0010)."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from kernel.identity.models import (
    AIAssignment,
    AIEmployeeProfile,
    Credential,
    ExternalRef,
    PlatformIdentityGovernorGrant,
    Session,
    Subject,
)


@runtime_checkable
class IdentityRepository(Protocol):
    def add_subject(self, subject: Subject) -> None: ...

    def get_subject(self, subject_id: UUID) -> Optional[Subject]: ...

    def save_subject(self, subject: Subject) -> None: ...

    def add_ai_profile(self, profile: AIEmployeeProfile) -> None: ...

    def get_ai_profile(self, ai_subject_id: UUID) -> Optional[AIEmployeeProfile]: ...

    def save_ai_profile(self, profile: AIEmployeeProfile) -> None: ...

    def find_by_external_ref(self, ref: ExternalRef) -> Optional[Subject]: ...

    def add_credential(self, credential: Credential) -> None: ...

    def get_credential(self, credential_id: UUID) -> Optional[Credential]: ...

    def save_credential(self, credential: Credential) -> None: ...

    def add_session(self, session: Session) -> None: ...

    def get_session(self, session_id: UUID) -> Optional[Session]: ...

    def save_session(self, session: Session) -> None: ...

    def add_assignment(self, assignment: AIAssignment) -> None: ...

    def save_assignment(self, assignment: AIAssignment) -> None: ...

    def list_active_assignments(self, ai_subject_id: UUID) -> list[AIAssignment]: ...

    def add_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None: ...

    def save_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None: ...

    def get_active_governor(
        self,
        subject_id: UUID,
    ) -> Optional[PlatformIdentityGovernorGrant]: ...

    def list_active_governors(self) -> list[PlatformIdentityGovernorGrant]: ...


class InMemoryIdentityRepository:
    def __init__(self) -> None:
        self.subjects: dict[UUID, Subject] = {}
        self.ai_profiles: dict[UUID, AIEmployeeProfile] = {}
        self.credentials: dict[UUID, Credential] = {}
        self.sessions: dict[UUID, Session] = {}
        self.assignments: dict[UUID, AIAssignment] = {}
        self.governor_grants: dict[UUID, PlatformIdentityGovernorGrant] = {}
        self._external_index: dict[tuple[str, str], UUID] = {}

    def add_subject(self, subject: Subject) -> None:
        for ref in subject.external_refs:
            key = (ref.system, ref.external_id)
            if key in self._external_index:
                raise KeyError("duplicate external ref")
        self.subjects[subject.id] = subject
        for ref in subject.external_refs:
            self._external_index[(ref.system, ref.external_id)] = subject.id

    def get_subject(self, subject_id: UUID) -> Optional[Subject]:
        return self.subjects.get(subject_id)

    def save_subject(self, subject: Subject) -> None:
        self.subjects[subject.id] = subject

    def add_ai_profile(self, profile: AIEmployeeProfile) -> None:
        if profile.ai_subject_id in self.ai_profiles:
            raise KeyError("duplicate AI profile")
        self.ai_profiles[profile.ai_subject_id] = profile

    def get_ai_profile(self, ai_subject_id: UUID) -> Optional[AIEmployeeProfile]:
        return self.ai_profiles.get(ai_subject_id)

    def save_ai_profile(self, profile: AIEmployeeProfile) -> None:
        self.ai_profiles[profile.ai_subject_id] = profile

    def find_by_external_ref(self, ref: ExternalRef) -> Optional[Subject]:
        subject_id = self._external_index.get((ref.system, ref.external_id))
        if subject_id is None:
            return None
        return self.subjects.get(subject_id)

    def add_credential(self, credential: Credential) -> None:
        self.credentials[credential.id] = credential

    def get_credential(self, credential_id: UUID) -> Optional[Credential]:
        return self.credentials.get(credential_id)

    def save_credential(self, credential: Credential) -> None:
        self.credentials[credential.id] = credential

    def add_session(self, session: Session) -> None:
        self.sessions[session.id] = session

    def get_session(self, session_id: UUID) -> Optional[Session]:
        return self.sessions.get(session_id)

    def save_session(self, session: Session) -> None:
        self.sessions[session.id] = session

    def add_assignment(self, assignment: AIAssignment) -> None:
        self.assignments[assignment.id] = assignment

    def save_assignment(self, assignment: AIAssignment) -> None:
        self.assignments[assignment.id] = assignment

    def list_active_assignments(self, ai_subject_id: UUID) -> list[AIAssignment]:
        from kernel.identity.models import EntityStatus

        return [
            a
            for a in self.assignments.values()
            if a.ai_subject_id == ai_subject_id and a.status == EntityStatus.ACTIVE
        ]

    def add_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None:
        self.governor_grants[grant.id] = grant

    def save_governor_grant(self, grant: PlatformIdentityGovernorGrant) -> None:
        self.governor_grants[grant.id] = grant

    def get_active_governor(
        self,
        subject_id: UUID,
    ) -> Optional[PlatformIdentityGovernorGrant]:
        from kernel.identity.models import EntityStatus

        return next(
            (
                grant
                for grant in self.governor_grants.values()
                if grant.subject_id == subject_id
                and grant.status == EntityStatus.ACTIVE
            ),
            None,
        )

    def list_active_governors(self) -> list[PlatformIdentityGovernorGrant]:
        from kernel.identity.models import EntityStatus

        return [
            grant
            for grant in self.governor_grants.values()
            if grant.status == EntityStatus.ACTIVE
        ]
