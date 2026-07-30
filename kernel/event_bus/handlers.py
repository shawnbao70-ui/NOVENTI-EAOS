"""Process-local handler registry for persisted subscription metadata."""

from __future__ import annotations

from threading import RLock
from uuid import UUID

from kernel.event_bus.repository import EventHandler


class EventHandlerRegistry:
    """Keep executable handlers out of the database."""

    def __init__(self) -> None:
        self._handlers: dict[UUID, EventHandler] = {}
        self._lock = RLock()

    def register(self, subscription_id: UUID, handler: EventHandler) -> None:
        with self._lock:
            self._handlers[subscription_id] = handler

    def resolve(self, subscription_id: UUID) -> EventHandler | None:
        with self._lock:
            return self._handlers.get(subscription_id)

    def unregister(self, subscription_id: UUID) -> None:
        with self._lock:
            self._handlers.pop(subscription_id, None)
