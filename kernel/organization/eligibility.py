"""Identity-owned eligibility port for Organization memberships."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class MembershipEligibility(Protocol):
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool: ...


class RejectAllMembershipEligibility:
    """Fail-closed default used when Identity is not composed."""

    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return False
