"""SQLAlchemy implementation of the Kernel Unit of Work port."""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyUnitOfWork:
    """Own exactly one Session and transaction lifecycle per context."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.committed = False
        self.rolled_back = False

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("unit of work is not active")
        if self.committed:
            raise RuntimeError("unit of work is already committed")
        return self._session

    def __enter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("unit of work is already active")
        self._session = self._session_factory()
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if not self.committed:
                self.rollback()
        finally:
            assert self._session is not None
            self._session.close()
            self._session = None

    def commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            self.rolled_back = True
            self.committed = False
            raise
        self.committed = True
        self.rolled_back = False

    def rollback(self) -> None:
        self.session.rollback()
        self.rolled_back = True
        self.committed = False
