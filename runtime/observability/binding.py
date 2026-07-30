"""Allowlisted observability fields derived from ExecutionContext."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.shared.context import ExecutionContext


@dataclass(frozen=True, slots=True)
class ObservabilityBinding:
    correlation_id: str
    subject_id: str
    subject_type: str
    tenant_id: str | None
    trace_id: str | None
    package_id: str | None

    @classmethod
    def from_context(cls, context: ExecutionContext) -> ObservabilityBinding:
        return cls(
            correlation_id=context.correlation_id,
            subject_id=str(context.subject_id),
            subject_type=context.subject_type.value,
            tenant_id=str(context.tenant_id) if context.tenant_id else None,
            trace_id=context.trace_id,
            package_id=context.package_id,
        )

    def as_dict(self) -> dict[str, str]:
        return {
            key: value
            for key, value in {
                "correlation_id": self.correlation_id,
                "subject_id": self.subject_id,
                "subject_type": self.subject_type,
                "tenant_id": self.tenant_id,
                "trace_id": self.trace_id,
                "package_id": self.package_id,
            }.items()
            if value is not None
        }
