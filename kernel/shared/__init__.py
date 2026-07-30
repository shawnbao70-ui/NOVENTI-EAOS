"""Shared Kernel primitives: context, errors, results, audit."""

from kernel.shared.audit import AuditEvent, AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from kernel.shared.unit_of_work import InMemoryUnitOfWork, UnitOfWork

__all__ = [
    "AuditEvent",
    "AuditLog",
    "ErrorCode",
    "ExecutionContext",
    "InMemoryAuditLog",
    "InMemoryUnitOfWork",
    "KernelError",
    "KernelResult",
    "SubjectType",
    "UnitOfWork",
    "require_context",
]
