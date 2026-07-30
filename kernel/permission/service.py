"""Permission Kernel service — PHX-K08 Policy / Scope / Delegation."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from kernel.permission.models import (
    SCOPE_RANK,
    DecisionEvidence,
    Grant,
    GrantStatus,
    PermissionDecision,
    PermissionEffect,
    Policy,
    PolicyRule,
    PolicyStatus,
    Resource,
    ScopeLevel,
)
from kernel.permission.ports import (
    ConditionEvaluator,
    PrincipalEligibility,
    RejectAllConditionEvaluator,
    RejectAllPrincipalEligibility,
    ScopeResolver,
    TenantOnlyScopeResolver,
)
from kernel.permission.role_grant_map import match_context_roles
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.permission.repository import InMemoryPermissionRepository, PermissionRepository
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult


class PermissionService:
    """Centralized, tenant-safe permission evaluation with default deny."""

    FOUNDATION_POLICY_VERSION = "foundation-0.1"

    def __init__(
        self,
        repository: PermissionRepository | None = None,
        audit_log: AuditLog | None = None,
        grant_administrators: set[UUID] | frozenset[UUID] | None = None,
        decision_auditors: set[UUID] | frozenset[UUID] | None = None,
        principal_eligibility: PrincipalEligibility | None = None,
        condition_evaluator: ConditionEvaluator | None = None,
        scope_resolver: ScopeResolver | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._repo = repository or InMemoryPermissionRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._grant_administrators = frozenset(grant_administrators or ())
        self._decision_auditors = frozenset(decision_auditors or ())
        self._principal_eligibility = (
            principal_eligibility or RejectAllPrincipalEligibility()
        )
        self._condition_evaluator = (
            condition_evaluator or RejectAllConditionEvaluator()
        )
        self._scope_resolver = scope_resolver or TenantOnlyScopeResolver()
        self._domain_events = domain_events

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    @property
    def POLICY_VERSION(self) -> str:
        return self.FOUNDATION_POLICY_VERSION

    def grant(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str,
        actions: set[str] | frozenset[str],
        resource_id: UUID | None = None,
        scope_level: ScopeLevel = ScopeLevel.RESOURCE,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        conditions_ref: str | None = None,
        expires_at: datetime | None = None,
        delegable: bool = False,
        remaining_depth: int = 0,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_grant_administrator(ctx)
            self._require_eligible_principal(principal_subject_id, ctx.tenant_id)
            normalized_actions = self._normalize_actions(actions)
            resource_type = resource_type.strip()
            if not resource_type or not normalized_actions:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "resource_type and at least one action are required",
                )
            if expires_at is not None and expires_at <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.PERMISSION_GRANT_EXPIRED,
                    "grant expiry must be in the future",
                )
            self._validate_scope_fields(
                scope_level=scope_level,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                resource_id=resource_id,
            )
            if remaining_depth < 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "remaining_depth must be non-negative",
                )
            for existing in self._repo.list_grants(
                tenant_id=ctx.tenant_id,
                principal_subject_id=principal_subject_id,
            ):
                if (
                    existing.status == GrantStatus.ACTIVE
                    and existing.resource_type == resource_type
                    and existing.resource_id == resource_id
                    and existing.scope_level == scope_level
                    and existing.enterprise_id == enterprise_id
                    and existing.org_unit_id == org_unit_id
                    and existing.actions == normalized_actions
                    and existing.parent_grant_id is None
                ):
                    raise KernelError(
                        ErrorCode.PERMISSION_GRANT_CONFLICT,
                        "equivalent active grant already exists",
                    )

            now = datetime.now(timezone.utc)
            grant = Grant(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                principal_subject_id=principal_subject_id,
                resource_type=resource_type,
                resource_id=resource_id,
                scope_level=scope_level,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                actions=normalized_actions,
                conditions_ref=conditions_ref,
                expires_at=expires_at,
                status=GrantStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                delegable=delegable,
                remaining_depth=remaining_depth if delegable else 0,
            )
            self._repo.add_grant(grant)
            audit = self._audit.record(
                ctx,
                action="Permission.Grant",
                resource=f"grant:{grant.id}",
                result="ok",
                details={"principal_subject_id": str(principal_subject_id)},
            )
            self._emit(
                ctx,
                event_name="permission.grant.created",
                payload={
                    "grant_id": str(grant.id),
                    "principal_subject_id": str(grant.principal_subject_id),
                    "version": grant.version,
                    "status": grant.status.value,
                },
            )
            return KernelResult.success(grant.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def grant_capability(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        capability: str,
        resource_type: str,
        actions: set[str] | frozenset[str],
        idempotency_key: str | None = None,
    ) -> KernelResult[UUID]:
        """Mint a tenant grant through the explicit PHX-G345 Cap→grant shell."""
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_grant_administrator(ctx)
            self._require_eligible_principal(principal_subject_id, ctx.tenant_id)
            cleaned_capability = capability.strip()
            cleaned_resource_type = resource_type.strip()
            normalized_actions = self._normalize_actions(actions)
            if not cleaned_capability or not cleaned_resource_type or not normalized_actions:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "capability, resource_type and at least one action are required",
                )

            # No separate Cap ledger is introduced: an idempotent retry resolves
            # only to the same real, tenant-scoped Kernel grant.
            if idempotency_key is not None:
                for existing in self._repo.list_grants(
                    tenant_id=ctx.tenant_id,
                    principal_subject_id=principal_subject_id,
                ):
                    if (
                        existing.status == GrantStatus.ACTIVE
                        and existing.resource_type == cleaned_resource_type
                        and existing.resource_id is None
                        and existing.scope_level == ScopeLevel.TENANT
                        and existing.enterprise_id is None
                        and existing.org_unit_id is None
                        and existing.actions == normalized_actions
                        and existing.parent_grant_id is None
                    ):
                        audit = self._audit.record(
                            ctx,
                            action="Permission.CapGrant.Create",
                            resource=f"grant:{existing.id}",
                            result="idempotent",
                            details={
                                "capability": cleaned_capability,
                                "principal_subject_id": str(principal_subject_id),
                                "idempotency_key": idempotency_key,
                            },
                        )
                        return KernelResult.success(existing.id, audit_id=audit.id)

            result = self.grant(
                ctx,
                principal_subject_id=principal_subject_id,
                resource_type=cleaned_resource_type,
                actions=normalized_actions,
                scope_level=ScopeLevel.TENANT,
            )
            if not result.ok or result.data is None:
                return result
            audit = self._audit.record(
                ctx,
                action="Permission.CapGrant.Create",
                resource=f"grant:{result.data}",
                result="ok",
                details={
                    "capability": cleaned_capability,
                    "principal_subject_id": str(principal_subject_id),
                    "idempotency_key": idempotency_key,
                },
            )
            return KernelResult.success(result.data, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke(
        self,
        ctx: ExecutionContext,
        *,
        grant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_grant_administrator(ctx)
            if not reason or not reason.strip():
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "reason is required",
                )
            grant = self._repo.get_grant(grant_id)
            if grant is None or grant.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.PERMISSION_GRANT_NOT_FOUND,
                    "grant not found",
                )
            if grant.status == GrantStatus.REVOKED:
                raise KernelError(
                    ErrorCode.PERMISSION_GRANT_REVOKED,
                    "grant is already revoked",
                )
            current_version = self._require_expected_version(expected_version)
            if grant.version != current_version:
                raise KernelError(
                    ErrorCode.PERMISSION_VERSION_CONFLICT,
                    "grant version conflict",
                )
            grant.status = GrantStatus.REVOKED
            grant.updated_at = datetime.now(timezone.utc)
            grant.version = current_version + 1
            self._repo.save_grant(grant, expected_version=current_version)
            audit = self._audit.record(
                ctx,
                action="Permission.Revoke",
                resource=f"grant:{grant.id}",
                result="ok",
                details={"reason": reason},
            )
            self._emit(
                ctx,
                event_name="permission.grant.revoked",
                payload={
                    "grant_id": str(grant.id),
                    "version": grant.version,
                    "status": grant.status.value,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke_capability(
        self,
        ctx: ExecutionContext,
        *,
        grant_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[bool]:
        """Revoke a real grant through the explicit PHX-G345 Cap→grant shell."""
        result = self.revoke(
            ctx,
            grant_id=grant_id,
            reason=reason,
            expected_version=expected_version,
        )
        if not result.ok:
            return result
        audit = self._audit.record(
            ctx,
            action="Permission.CapGrant.Revoke",
            resource=f"grant:{grant_id}",
            result="ok",
            details={"reason": reason},
        )
        return KernelResult.success(True, audit_id=audit.id)

    def list_tenant_grants(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID | None = None,
    ) -> KernelResult[list[Grant]]:
        """List tenant-visible grants for grant administrators only."""
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_grant_administrator(ctx)
            if principal_subject_id is not None:
                self._require_eligible_principal(principal_subject_id, ctx.tenant_id)
            return KernelResult.success(
                self._repo.list_grants(
                    tenant_id=ctx.tenant_id,
                    principal_subject_id=principal_subject_id,
                )
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_policy(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        policy_version: str,
        rules: list[PolicyRule],
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_grant_administrator(ctx)
            cleaned_name = name.strip()
            cleaned_version = policy_version.strip()
            if not cleaned_name or not cleaned_version:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "policy name and policy_version are required",
                )
            if not rules:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "policy requires at least one rule",
                )
            for rule in rules:
                self._validate_scope_fields(
                    scope_level=rule.scope_level,
                    enterprise_id=rule.enterprise_id,
                    org_unit_id=rule.org_unit_id,
                    resource_id=None,
                )
                if not rule.resource_type.strip() or not rule.actions:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "rule resource_type and actions are required",
                    )
            for existing in self._repo.list_policies(tenant_id=ctx.tenant_id):
                if (
                    existing.name.lower() == cleaned_name.lower()
                    and existing.policy_version == cleaned_version
                ):
                    raise KernelError(
                        ErrorCode.PERMISSION_POLICY_CONFLICT,
                        "policy name and version already exist",
                    )
            now = datetime.now(timezone.utc)
            policy = Policy(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                name=cleaned_name,
                policy_version=cleaned_version,
                status=PolicyStatus.DRAFT,
                rules=list(rules),
                created_at=now,
                updated_at=now,
            )
            self._repo.add_policy(policy)
            audit = self._audit.record(
                ctx,
                action="Permission.CreatePolicy",
                resource=f"policy:{policy.id}",
                result="ok",
            )
            return KernelResult.success(policy.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def activate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_grant_administrator(ctx)
            policy = self._require_policy(ctx, policy_id)
            if policy.status == PolicyStatus.DEPRECATED:
                raise KernelError(
                    ErrorCode.PERMISSION_POLICY_DEPRECATED,
                    "deprecated policy cannot be activated",
                )
            if policy.status == PolicyStatus.ACTIVE:
                return KernelResult.success(True)
            current_version = self._require_expected_version(expected_version)
            if policy.version != current_version:
                raise KernelError(
                    ErrorCode.PERMISSION_VERSION_CONFLICT,
                    "policy version conflict",
                )
            policy.status = PolicyStatus.ACTIVE
            policy.updated_at = datetime.now(timezone.utc)
            policy.version = current_version + 1
            self._repo.save_policy(policy, expected_version=current_version)
            audit = self._audit.record(
                ctx,
                action="Permission.ActivatePolicy",
                resource=f"policy:{policy.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="permission.policy.activated",
                payload={
                    "policy_id": str(policy.id),
                    "version": policy.version,
                    "status": policy.status.value,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def deprecate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_grant_administrator(ctx)
            policy = self._require_policy(ctx, policy_id)
            if policy.status == PolicyStatus.DEPRECATED:
                return KernelResult.success(True)
            current_version = self._require_expected_version(expected_version)
            if policy.version != current_version:
                raise KernelError(
                    ErrorCode.PERMISSION_VERSION_CONFLICT,
                    "policy version conflict",
                )
            policy.status = PolicyStatus.DEPRECATED
            policy.updated_at = datetime.now(timezone.utc)
            policy.version = current_version + 1
            self._repo.save_policy(policy, expected_version=current_version)
            audit = self._audit.record(
                ctx,
                action="Permission.DeprecatePolicy",
                resource=f"policy:{policy.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="permission.policy.deprecated",
                payload={
                    "policy_id": str(policy.id),
                    "version": policy.version,
                    "status": policy.status.value,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def delegate(
        self,
        ctx: ExecutionContext,
        *,
        parent_grant_id: UUID,
        to_principal_subject_id: UUID,
        actions: set[str] | frozenset[str] | None = None,
        scope_level: ScopeLevel | None = None,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        resource_id: UUID | None = None,
        expires_at: datetime | None = None,
        conditions_ref: str | None = None,
        remaining_depth: int | None = None,
        delegable: bool = False,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            parent = self._repo.get_grant(parent_grant_id)
            if parent is None or parent.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.PERMISSION_GRANT_NOT_FOUND,
                    "parent grant not found",
                )
            if parent.principal_subject_id != ctx.subject_id:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "only the grant principal may delegate",
                )
            if not self._grant_is_effective(parent, ctx=ctx, resource=None):
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "parent grant is not effective",
                )
            if not parent.delegable or parent.remaining_depth < 1:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "parent grant is not delegable",
                )
            self._require_eligible_principal(to_principal_subject_id, ctx.tenant_id)
            child_actions = (
                self._normalize_actions(actions)
                if actions is not None
                else parent.actions
            )
            if not child_actions.issubset(parent.actions):
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated actions must be a subset of parent actions",
                )
            child_scope = scope_level or parent.scope_level
            child_enterprise = (
                enterprise_id if enterprise_id is not None else parent.enterprise_id
            )
            child_unit = org_unit_id if org_unit_id is not None else parent.org_unit_id
            child_resource = resource_id if resource_id is not None else parent.resource_id
            self._validate_scope_fields(
                scope_level=child_scope,
                enterprise_id=child_enterprise,
                org_unit_id=child_unit,
                resource_id=child_resource,
            )
            if SCOPE_RANK[child_scope] > SCOPE_RANK[parent.scope_level]:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated scope cannot be broader than parent",
                )
            if (
                parent.enterprise_id is not None
                and child_enterprise != parent.enterprise_id
            ):
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated enterprise scope cannot expand",
                )
            if parent.org_unit_id is not None and child_unit != parent.org_unit_id:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated org-unit scope cannot expand",
                )
            if parent.resource_id is not None and child_resource != parent.resource_id:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated resource scope cannot expand",
                )
            child_expiry = expires_at
            if child_expiry is None:
                child_expiry = parent.expires_at
            elif parent.expires_at is not None and child_expiry > parent.expires_at:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated expiry cannot exceed parent",
                )
            if child_expiry is not None and child_expiry <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.PERMISSION_GRANT_EXPIRED,
                    "delegated expiry must be in the future",
                )
            child_depth = (
                remaining_depth
                if remaining_depth is not None
                else parent.remaining_depth - 1
            )
            if child_depth < 0 or child_depth >= parent.remaining_depth:
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegated remaining_depth must decrease",
                )
            if not delegable:
                child_depth = 0
            child_condition = conditions_ref or parent.conditions_ref
            if self._delegation_cycle(parent.id, to_principal_subject_id):
                raise KernelError(
                    ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
                    "delegation cycle is forbidden",
                )
            now = datetime.now(timezone.utc)
            child = Grant(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                principal_subject_id=to_principal_subject_id,
                resource_type=parent.resource_type,
                resource_id=child_resource,
                scope_level=child_scope,
                enterprise_id=child_enterprise,
                org_unit_id=child_unit,
                actions=child_actions,
                conditions_ref=child_condition,
                expires_at=child_expiry,
                status=GrantStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                parent_grant_id=parent.id,
                delegator_subject_id=ctx.subject_id,
                remaining_depth=child_depth,
                delegable=delegable and child_depth > 0,
            )
            self._repo.add_grant(child)
            audit = self._audit.record(
                ctx,
                action="Permission.Delegate",
                resource=f"grant:{child.id}",
                result="ok",
                details={
                    "parent_grant_id": str(parent.id),
                    "to_principal_subject_id": str(to_principal_subject_id),
                },
            )
            self._emit(
                ctx,
                event_name="permission.grant.delegated",
                payload={
                    "grant_id": str(child.id),
                    "parent_grant_id": str(parent.id),
                    "principal_subject_id": str(child.principal_subject_id),
                    "version": child.version,
                    "status": child.status.value,
                },
            )
            return KernelResult.success(child.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult[PermissionDecision]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if resource.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.PERMISSION_CROSS_TENANT_FORBIDDEN,
                    "cross-tenant permission evaluation is forbidden",
                )
            self._require_eligible_principal(principal_subject_id, ctx.tenant_id)
            normalized_action = action.strip().lower()
            if not normalized_action or not resource.resource_type.strip():
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "action and resource_type are required",
                )

            evidence = DecisionEvidence()
            deny_hit = False
            allow_hit = False
            expired_match = False
            unresolved_condition = False
            policy_versions: list[str] = []

            for grant in self._repo.list_grants(
                tenant_id=ctx.tenant_id,
                principal_subject_id=principal_subject_id,
            ):
                match = self._match_grant(
                    grant,
                    ctx=ctx,
                    action=normalized_action,
                    resource=resource,
                    evidence=evidence,
                )
                if match == "expired":
                    expired_match = True
                elif match == "unresolved":
                    unresolved_condition = True
                elif match == "allow":
                    allow_hit = True
                    evidence.matched_grant_ids.append(grant.id)

            for policy in self._repo.list_policies(tenant_id=ctx.tenant_id):
                if policy.status != PolicyStatus.ACTIVE:
                    continue
                for rule in policy.rules:
                    match = self._match_rule(
                        rule,
                        ctx=ctx,
                        action=normalized_action,
                        resource=resource,
                        evidence=evidence,
                    )
                    if match == "deny":
                        deny_hit = True
                        evidence.matched_policy_ids.append(policy.id)
                        evidence.matched_rule_ids.append(rule.id)
                        policy_versions.append(policy.policy_version)
                    elif match == "allow":
                        allow_hit = True
                        evidence.matched_policy_ids.append(policy.id)
                        evidence.matched_rule_ids.append(rule.id)
                        policy_versions.append(policy.policy_version)
                    elif match == "unresolved":
                        unresolved_condition = True

            role_hits = match_context_roles(
                roles=ctx.roles,
                resource_type=resource.resource_type,
                action=normalized_action,
            )
            if role_hits:
                allow_hit = True
                evidence.matched_roles.extend(role_hits)

            grant_or_policy_allow = bool(
                evidence.matched_grant_ids or evidence.matched_policy_ids
            )

            if deny_hit:
                effect = PermissionEffect.DENY
                reason_code = ErrorCode.PERMISSION_DENIED.value
            elif allow_hit:
                effect = PermissionEffect.ALLOW
                if grant_or_policy_allow:
                    reason_code = "MATCHED_ACTIVE_GRANT"
                elif evidence.matched_roles:
                    reason_code = "MATCHED_CONTEXT_ROLE"
                else:
                    reason_code = "MATCHED_ACTIVE_GRANT"
            elif expired_match:
                effect = PermissionEffect.DENY
                reason_code = ErrorCode.PERMISSION_GRANT_EXPIRED.value
            elif unresolved_condition:
                effect = PermissionEffect.DENY
                reason_code = ErrorCode.PERMISSION_CONDITION_UNRESOLVED.value
            else:
                effect = PermissionEffect.DENY
                reason_code = ErrorCode.PERMISSION_DENIED.value

            now = datetime.now(timezone.utc)
            decision = PermissionDecision(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                principal_subject_id=principal_subject_id,
                action=normalized_action,
                resource_type=resource.resource_type,
                resource_id=resource.resource_id,
                effect=effect,
                reason_code=reason_code,
                policy_version=(
                    ",".join(dict.fromkeys(policy_versions))
                    if policy_versions
                    else self.FOUNDATION_POLICY_VERSION
                ),
                correlation_id=ctx.correlation_id,
                decided_at=now,
                evidence=evidence,
            )
            self._repo.add_decision(decision)
            audit = self._audit.record(
                ctx,
                action="Permission.Evaluate",
                resource=(
                    f"{resource.resource_type}:"
                    f"{resource.resource_id if resource.resource_id else '*'}"
                ),
                result=effect.value,
                details={
                    "decision_id": str(decision.id),
                    "reason_code": reason_code,
                },
            )
            self._emit(
                ctx,
                event_name="permission.decision.recorded",
                payload={
                    "decision_id": str(decision.id),
                    "principal_subject_id": str(decision.principal_subject_id),
                    "action": decision.action,
                    "resource_type": decision.resource_type,
                    "resource_id": (
                        str(decision.resource_id)
                        if decision.resource_id is not None
                        else None
                    ),
                    "effect": decision.effect.value,
                    "reason_code": decision.reason_code,
                    "policy_version": decision.policy_version,
                    "matched_grant_ids": [
                        str(item) for item in evidence.matched_grant_ids
                    ],
                    "matched_policy_ids": [
                        str(item) for item in evidence.matched_policy_ids
                    ],
                    "matched_roles": list(evidence.matched_roles),
                },
            )
            return KernelResult.success(decision, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def explain(
        self,
        ctx: ExecutionContext,
        *,
        decision_id: UUID,
    ) -> KernelResult[dict[str, str]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            decision = self._repo.get_decision(decision_id)
            if decision is None or decision.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "decision not found")
            if (
                ctx.subject_id != decision.principal_subject_id
                and ctx.subject_id not in self._decision_auditors
            ):
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "decision explanation is not visible to caller",
                )
            payload = {
                "effect": decision.effect.value,
                "reason_code": decision.reason_code,
                "policy_version": decision.policy_version,
            }
            if decision.evidence is not None:
                if decision.evidence.matched_grant_ids:
                    payload["matched_grants"] = ",".join(
                        str(item) for item in decision.evidence.matched_grant_ids
                    )
                if decision.evidence.matched_policy_ids:
                    payload["matched_policies"] = ",".join(
                        str(item) for item in decision.evidence.matched_policy_ids
                    )
                if decision.evidence.matched_rule_ids:
                    payload["matched_rules"] = ",".join(
                        str(item) for item in decision.evidence.matched_rule_ids
                    )
                if decision.evidence.scope_trace:
                    payload["scope_trace"] = "|".join(decision.evidence.scope_trace)
                if decision.evidence.condition_outcomes:
                    payload["condition_outcomes"] = "|".join(
                        decision.evidence.condition_outcomes
                    )
                if decision.evidence.matched_roles:
                    payload["matched_roles"] = ",".join(
                        decision.evidence.matched_roles
                    )
            return KernelResult.success(payload)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_effective(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str | None = None,
    ) -> KernelResult[list[Grant]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if (
                ctx.subject_id != principal_subject_id
                and ctx.subject_id not in self._decision_auditors
            ):
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "effective permissions are not visible to caller",
                )
            self._require_eligible_principal(principal_subject_id, ctx.tenant_id)
            effective: list[Grant] = []
            for grant in self._repo.list_grants(
                tenant_id=ctx.tenant_id,
                principal_subject_id=principal_subject_id,
            ):
                if resource_type is not None and grant.resource_type != resource_type:
                    continue
                probe = Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type=grant.resource_type,
                    resource_id=grant.resource_id,
                    enterprise_id=grant.enterprise_id,
                    org_unit_id=grant.org_unit_id,
                )
                if self._grant_is_effective(grant, ctx=ctx, resource=probe):
                    effective.append(grant)
            return KernelResult.success(effective)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_grant_administrator(self, ctx: ExecutionContext) -> None:
        if ctx.subject_id not in self._grant_administrators:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "grant administration authority is required",
            )

    def _emit(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        payload: dict[str, object],
        tenant_id: UUID | None = None,
    ) -> None:
        if self._domain_events is None:
            return
        self._domain_events.enqueue_fact(
            ctx,
            event_name=event_name,
            producer="permission.kernel",
            payload=payload,
            tenant_id=tenant_id,
        )

    def _require_eligible_principal(self, subject_id: UUID, tenant_id: UUID) -> None:
        if not self._principal_eligibility.is_eligible(
            subject_id=subject_id,
            tenant_id=tenant_id,
        ):
            raise KernelError(
                ErrorCode.PERMISSION_PRINCIPAL_INELIGIBLE,
                "principal is not eligible in tenant",
            )

    def _require_policy(self, ctx: ExecutionContext, policy_id: UUID) -> Policy:
        policy = self._repo.get_policy(policy_id)
        if policy is None or policy.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.PERMISSION_POLICY_NOT_FOUND,
                "policy not found",
            )
        return policy

    def _match_grant(
        self,
        grant: Grant,
        *,
        ctx: ExecutionContext,
        action: str,
        resource: Resource,
        evidence: DecisionEvidence,
    ) -> str | None:
        if grant.status != GrantStatus.ACTIVE:
            return None
        if grant.resource_type != resource.resource_type:
            return None
        if action not in grant.actions:
            return None
        if not self._scope_covers(grant, resource=resource, evidence=evidence):
            return None
        if not self._parent_chain_effective(grant, ctx=ctx, resource=resource):
            return None
        now = datetime.now(timezone.utc)
        if grant.expires_at is not None and grant.expires_at <= now:
            return "expired"
        if grant.conditions_ref is not None:
            ok = self._condition_evaluator.evaluate(
                condition_ref=grant.conditions_ref,
                ctx=ctx,
                principal_subject_id=grant.principal_subject_id,
                action=action,
                resource=resource,
            )
            evidence.condition_outcomes.append(
                f"grant:{grant.id}:{grant.conditions_ref}:{'true' if ok else 'false'}"
            )
            if not ok:
                return "unresolved"
        return "allow"

    def _match_rule(
        self,
        rule: PolicyRule,
        *,
        ctx: ExecutionContext,
        action: str,
        resource: Resource,
        evidence: DecisionEvidence,
    ) -> str | None:
        if rule.resource_type != resource.resource_type:
            return None
        if action not in {item.strip().lower() for item in rule.actions}:
            return None
        if not self._scope_resolver.covers(
            tenant_id=resource.tenant_id,
            scope_level=rule.scope_level,
            enterprise_id=rule.enterprise_id,
            org_unit_id=rule.org_unit_id,
            resource=resource,
        ):
            return None
        evidence.scope_trace.append(
            f"rule:{rule.id}:{rule.scope_level.value}:cover"
        )
        if rule.conditions_ref is not None:
            ok = self._condition_evaluator.evaluate(
                condition_ref=rule.conditions_ref,
                ctx=ctx,
                principal_subject_id=ctx.subject_id,
                action=action,
                resource=resource,
            )
            evidence.condition_outcomes.append(
                f"rule:{rule.id}:{rule.conditions_ref}:{'true' if ok else 'false'}"
            )
            if not ok:
                return "unresolved"
        return rule.effect.value

    def _scope_covers(
        self,
        grant: Grant,
        *,
        resource: Resource,
        evidence: DecisionEvidence,
    ) -> bool:
        if grant.scope_level == ScopeLevel.RESOURCE:
            if grant.resource_id is not None and grant.resource_id != resource.resource_id:
                return False
            evidence.scope_trace.append(f"grant:{grant.id}:resource:cover")
            return True
        covered = self._scope_resolver.covers(
            tenant_id=grant.tenant_id,
            scope_level=grant.scope_level,
            enterprise_id=grant.enterprise_id,
            org_unit_id=grant.org_unit_id,
            resource=resource,
        )
        evidence.scope_trace.append(
            f"grant:{grant.id}:{grant.scope_level.value}:"
            f"{'cover' if covered else 'miss'}"
        )
        return covered

    def _grant_is_effective(
        self,
        grant: Grant,
        *,
        ctx: ExecutionContext,
        resource: Resource | None,
    ) -> bool:
        if grant.status != GrantStatus.ACTIVE:
            return False
        now = datetime.now(timezone.utc)
        if grant.expires_at is not None and grant.expires_at <= now:
            return False
        if not self._parent_chain_effective(grant, ctx=ctx, resource=resource):
            return False
        if grant.conditions_ref is None:
            return True
        probe = resource or Resource(
            tenant_id=grant.tenant_id,
            resource_type=grant.resource_type,
            resource_id=grant.resource_id,
            enterprise_id=grant.enterprise_id,
            org_unit_id=grant.org_unit_id,
        )
        return self._condition_evaluator.evaluate(
            condition_ref=grant.conditions_ref,
            ctx=ctx,
            principal_subject_id=grant.principal_subject_id,
            action="*",
            resource=probe,
        )

    def _parent_chain_effective(
        self,
        grant: Grant,
        *,
        ctx: ExecutionContext,
        resource: Resource | None,
    ) -> bool:
        seen: set[UUID] = set()
        current: Grant | None = grant
        while current is not None and current.parent_grant_id is not None:
            if current.parent_grant_id in seen:
                return False
            seen.add(current.parent_grant_id)
            parent = self._repo.get_grant(current.parent_grant_id)
            if parent is None or parent.tenant_id != grant.tenant_id:
                return False
            if parent.status != GrantStatus.ACTIVE:
                return False
            now = datetime.now(timezone.utc)
            if parent.expires_at is not None and parent.expires_at <= now:
                return False
            if not self._principal_eligibility.is_eligible(
                subject_id=parent.principal_subject_id,
                tenant_id=parent.tenant_id,
            ):
                return False
            if parent.conditions_ref is not None:
                probe = resource or Resource(
                    tenant_id=parent.tenant_id,
                    resource_type=parent.resource_type,
                    resource_id=parent.resource_id,
                    enterprise_id=parent.enterprise_id,
                    org_unit_id=parent.org_unit_id,
                )
                if not self._condition_evaluator.evaluate(
                    condition_ref=parent.conditions_ref,
                    ctx=ctx,
                    principal_subject_id=parent.principal_subject_id,
                    action="*",
                    resource=probe,
                ):
                    return False
            current = parent
        return True

    def _delegation_cycle(self, parent_grant_id: UUID, to_principal: UUID) -> bool:
        current = self._repo.get_grant(parent_grant_id)
        while current is not None:
            if current.principal_subject_id == to_principal:
                return True
            if current.parent_grant_id is None:
                break
            current = self._repo.get_grant(current.parent_grant_id)
        return False

    @staticmethod
    def _normalize_actions(actions: set[str] | frozenset[str]) -> frozenset[str]:
        return frozenset(action.strip().lower() for action in actions if action.strip())

    @staticmethod
    def _validate_scope_fields(
        *,
        scope_level: ScopeLevel,
        enterprise_id: UUID | None,
        org_unit_id: UUID | None,
        resource_id: UUID | None,
    ) -> None:
        if scope_level == ScopeLevel.TENANT:
            if enterprise_id is not None or org_unit_id is not None:
                raise KernelError(
                    ErrorCode.PERMISSION_SCOPE_INVALID,
                    "tenant scope cannot bind enterprise or org unit",
                )
        elif scope_level == ScopeLevel.ENTERPRISE:
            if enterprise_id is None or org_unit_id is not None:
                raise KernelError(
                    ErrorCode.PERMISSION_SCOPE_INVALID,
                    "enterprise scope requires enterprise_id only",
                )
        elif scope_level == ScopeLevel.ORG_UNIT:
            if enterprise_id is None or org_unit_id is None:
                raise KernelError(
                    ErrorCode.PERMISSION_SCOPE_INVALID,
                    "org unit scope requires enterprise_id and org_unit_id",
                )
        elif scope_level == ScopeLevel.RESOURCE:
            del resource_id
        else:
            raise KernelError(
                ErrorCode.PERMISSION_SCOPE_INVALID,
                "unknown scope level",
            )

    @staticmethod
    def _require_expected_version(expected_version: int | None) -> int:
        if expected_version is None or expected_version < 1:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "expected_version must be a positive integer",
            )
        return expected_version
