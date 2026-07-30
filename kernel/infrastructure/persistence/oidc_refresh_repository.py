"""SQLAlchemy repository for OIDC refresh bindings (PHX-G63)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.oidc_refresh_models import OidcRefreshBindingRecord


class SQLAlchemyOidcRefreshRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get(self, eaos_jti: str) -> OidcRefreshBindingRecord | None:
        with self._session_factory() as session:
            return session.get(OidcRefreshBindingRecord, eaos_jti)

    def put(
        self,
        *,
        eaos_jti: str,
        refresh_token: str | None,
        id_token: str | None,
    ) -> OidcRefreshBindingRecord:
        now = datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(OidcRefreshBindingRecord, eaos_jti)
            if row is None:
                row = OidcRefreshBindingRecord(
                    eaos_jti=eaos_jti,
                    refresh_token=refresh_token,
                    id_token=id_token,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.refresh_token = refresh_token
                row.id_token = id_token
                row.updated_at = now
            session.commit()
            session.refresh(row)
            return row

    def clear(self) -> None:
        with self._session_factory() as session:
            session.execute(delete(OidcRefreshBindingRecord))
            session.commit()

    def pop_detached(self, eaos_jti: str) -> tuple[str | None, str | None] | None:
        """Pop and return (refresh_token, id_token) without a live ORM instance."""

        with self._session_factory() as session:
            row = session.get(OidcRefreshBindingRecord, eaos_jti)
            if row is None:
                return None
            tokens = (row.refresh_token, row.id_token)
            session.delete(row)
            session.commit()
            return tokens
