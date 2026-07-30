"""In-memory Permission repository for PHX-K08."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from kernel.permission.models import Grant, PermissionDecision, Policy


@runtime_checkable
class PermissionRepository(Protocol):
    def add_grant(self, grant: Grant) -> None: ...

    def get_grant(self, grant_id: UUID) -> Optional[Grant]: ...

    def save_grant(self, grant: Grant, *, expected_version: int) -> None: ...

    def list_grants(
        self,
        *,
        tenant_id: UUID,
        principal_subject_id: UUID | None = None,
    ) -> list[Grant]: ...

    def add_policy(self, policy: Policy) -> None: ...

    def get_policy(self, policy_id: UUID) -> Optional[Policy]: ...

    def save_policy(self, policy: Policy, *, expected_version: int) -> None: ...

    def list_policies(self, *, tenant_id: UUID) -> list[Policy]: ...

    def add_decision(self, decision: PermissionDecision) -> None: ...

    def get_decision(self, decision_id: UUID) -> Optional[PermissionDecision]: ...

    def list_decisions(self) -> list[PermissionDecision]: ...


class InMemoryPermissionRepository:
    def __init__(self) -> None:
        self.grants: dict[UUID, Grant] = {}
        self.policies: dict[UUID, Policy] = {}
        self.decisions: dict[UUID, PermissionDecision] = {}

    def add_grant(self, grant: Grant) -> None:
        self.grants[grant.id] = replace(grant)

    def get_grant(self, grant_id: UUID) -> Optional[Grant]:
        grant = self.grants.get(grant_id)
        return replace(grant) if grant is not None else None

    def save_grant(self, grant: Grant, *, expected_version: int) -> None:
        current = self.grants.get(grant.id)
        if current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(
                ErrorCode.PERMISSION_VERSION_CONFLICT,
                "grant version conflict",
            )
        self.grants[grant.id] = replace(grant)

    def list_grants(
        self,
        *,
        tenant_id: UUID,
        principal_subject_id: UUID | None = None,
    ) -> list[Grant]:
        return [
            replace(grant)
            for grant in self.grants.values()
            if grant.tenant_id == tenant_id
            and (
                principal_subject_id is None
                or grant.principal_subject_id == principal_subject_id
            )
        ]

    def add_policy(self, policy: Policy) -> None:
        self.policies[policy.id] = deepcopy(policy)

    def get_policy(self, policy_id: UUID) -> Optional[Policy]:
        policy = self.policies.get(policy_id)
        return deepcopy(policy) if policy is not None else None

    def save_policy(self, policy: Policy, *, expected_version: int) -> None:
        current = self.policies.get(policy.id)
        if current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(
                ErrorCode.PERMISSION_VERSION_CONFLICT,
                "policy version conflict",
            )
        self.policies[policy.id] = deepcopy(policy)

    def list_policies(self, *, tenant_id: UUID) -> list[Policy]:
        return [
            deepcopy(policy)
            for policy in self.policies.values()
            if policy.tenant_id == tenant_id
        ]

    def add_decision(self, decision: PermissionDecision) -> None:
        self.decisions[decision.id] = replace(decision)

    def get_decision(self, decision_id: UUID) -> Optional[PermissionDecision]:
        decision = self.decisions.get(decision_id)
        return replace(decision) if decision is not None else None

    def list_decisions(self) -> list[PermissionDecision]:
        return [replace(decision) for decision in self.decisions.values()]
