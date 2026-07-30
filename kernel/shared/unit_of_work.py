"""Transaction boundary ports shared by Kernel services."""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class UnitOfWork(Protocol):
    """Persistence-neutral transaction boundary."""

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class InMemoryUnitOfWork:
    """No-storage UoW used to verify transaction lifecycle contracts."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self._active = False

    def __enter__(self) -> Self:
        self.committed = False
        self.rolled_back = False
        self._active = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            self.rollback()
        self._active = False

    def commit(self) -> None:
        self._require_active()
        self.committed = True

    def rollback(self) -> None:
        self._require_active()
        self.rolled_back = True
        self.committed = False

    def _require_active(self) -> None:
        if not self._active:
            raise RuntimeError("unit of work is not active")
