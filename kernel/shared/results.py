"""Common Kernel result envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from kernel.shared.errors import ErrorCode, KernelError

T = TypeVar("T")


@dataclass(slots=True)
class KernelResult(Generic[T]):
    ok: bool
    data: Optional[T] = None
    error_code: Optional[ErrorCode] = None
    error_message: Optional[str] = None
    audit_id: Optional[UUID] = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, data: T, *, audit_id: UUID | None = None) -> KernelResult[T]:
        return cls(ok=True, data=data, audit_id=audit_id)

    @classmethod
    def failure(
        cls,
        code: ErrorCode,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        audit_id: UUID | None = None,
    ) -> KernelResult[T]:
        return cls(
            ok=False,
            error_code=code,
            error_message=message,
            details=details or {},
            audit_id=audit_id,
        )

    @classmethod
    def from_error(cls, err: KernelError, *, audit_id: UUID | None = None) -> KernelResult[T]:
        return cls.failure(err.code, err.message, details=err.details, audit_id=audit_id)
