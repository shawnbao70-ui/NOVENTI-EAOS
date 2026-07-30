"""KernelResult helpers for SDK consumers."""

from __future__ import annotations

from typing import TypeVar

from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

T = TypeVar("T")


def require_ok(result: KernelResult[T], *, message: str | None = None) -> KernelResult[T]:
    if not result.ok:
        raise KernelError(
            result.error_code or ErrorCode.COMMON_INTERNAL,
            message or result.error_message or "kernel operation failed",
            details=dict(result.details or {}),
        )
    return result


def unwrap(result: KernelResult[T]) -> T:
    require_ok(result)
    assert result.data is not None
    return result.data
