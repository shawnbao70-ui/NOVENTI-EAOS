"""Permission HTTP DTO mapping."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kernel.permission.models import Grant, PermissionDecision


from api.gateway.serializers.common import uuid_result as uuid_result


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_evaluate(decision: PermissionDecision, *, audit_id: UUID | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "decision_id": str(decision.id),
        "effect": decision.effect.value,
        "reason_code": decision.reason_code,
        "policy_version": decision.policy_version,
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_explanation(
    decision_id: UUID,
    payload: dict[str, str],
) -> dict[str, Any]:
    matched_grants = [
        item for item in payload.get("matched_grants", "").split(",") if item
    ]
    matched_policies = [
        item for item in payload.get("matched_policies", "").split(",") if item
    ]
    scope_trace = [
        item for item in payload.get("scope_trace", "").split("|") if item
    ]
    condition_outcomes = [
        item for item in payload.get("condition_outcomes", "").split("|") if item
    ]
    matched_roles = [
        item for item in payload.get("matched_roles", "").split(",") if item
    ]
    return {
        "decision_id": str(decision_id),
        "effect": payload["effect"],
        "reason_code": payload["reason_code"],
        "policy_version": payload["policy_version"],
        "matched_policy_ids": matched_policies,
        "matched_grant_ids": matched_grants,
        "matched_roles": matched_roles,
        "scope_trace": scope_trace,
        "condition_outcomes": condition_outcomes,
        "evidence_summary": (
            f"effect={payload['effect']};reason={payload['reason_code']}"
        ),
    }


def serialize_effective_grant(grant: Grant) -> dict[str, Any]:
    scope_ref: str | None = None
    if grant.org_unit_id is not None:
        scope_ref = str(grant.org_unit_id)
    elif grant.enterprise_id is not None:
        scope_ref = str(grant.enterprise_id)
    return {
        "grant_id": str(grant.id),
        "resource_type": grant.resource_type,
        "resource_id": str(grant.resource_id) if grant.resource_id else None,
        "scope_level": grant.scope_level.value,
        "scope_ref_id": scope_ref,
        "actions": sorted(grant.actions),
        "effect": "allow",
    }
