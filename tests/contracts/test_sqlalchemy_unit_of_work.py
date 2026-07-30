"""Transaction lifecycle contracts for SQLAlchemy Unit of Work."""

from __future__ import annotations

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from kernel.infrastructure.persistence import (
    SQLAlchemyUnitOfWork,
    create_session_factory,
)
from kernel.shared.unit_of_work import UnitOfWork


def _unit_of_work() -> tuple[SQLAlchemyUnitOfWork, Engine]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE records (value INTEGER NOT NULL)"))
    return SQLAlchemyUnitOfWork(create_session_factory(engine)), engine


def _record_count(engine: Engine) -> int:
    with engine.connect() as connection:
        return int(connection.scalar(text("SELECT COUNT(*) FROM records")))


def test_sqlalchemy_unit_of_work_satisfies_port_and_commits() -> None:
    unit_of_work, engine = _unit_of_work()
    assert isinstance(unit_of_work, UnitOfWork)

    with unit_of_work:
        unit_of_work.session.execute(text("INSERT INTO records VALUES (1)"))
        unit_of_work.commit()

    assert unit_of_work.committed
    assert not unit_of_work.rolled_back
    assert _record_count(engine) == 1


def test_sqlalchemy_unit_of_work_rolls_back_without_commit() -> None:
    unit_of_work, engine = _unit_of_work()

    with unit_of_work:
        unit_of_work.session.execute(text("INSERT INTO records VALUES (1)"))

    assert not unit_of_work.committed
    assert unit_of_work.rolled_back
    assert _record_count(engine) == 0


def test_sqlalchemy_unit_of_work_rolls_back_on_exception() -> None:
    unit_of_work, engine = _unit_of_work()

    with pytest.raises(RuntimeError, match="failure"):
        with unit_of_work:
            unit_of_work.session.execute(text("INSERT INTO records VALUES (1)"))
            raise RuntimeError("failure")

    assert unit_of_work.rolled_back
    assert _record_count(engine) == 0


def test_sqlalchemy_unit_of_work_closes_session_boundary() -> None:
    unit_of_work, _ = _unit_of_work()

    with pytest.raises(RuntimeError, match="not active"):
        _ = unit_of_work.session

    with unit_of_work:
        unit_of_work.commit()
        with pytest.raises(RuntimeError, match="already committed"):
            _ = unit_of_work.session

    with pytest.raises(RuntimeError, match="not active"):
        _ = unit_of_work.session


def test_sqlalchemy_unit_of_work_rejects_nested_entry() -> None:
    unit_of_work, _ = _unit_of_work()

    with unit_of_work:
        with pytest.raises(RuntimeError, match="already active"):
            unit_of_work.__enter__()


def test_session_factory_disables_autoflush_and_expiration() -> None:
    unit_of_work, _ = _unit_of_work()

    with unit_of_work:
        assert not unit_of_work.session.autoflush
        assert not unit_of_work.session.expire_on_commit
