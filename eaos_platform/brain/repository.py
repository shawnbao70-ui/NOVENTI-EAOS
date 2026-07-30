"""In-memory Enterprise Brain repository."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol
from uuid import UUID

from eaos_platform.brain.models import BrainInsight
from kernel.shared.errors import ErrorCode, KernelError


class BrainRepository(Protocol):
    def add_insight(self, insight: BrainInsight) -> None: ...

    def get_insight(self, insight_id: UUID) -> BrainInsight | None: ...


class InMemoryBrainRepository:
    def __init__(self) -> None:
        self._insights: dict[UUID, BrainInsight] = {}

    def add_insight(self, insight: BrainInsight) -> None:
        self._insights[insight.id] = deepcopy(insight)

    def get_insight(self, insight_id: UUID) -> BrainInsight | None:
        item = self._insights.get(insight_id)
        return deepcopy(item) if item is not None else None
