"""In-memory Digital Twin repository."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol
from uuid import UUID

from eaos_platform.twin.models import TwinSnapshot
from kernel.shared.errors import ErrorCode, KernelError


class TwinRepository(Protocol):
    def add_snapshot(self, snapshot: TwinSnapshot) -> None: ...

    def get_snapshot(self, snapshot_id: UUID) -> TwinSnapshot | None: ...

    def get_active_by_entity_ref(
        self,
        *,
        tenant_id: UUID,
        entity_ref: str,
    ) -> TwinSnapshot | None: ...

    def save_snapshot(
        self,
        snapshot: TwinSnapshot,
        *,
        expected_version: int,
    ) -> None: ...


class InMemoryTwinRepository:
    def __init__(self) -> None:
        self._snapshots: dict[UUID, TwinSnapshot] = {}

    def add_snapshot(self, snapshot: TwinSnapshot) -> None:
        self._snapshots[snapshot.id] = deepcopy(snapshot)

    def get_snapshot(self, snapshot_id: UUID) -> TwinSnapshot | None:
        item = self._snapshots.get(snapshot_id)
        return deepcopy(item) if item is not None else None

    def get_active_by_entity_ref(
        self,
        *,
        tenant_id: UUID,
        entity_ref: str,
    ) -> TwinSnapshot | None:
        for item in self._snapshots.values():
            if (
                item.tenant_id == tenant_id
                and item.entity_ref.casefold() == entity_ref.casefold()
                and item.status.value == "active"
            ):
                return deepcopy(item)
        return None

    def save_snapshot(
        self,
        snapshot: TwinSnapshot,
        *,
        expected_version: int,
    ) -> None:
        current = self._snapshots.get(snapshot.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "twin snapshot version conflict")
        self._snapshots[snapshot.id] = deepcopy(snapshot)
