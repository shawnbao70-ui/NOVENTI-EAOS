"""Fail-closed ExecutionContext propagation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import UUID

from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError


@dataclass(frozen=True, slots=True)
class PropagationOverrides:
    tenant_id: UUID | None = None
    subject_id: UUID | None = None
    subject_type: SubjectType | None = None
    correlation_id: str | None = None
    platform_scope: bool | None = None
    package_id: str | None = None
    locale: str | None = None
    trace_id: str | None = None
    approval_ref: str | None = None


class ContextPropagator:
    @staticmethod
    def propagate(
        parent: ExecutionContext,
        *,
        overrides: PropagationOverrides | None = None,
    ) -> ExecutionContext:
        changes = overrides or PropagationOverrides()
        ContextPropagator._same("tenant_id", parent.tenant_id, changes.tenant_id)
        ContextPropagator._same("subject_id", parent.subject_id, changes.subject_id)
        ContextPropagator._same(
            "subject_type",
            parent.subject_type,
            changes.subject_type,
        )
        ContextPropagator._same(
            "correlation_id",
            parent.correlation_id,
            changes.correlation_id,
        )
        ContextPropagator._same(
            "platform_scope",
            parent.platform_scope,
            changes.platform_scope,
        )
        return replace(
            parent,
            package_id=ContextPropagator._supplement(
                "package_id",
                parent.package_id,
                changes.package_id,
            ),
            locale=ContextPropagator._supplement(
                "locale",
                parent.locale,
                changes.locale,
            ),
            trace_id=ContextPropagator._supplement(
                "trace_id",
                parent.trace_id,
                changes.trace_id,
            ),
            approval_ref=ContextPropagator._supplement(
                "approval_ref",
                parent.approval_ref,
                changes.approval_ref,
            ),
        )

    @staticmethod
    def _same(name: str, current: object, requested: object | None) -> None:
        if requested is not None and requested != current:
            raise KernelError(
                ErrorCode.RT_PROPAGATION_VIOLATION,
                f"{name} cannot change during propagation",
            )

    @staticmethod
    def _supplement(name: str, current: str | None, requested: str | None) -> str | None:
        if requested is None:
            return current
        normalized = requested.strip()
        if not normalized or (current is not None and normalized != current):
            raise KernelError(
                ErrorCode.RT_PROPAGATION_VIOLATION,
                f"{name} cannot be cleared or rebound during propagation",
            )
        return normalized
