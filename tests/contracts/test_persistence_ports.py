"""Contracts for persistence-neutral Kernel ports."""

from __future__ import annotations

import pytest

from kernel.event_bus.repository import EventRepository, InMemoryEventRepository
from kernel.identity.repository import IdentityRepository, InMemoryIdentityRepository
from kernel.organization.repository import (
    InMemoryOrganizationRepository,
    OrganizationRepository,
)
from kernel.permission.repository import InMemoryPermissionRepository, PermissionRepository
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.unit_of_work import InMemoryUnitOfWork, UnitOfWork
from kernel.workflow.repository import InMemoryWorkflowRepository, WorkflowRepository


@pytest.mark.parametrize(
    ("adapter", "port"),
    [
        (InMemoryIdentityRepository(), IdentityRepository),
        (InMemoryOrganizationRepository(), OrganizationRepository),
        (InMemoryPermissionRepository(), PermissionRepository),
        (InMemoryWorkflowRepository(), WorkflowRepository),
        (InMemoryEventRepository(), EventRepository),
        (InMemoryAuditLog(), AuditLog),
    ],
)
def test_in_memory_adapters_satisfy_ports(adapter: object, port: type[object]) -> None:
    assert isinstance(adapter, port)


def test_in_memory_unit_of_work_commits_explicitly() -> None:
    unit_of_work = InMemoryUnitOfWork()
    assert isinstance(unit_of_work, UnitOfWork)

    with unit_of_work:
        unit_of_work.commit()

    assert unit_of_work.committed
    assert not unit_of_work.rolled_back


def test_in_memory_unit_of_work_rolls_back_without_commit() -> None:
    unit_of_work = InMemoryUnitOfWork()

    with unit_of_work:
        pass

    assert not unit_of_work.committed
    assert unit_of_work.rolled_back


def test_in_memory_unit_of_work_rolls_back_on_exception() -> None:
    unit_of_work = InMemoryUnitOfWork()

    with pytest.raises(RuntimeError, match="failure"):
        with unit_of_work:
            raise RuntimeError("failure")

    assert not unit_of_work.committed
    assert unit_of_work.rolled_back
