"""SQLAlchemy repository for IdP issuer bindings (PHX-G57)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.idp_issuer_models import IdpIssuerBindingRecord


class SQLAlchemyIdpIssuerRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self, *, include_disabled: bool = True) -> list[IdpIssuerBindingRecord]:
        with self._session_factory() as session:
            stmt = select(IdpIssuerBindingRecord).order_by(
                func.lower(IdpIssuerBindingRecord.issuer)
            )
            if not include_disabled:
                stmt = stmt.where(IdpIssuerBindingRecord.status == "active")
            return list(session.scalars(stmt).all())

    def get(self, issuer_id: UUID) -> IdpIssuerBindingRecord | None:
        with self._session_factory() as session:
            return session.get(IdpIssuerBindingRecord, issuer_id)

    def create_or_reactivate(
        self,
        *,
        issuer: str,
        jwks_url: str | None,
        jwks_json: str | None,
    ) -> tuple[IdpIssuerBindingRecord, str]:
        """Return (record, 'created'|'reactivated'). Raises ValueError on active conflict."""

        payload = _encode_jwks_json(jwks_json)
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            existing = session.scalar(
                select(IdpIssuerBindingRecord).where(
                    func.lower(IdpIssuerBindingRecord.issuer) == issuer.casefold()
                )
            )
            if existing is not None:
                if existing.status == "active":
                    raise ValueError("active_exists")
                existing.jwks_url = jwks_url
                existing.jwks_json = payload
                existing.status = "active"
                existing.updated_at = now
                existing.version = int(existing.version) + 1
                session.commit()
                session.refresh(existing)
                return existing, "reactivated"

            row = IdpIssuerBindingRecord(
                id=uuid4(),
                issuer=issuer,
                jwks_url=jwks_url,
                jwks_json=payload,
                status="active",
                created_at=now,
                updated_at=now,
                version=1,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row, "created"

    def upsert(
        self,
        *,
        issuer: str,
        jwks_url: str | None,
        jwks_json: str | None,
    ) -> tuple[IdpIssuerBindingRecord, str]:
        """Create, reactivate, or update active row. Returns action label."""

        payload = _encode_jwks_json(jwks_json)
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            existing = session.scalar(
                select(IdpIssuerBindingRecord).where(
                    func.lower(IdpIssuerBindingRecord.issuer) == issuer.casefold()
                )
            )
            if existing is not None:
                same = (
                    existing.status == "active"
                    and existing.jwks_url == jwks_url
                    and existing.jwks_json == payload
                )
                if same:
                    return existing, "unchanged"
                prior = existing.status
                existing.jwks_url = jwks_url
                existing.jwks_json = payload
                existing.status = "active"
                existing.updated_at = now
                existing.version = int(existing.version) + 1
                session.commit()
                session.refresh(existing)
                return existing, "reactivated" if prior == "disabled" else "updated"

            row = IdpIssuerBindingRecord(
                id=uuid4(),
                issuer=issuer,
                jwks_url=jwks_url,
                jwks_json=payload,
                status="active",
                created_at=now,
                updated_at=now,
                version=1,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row, "created"

    def disable(self, issuer_id: UUID) -> IdpIssuerBindingRecord | None:
        with self._session_factory() as session:
            row = session.get(IdpIssuerBindingRecord, issuer_id)
            if row is None:
                return None
            if row.status != "disabled":
                row.status = "disabled"
                row.updated_at = datetime.now(timezone.utc)
                row.version = int(row.version) + 1
                session.commit()
                session.refresh(row)
            return row


def decode_jwks_json(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def _encode_jwks_json(raw: str | None) -> dict[str, Any] | list[Any] | None:
    if raw is None or not str(raw).strip():
        return None
    text = str(raw).strip()
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    if isinstance(loaded, (dict, list)):
        return loaded
    return {"raw": text}
