"""Map KernelResult failures to HTTP problem responses."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

_NOT_FOUND = frozenset(
    {
        ErrorCode.IDENTITY_NOT_FOUND,
        ErrorCode.IDENTITY_SESSION_NOT_FOUND,
        ErrorCode.ORG_TENANT_NOT_FOUND,
        ErrorCode.ORG_ENTERPRISE_NOT_FOUND,
        ErrorCode.ORG_UNIT_NOT_FOUND,
        ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
        ErrorCode.COMMON_NOT_FOUND,
        ErrorCode.PERMISSION_GRANT_NOT_FOUND,
        ErrorCode.PERMISSION_POLICY_NOT_FOUND,
        ErrorCode.WORKFLOW_DEFINITION_NOT_FOUND,
        ErrorCode.WORKFLOW_INSTANCE_NOT_FOUND,
        ErrorCode.WORKFLOW_TASK_NOT_FOUND,
        ErrorCode.KNOWLEDGE_ENTITY_NOT_FOUND,
        ErrorCode.KNOWLEDGE_LINK_NOT_FOUND,
        ErrorCode.EVENT_NOT_FOUND,
        ErrorCode.EVENT_OUTBOX_NOT_FOUND,
        ErrorCode.EVENT_DEAD_LETTER_NOT_FOUND,
        ErrorCode.PACKAGE_NOT_FOUND,
        ErrorCode.PACKAGE_NOT_INSTALLED,
        ErrorCode.TWIN_NOT_FOUND,
        ErrorCode.BRAIN_NOT_FOUND,
        ErrorCode.MARKETPLACE_NOT_FOUND,
        ErrorCode.TERMINAL_EXTENSION_NOT_FOUND,
    }
)
_CONFLICT = frozenset(
    {
        ErrorCode.IDENTITY_DUPLICATE,
        ErrorCode.IDENTITY_GOVERNOR_CONFLICT,
        ErrorCode.COMMON_CONFLICT,
        ErrorCode.ORG_TENANT_DUPLICATE_NAME,
        ErrorCode.ORG_ENTERPRISE_DUPLICATE_NAME,
        ErrorCode.ORG_MEMBERSHIP_DUPLICATE,
        ErrorCode.ORG_VERSION_CONFLICT,
        ErrorCode.ORG_INVALID_STATE_TRANSITION,
        ErrorCode.ORG_ACTIVE_DEPENDENCIES,
        ErrorCode.ORG_UNIT_CYCLE_DETECTED,
        ErrorCode.PERMISSION_GRANT_CONFLICT,
        ErrorCode.PERMISSION_VERSION_CONFLICT,
        ErrorCode.PERMISSION_POLICY_CONFLICT,
        ErrorCode.PERMISSION_GRANT_REVOKED,
        ErrorCode.PERMISSION_POLICY_DEPRECATED,
        ErrorCode.WORKFLOW_DEFINITION_CONFLICT,
        ErrorCode.WORKFLOW_SIGNAL_CONFLICT,
        ErrorCode.WORKFLOW_VERSION_CONFLICT,
        ErrorCode.WORKFLOW_BUSINESS_KEY_CONFLICT,
        ErrorCode.WORKFLOW_INVALID_STATE,
        ErrorCode.KNOWLEDGE_ENTITY_CONFLICT,
        ErrorCode.KNOWLEDGE_VERSION_CONFLICT,
        ErrorCode.KNOWLEDGE_DERIVED_MISLABELLED,
        ErrorCode.KNOWLEDGE_LINK_INVALID,
        ErrorCode.EVENT_LEASE_CONFLICT,
        ErrorCode.EVENT_DELIVERY_FAILED,
        ErrorCode.PACKAGE_VERSION_CONFLICT,
        ErrorCode.PACKAGE_ACTION_AMBIGUOUS,
        ErrorCode.PACKAGE_ALREADY_INSTALLED,
        ErrorCode.PACKAGE_NOT_PUBLISHED,
        ErrorCode.MARKETPLACE_ALREADY_ACQUIRED,
        ErrorCode.MARKETPLACE_REVOKED,
        ErrorCode.MARKETPLACE_NOT_APPROVED,
        ErrorCode.MARKETPLACE_NOT_PUBLISHED,
        ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED,
        ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
        ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
        ErrorCode.MARKETPLACE_CAPABILITY_REQUIRED,
    }
)
_FORBIDDEN = frozenset(
    {
        ErrorCode.PERMISSION_DENIED,
        ErrorCode.IDENTITY_SECRET_LEAK_FORBIDDEN,
        ErrorCode.ORG_CROSS_TENANT_FORBIDDEN,
        ErrorCode.ORG_SUBJECT_INELIGIBLE,
        ErrorCode.ORG_UNIT_CROSS_TENANT,
        ErrorCode.PERMISSION_PRINCIPAL_INELIGIBLE,
        ErrorCode.PERMISSION_DELEGATION_FORBIDDEN,
        ErrorCode.PERMISSION_CROSS_TENANT_FORBIDDEN,
        ErrorCode.WORKFLOW_TASK_NOT_ASSIGNEE,
        ErrorCode.WORKFLOW_CANCEL_FORBIDDEN,
        ErrorCode.WORKFLOW_CROSS_TENANT_FORBIDDEN,
        ErrorCode.WORKFLOW_APPROVAL_REQUIRED,
        ErrorCode.WORKFLOW_APPROVAL_REJECTED,
        ErrorCode.KNOWLEDGE_CROSS_TENANT_FORBIDDEN,
        ErrorCode.KNOWLEDGE_SECRET_FORBIDDEN,
        ErrorCode.AI_KNOWLEDGE_DENIED,
        ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
        ErrorCode.TWIN_EXECUTION_FORBIDDEN,
        ErrorCode.TWIN_SECRET_DENIED,
        ErrorCode.BRAIN_EXECUTION_FORBIDDEN,
        ErrorCode.BRAIN_SECRET_DENIED,
        ErrorCode.BRAIN_ADVISORY_REQUIRED,
        ErrorCode.COMMERCIAL_HANDOFF_FORBIDDEN,
        ErrorCode.AI_RUNTIME_REQUIRED,
        ErrorCode.AI_TOOL_DENIED,
        ErrorCode.AI_APPROVAL_REQUIRED,
        ErrorCode.AI_COMMIT_FORBIDDEN,
        ErrorCode.AI_MEMORY_DENIED,
        ErrorCode.TERMINAL_DEVICE_UNTRUSTED,
        ErrorCode.TERMINAL_APPROVAL_INVALID,
        ErrorCode.TERMINAL_COMMIT_FORBIDDEN,
        ErrorCode.TERMINAL_SECRET_DENIED,
        ErrorCode.TERMINAL_EXTENSION_UNSIGNED,
        ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID,
        ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
        ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
        ErrorCode.TERMINAL_EXTENSION_REVOKED,
        ErrorCode.MARKETPLACE_COMMERCIAL_POLICY_REQUIRED,
    }
)
_GONE_OR_INVALID = frozenset(
    {
        ErrorCode.IDENTITY_SESSION_EXPIRED,
        ErrorCode.IDENTITY_SESSION_REVOKED,
        ErrorCode.IDENTITY_CREDENTIAL_INVALID,
        ErrorCode.IDENTITY_CREDENTIAL_REVOKED,
        ErrorCode.ORG_TENANT_SUSPENDED,
        ErrorCode.ORG_TENANT_CLOSED,
        ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE,
        ErrorCode.PERMISSION_GRANT_EXPIRED,
        ErrorCode.PERMISSION_CONDITION_UNRESOLVED,
        ErrorCode.WORKFLOW_APPROVAL_EXPIRED,
        ErrorCode.WORKFLOW_SIGNAL_UNKNOWN,
        ErrorCode.WORKFLOW_IDEMPOTENCY_REQUIRED,
        ErrorCode.KNOWLEDGE_ARCHIVED,
        ErrorCode.KNOWLEDGE_RETENTION_EXPIRED,
        ErrorCode.KNOWLEDGE_PROVENANCE_REQUIRED,
        ErrorCode.TERMINAL_STALE_PREVIEW,
    }
)


def raise_for_result(result: KernelResult[Any]) -> None:
    if result.ok:
        return
    code = result.error_code or ErrorCode.COMMON_INTERNAL
    if code in _NOT_FOUND:
        http_status = status.HTTP_404_NOT_FOUND
    elif code in _FORBIDDEN:
        http_status = status.HTTP_403_FORBIDDEN
    elif code in _CONFLICT:
        http_status = status.HTTP_409_CONFLICT
    elif code in _GONE_OR_INVALID:
        http_status = status.HTTP_409_CONFLICT
    elif code in {
        ErrorCode.COMMON_VALIDATION_FAILED,
        ErrorCode.IDENTITY_INVALID_TYPE,
        ErrorCode.ORG_TENANT_INVALID,
        ErrorCode.ORG_UNIT_PARENT_INVALID,
        ErrorCode.ORG_UNIT_ENTERPRISE_MISMATCH,
        ErrorCode.PERMISSION_SCOPE_INVALID,
        ErrorCode.WORKFLOW_DEFINITION_INVALID,
        ErrorCode.EVENT_ENVELOPE_INVALID,
        ErrorCode.EVENT_SUBSCRIPTION_INVALID,
        ErrorCode.PACKAGE_MANIFEST_INVALID,
        ErrorCode.PACKAGE_ACTION_UNDECLARED,
        ErrorCode.PACKAGE_SURFACE_UNDECLARED,
        ErrorCode.TWIN_PROVENANCE_REQUIRED,
        ErrorCode.TWIN_CONFIDENCE_INVALID,
        ErrorCode.BRAIN_PROVENANCE_REQUIRED,
        ErrorCode.BRAIN_CONFIDENCE_INVALID,
        ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
        ErrorCode.TERMINAL_EXTENSION_INVALID,
    }:
        http_status = status.HTTP_400_BAD_REQUEST
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    raise HTTPException(
        status_code=http_status,
        detail={
            "code": str(code.value if hasattr(code, "value") else code),
            "message": result.error_message or "request failed",
            "details": result.details,
        },
    )
