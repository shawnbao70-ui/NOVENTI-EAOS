"""Tenant-bound SQLAlchemy adapter for Permission Repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import overload
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.permission_models import (
    GrantRecord,
    PermissionDecisionRecord,
    PolicyRecord,
    PolicyRuleRecord,
)
from kernel.permission.models import (
    DecisionEvidence,
    Grant,
    GrantStatus,
    PermissionDecision,
    PermissionEffect,
    Policy,
    PolicyRule,
    PolicyStatus,
    ScopeLevel,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyPermissionRepository:
    def __init__(
        self,
        session: Session,
        *,
        tenant_id: UUID | None,
        platform_scope: bool = False,
    ) -> None:
        if platform_scope == (tenant_id is not None):
            raise ValueError("provide either tenant_id or platform_scope")
        self._session = session
        self._tenant_id = tenant_id
        self._platform_scope = platform_scope

    def add_grant(self, grant: Grant) -> None:
        self._require_tenant_scope(grant.tenant_id)
        self._session.add(
            GrantRecord(
                id=grant.id,
                tenant_id=grant.tenant_id,
                principal_subject_id=grant.principal_subject_id,
                resource_type=grant.resource_type,
                resource_id=grant.resource_id,
                scope_level=grant.scope_level.value,
                enterprise_id=grant.enterprise_id,
                org_unit_id=grant.org_unit_id,
                actions=sorted(grant.actions),
                conditions_ref=grant.conditions_ref,
                expires_at=grant.expires_at,
                parent_grant_id=grant.parent_grant_id,
                delegator_subject_id=grant.delegator_subject_id,
                remaining_depth=grant.remaining_depth,
                delegable=grant.delegable,
                status=grant.status.value,
                created_at=grant.created_at,
                updated_at=grant.updated_at,
                version=grant.version,
            )
        )

    def get_grant(self, grant_id: UUID) -> Grant | None:
        record = self._session.scalar(
            self._scoped_grants().where(GrantRecord.id == grant_id)
        )
        return self._to_grant(record) if record is not None else None

    def save_grant(self, grant: Grant, *, expected_version: int) -> None:
        self._require_tenant_scope(grant.tenant_id)
        result = self._session.execute(
            update(GrantRecord)
            .where(
                GrantRecord.id == grant.id,
                GrantRecord.tenant_id == grant.tenant_id,
                GrantRecord.version == expected_version,
            )
            .values(
                actions=sorted(grant.actions),
                conditions_ref=grant.conditions_ref,
                expires_at=grant.expires_at,
                scope_level=grant.scope_level.value,
                enterprise_id=grant.enterprise_id,
                org_unit_id=grant.org_unit_id,
                parent_grant_id=grant.parent_grant_id,
                delegator_subject_id=grant.delegator_subject_id,
                remaining_depth=grant.remaining_depth,
                delegable=grant.delegable,
                status=grant.status.value,
                updated_at=grant.updated_at,
                version=grant.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.PERMISSION_VERSION_CONFLICT,
                "grant version conflict",
            )

    def list_grants(
        self,
        *,
        tenant_id: UUID,
        principal_subject_id: UUID | None = None,
    ) -> list[Grant]:
        self._require_tenant_scope(tenant_id)
        statement = select(GrantRecord).where(GrantRecord.tenant_id == tenant_id)
        if principal_subject_id is not None:
            statement = statement.where(
                GrantRecord.principal_subject_id == principal_subject_id
            )
        return [self._to_grant(record) for record in self._session.scalars(statement)]

    def add_policy(self, policy: Policy) -> None:
        self._require_tenant_scope(policy.tenant_id)
        self._session.add(
            PolicyRecord(
                id=policy.id,
                tenant_id=policy.tenant_id,
                name=policy.name,
                policy_version=policy.policy_version,
                status=policy.status.value,
                created_at=policy.created_at,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        for rule in policy.rules:
            self._session.add(
                PolicyRuleRecord(
                    id=rule.id,
                    policy_id=policy.id,
                    effect=rule.effect.value,
                    resource_type=rule.resource_type,
                    actions=sorted(rule.actions),
                    scope_level=rule.scope_level.value,
                    enterprise_id=rule.enterprise_id,
                    org_unit_id=rule.org_unit_id,
                    conditions_ref=rule.conditions_ref,
                )
            )

    def get_policy(self, policy_id: UUID) -> Policy | None:
        record = self._session.scalar(
            self._scoped_policies().where(PolicyRecord.id == policy_id)
        )
        if record is None:
            return None
        return self._to_policy(record)

    def save_policy(self, policy: Policy, *, expected_version: int) -> None:
        self._require_tenant_scope(policy.tenant_id)
        result = self._session.execute(
            update(PolicyRecord)
            .where(
                PolicyRecord.id == policy.id,
                PolicyRecord.tenant_id == policy.tenant_id,
                PolicyRecord.version == expected_version,
            )
            .values(
                status=policy.status.value,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.PERMISSION_VERSION_CONFLICT,
                "policy version conflict",
            )
        self._session.execute(
            delete(PolicyRuleRecord).where(PolicyRuleRecord.policy_id == policy.id)
        )
        for rule in policy.rules:
            self._session.add(
                PolicyRuleRecord(
                    id=rule.id,
                    policy_id=policy.id,
                    effect=rule.effect.value,
                    resource_type=rule.resource_type,
                    actions=sorted(rule.actions),
                    scope_level=rule.scope_level.value,
                    enterprise_id=rule.enterprise_id,
                    org_unit_id=rule.org_unit_id,
                    conditions_ref=rule.conditions_ref,
                )
            )

    def list_policies(self, *, tenant_id: UUID) -> list[Policy]:
        self._require_tenant_scope(tenant_id)
        statement = select(PolicyRecord).where(PolicyRecord.tenant_id == tenant_id)
        return [self._to_policy(record) for record in self._session.scalars(statement)]

    def add_decision(self, decision: PermissionDecision) -> None:
        self._require_tenant_scope(decision.tenant_id)
        evidence = None
        if decision.evidence is not None:
            evidence = {
                "matched_grant_ids": [
                    str(item) for item in decision.evidence.matched_grant_ids
                ],
                "matched_policy_ids": [
                    str(item) for item in decision.evidence.matched_policy_ids
                ],
                "matched_rule_ids": [
                    str(item) for item in decision.evidence.matched_rule_ids
                ],
                "scope_trace": list(decision.evidence.scope_trace),
                "condition_outcomes": list(decision.evidence.condition_outcomes),
                "matched_roles": list(decision.evidence.matched_roles),
            }
        self._session.add(
            PermissionDecisionRecord(
                id=decision.id,
                tenant_id=decision.tenant_id,
                principal_subject_id=decision.principal_subject_id,
                action=decision.action,
                resource_type=decision.resource_type,
                resource_id=decision.resource_id,
                effect=decision.effect.value,
                reason_code=decision.reason_code,
                policy_version=decision.policy_version,
                correlation_id=decision.correlation_id,
                decided_at=decision.decided_at,
                evidence_json=evidence,
            )
        )

    def get_decision(self, decision_id: UUID) -> PermissionDecision | None:
        record = self._session.scalar(
            self._scoped_decisions().where(PermissionDecisionRecord.id == decision_id)
        )
        return self._to_decision(record) if record is not None else None

    def list_decisions(self) -> list[PermissionDecision]:
        return [
            self._to_decision(record)
            for record in self._session.scalars(self._scoped_decisions())
        ]

    def _scoped_grants(self):
        statement = select(GrantRecord)
        if not self._platform_scope:
            statement = statement.where(GrantRecord.tenant_id == self._tenant_id)
        return statement

    def _scoped_policies(self):
        statement = select(PolicyRecord)
        if not self._platform_scope:
            statement = statement.where(PolicyRecord.tenant_id == self._tenant_id)
        return statement

    def _scoped_decisions(self):
        statement = select(PermissionDecisionRecord)
        if not self._platform_scope:
            statement = statement.where(
                PermissionDecisionRecord.tenant_id == self._tenant_id
            )
        return statement

    def _require_tenant_scope(self, tenant_id: UUID) -> None:
        if not self._platform_scope and tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.PERMISSION_CROSS_TENANT_FORBIDDEN,
                "permission operation is outside repository tenant scope",
            )

    def _to_policy(self, record: PolicyRecord) -> Policy:
        rules = [
            PolicyRule(
                id=rule.id,
                effect=PermissionEffect(rule.effect),
                resource_type=rule.resource_type,
                actions=frozenset(rule.actions),
                scope_level=ScopeLevel(rule.scope_level),
                enterprise_id=rule.enterprise_id,
                org_unit_id=rule.org_unit_id,
                conditions_ref=rule.conditions_ref,
            )
            for rule in self._session.scalars(
                select(PolicyRuleRecord).where(PolicyRuleRecord.policy_id == record.id)
            )
        ]
        return Policy(
            id=record.id,
            tenant_id=record.tenant_id,
            name=record.name,
            policy_version=record.policy_version,
            status=PolicyStatus(record.status),
            rules=rules,
            created_at=self._as_utc(record.created_at),
            updated_at=self._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_grant(cls, record: GrantRecord) -> Grant:
        return Grant(
            id=record.id,
            tenant_id=record.tenant_id,
            principal_subject_id=record.principal_subject_id,
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            scope_level=ScopeLevel(record.scope_level),
            enterprise_id=record.enterprise_id,
            org_unit_id=record.org_unit_id,
            actions=frozenset(record.actions),
            conditions_ref=record.conditions_ref,
            expires_at=cls._as_utc(record.expires_at),
            parent_grant_id=record.parent_grant_id,
            delegator_subject_id=record.delegator_subject_id,
            remaining_depth=record.remaining_depth,
            delegable=record.delegable,
            status=GrantStatus(record.status),
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_decision(cls, record: PermissionDecisionRecord) -> PermissionDecision:
        evidence = None
        if record.evidence_json:
            raw = record.evidence_json
            evidence = DecisionEvidence(
                matched_grant_ids=[UUID(item) for item in raw.get("matched_grant_ids", [])],
                matched_policy_ids=[
                    UUID(item) for item in raw.get("matched_policy_ids", [])
                ],
                matched_rule_ids=[UUID(item) for item in raw.get("matched_rule_ids", [])],
                scope_trace=list(raw.get("scope_trace", [])),
                condition_outcomes=list(raw.get("condition_outcomes", [])),
                matched_roles=[
                    str(item) for item in raw.get("matched_roles", []) if str(item)
                ],
            )
        return PermissionDecision(
            id=record.id,
            tenant_id=record.tenant_id,
            principal_subject_id=record.principal_subject_id,
            action=record.action,
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            effect=PermissionEffect(record.effect),
            reason_code=record.reason_code,
            policy_version=record.policy_version,
            correlation_id=record.correlation_id,
            decided_at=cls._as_utc(record.decided_at),
            evidence=evidence,
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
