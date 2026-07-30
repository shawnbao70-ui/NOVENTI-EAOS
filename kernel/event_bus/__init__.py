"""Event Bus — immutable envelopes, outbox relay, DLQ and controlled replay."""

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.event_bus.models import DeliveryReport, EventEnvelope
from kernel.event_bus.outbox import (
    DeadLetterEntry,
    DeliveryStats,
    DispatchReport,
    OutboxEntry,
    OutboxStatus,
)

__all__ = [
    "DeadLetterEntry",
    "DeliveryReport",
    "DeliveryStats",
    "DispatchReport",
    "DomainEventEmitter",
    "EventBus",
    "EventEnvelope",
    "OutboxEntry",
    "OutboxStatus",
]


def __getattr__(name: str):
    if name == "EventBus":
        from kernel.event_bus.bus import EventBus

        return EventBus
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
