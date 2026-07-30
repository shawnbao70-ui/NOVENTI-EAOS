"""Identity-owned principal eligibility adapter for Permission."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence.identity_models import (
    AIAssignmentRecord,
    SubjectRecord,
)


class SQLAlchemyPrincipalEligibility:
    def __init__(self, session: Session) -> None:
        self._session = session

    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        subject = self._session.scalar(
            select(SubjectRecord).where(SubjectRecord.id == subject_id)
        )
        if subject is None or subject.status != "active":
            return False
        if subject.subject_type != SubjectKind.AI_EMPLOYEE.value:
            return subject.tenant_id == tenant_id
        assignment = self._session.scalar(
            select(AIAssignmentRecord.id).where(
                AIAssignmentRecord.ai_subject_id == subject_id,
                AIAssignmentRecord.tenant_id == tenant_id,
                AIAssignmentRecord.status == "active",
            )
        )
        return assignment is not None
