"""SQLAlchemy repository for declared EAOS roles (PHX-G90)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.eaos_declared_role_models import (
    EaosDeclaredRoleRecord,
)


class SQLAlchemyEaosDeclaredRoleRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self, *, include_disabled: bool = True) -> list[EaosDeclaredRoleRecord]:
        with self._session_factory() as session:
            stmt = select(EaosDeclaredRoleRecord).order_by(
                func.lower(EaosDeclaredRoleRecord.name)
            )
            if not include_disabled:
                stmt = stmt.where(EaosDeclaredRoleRecord.status == "active")
            return list(session.scalars(stmt).all())

    def get(self, role_id: UUID) -> EaosDeclaredRoleRecord | None:
        with self._session_factory() as session:
            return session.get(EaosDeclaredRoleRecord, role_id)

    def upsert(self, *, name: str) -> tuple[EaosDeclaredRoleRecord, str]:
        """Create, reactivate, or leave unchanged. Returns (row, action)."""

        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            existing = session.scalar(
                select(EaosDeclaredRoleRecord).where(
                    func.lower(EaosDeclaredRoleRecord.name) == name.casefold()
                )
            )
            if existing is not None:
                if existing.status == "active":
                    return existing, "unchanged"
                existing.status = "active"
                existing.updated_at = now
                existing.version = int(existing.version) + 1
                session.commit()
                session.refresh(existing)
                return existing, "reactivated"

            row = EaosDeclaredRoleRecord(
                id=uuid4(),
                name=name,
                status="active",
                created_at=now,
                updated_at=now,
                version=1,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row, "created"

    def disable(self, role_id: UUID) -> EaosDeclaredRoleRecord | None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(EaosDeclaredRoleRecord, role_id)
            if row is None:
                return None
            if row.status == "disabled":
                return row
            row.status = "disabled"
            row.updated_at = now
            row.version = int(row.version) + 1
            session.commit()
            session.refresh(row)
            return row

    def clear(self) -> None:
        with self._session_factory() as session:
            for row in session.scalars(select(EaosDeclaredRoleRecord)):
                session.delete(row)
            session.commit()
