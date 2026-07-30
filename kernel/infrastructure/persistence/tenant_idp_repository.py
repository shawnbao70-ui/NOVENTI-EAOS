"""SQLAlchemy repository for tenant IdP federation bindings (PHX-G67/G78)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.tenant_idp_models import (
    DEFAULT_PRIORITY,
    TenantIdpBindingRecord,
)


class SQLAlchemyTenantIdpRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(
        self,
        *,
        tenant_id: UUID | None = None,
        include_disabled: bool = True,
    ) -> list[TenantIdpBindingRecord]:
        with self._session_factory() as session:
            stmt = select(TenantIdpBindingRecord).order_by(
                TenantIdpBindingRecord.tenant_id,
                TenantIdpBindingRecord.priority,
                func.lower(TenantIdpBindingRecord.issuer),
            )
            if tenant_id is not None:
                stmt = stmt.where(TenantIdpBindingRecord.tenant_id == tenant_id)
            if not include_disabled:
                stmt = stmt.where(TenantIdpBindingRecord.status == "active")
            return list(session.scalars(stmt).all())

    def get(self, binding_id: UUID) -> TenantIdpBindingRecord | None:
        with self._session_factory() as session:
            return session.get(TenantIdpBindingRecord, binding_id)

    def create_or_reactivate(
        self,
        *,
        tenant_id: UUID,
        issuer: str,
    ) -> tuple[TenantIdpBindingRecord, str]:
        """Return (record, 'created'|'reactivated'). Raises ValueError on active conflict."""

        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            existing = session.scalar(
                select(TenantIdpBindingRecord).where(
                    TenantIdpBindingRecord.tenant_id == tenant_id,
                    func.lower(TenantIdpBindingRecord.issuer) == issuer.casefold(),
                )
            )
            if existing is not None:
                if existing.status == "active":
                    raise ValueError("active_exists")
                existing.status = "active"
                existing.issuer = issuer
                existing.updated_at = now
                existing.version = int(existing.version) + 1
                session.commit()
                session.refresh(existing)
                return existing, "reactivated"

            row = TenantIdpBindingRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                issuer=issuer,
                status="active",
                priority=DEFAULT_PRIORITY,
                created_at=now,
                updated_at=now,
                version=1,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row, "created"

    def set_priority(
        self, binding_id: UUID, *, priority: int
    ) -> TenantIdpBindingRecord | None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(TenantIdpBindingRecord, binding_id)
            if row is None:
                return None
            row.priority = priority
            row.updated_at = now
            row.version = int(row.version) + 1
            session.commit()
            session.refresh(row)
            return row

    def disable(self, binding_id: UUID) -> TenantIdpBindingRecord | None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(TenantIdpBindingRecord, binding_id)
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
            session.execute(delete(TenantIdpBindingRecord))
            session.commit()

    def has_active(self, *, tenant_id: UUID, issuer: str) -> bool:
        with self._session_factory() as session:
            row = session.scalar(
                select(TenantIdpBindingRecord.id).where(
                    TenantIdpBindingRecord.tenant_id == tenant_id,
                    TenantIdpBindingRecord.status == "active",
                    func.lower(TenantIdpBindingRecord.issuer) == issuer.casefold(),
                )
            )
            return row is not None
