"""Explicit Runtime execution gateway."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar
from uuid import UUID

from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

T = TypeVar("T")


class SessionValidator(Protocol):
    def validate_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
    ) -> KernelResult[Any]: ...


class RuntimeExecutor:
    @staticmethod
    def execute(
        context: ExecutionContext,
        operation: Callable[[ExecutionContext], T],
        *,
        tenant_data_plane: bool = True,
        session_validator: SessionValidator | None = None,
    ) -> T:
        require_context(context, tenant_data_plane=tenant_data_plane)
        if context.session_id is not None:
            if session_validator is None:
                raise KernelError(
                    ErrorCode.CTX_INVALID,
                    "session validation is required",
                )
            result = session_validator.validate_session(
                context,
                session_id=context.session_id,
            )
            if not result.ok:
                raise KernelError(
                    ErrorCode.CTX_INVALID,
                    "session validation failed",
                )
        return operation(context)
