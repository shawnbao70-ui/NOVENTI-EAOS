"""In-memory Event store, subscription registry, outbox and DLQ."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, Protocol, runtime_checkable
from uuid import UUID

from kernel.event_bus.models import EventEnvelope
from kernel.event_bus.outbox import DeadLetterEntry, OutboxEntry, OutboxStatus
from kernel.shared.errors import ErrorCode, KernelError

EventHandler = Callable[[EventEnvelope], None]


@dataclass(frozen=True, slots=True)
class EventSubscription:
    id: UUID
    tenant_id: UUID
    subscriber_id: str
    subscriber_subject_id: UUID
    event_name: str
    handler: EventHandler
    delivery_url: str | None = None
    signing_secret: str | None = None


@dataclass(frozen=True, slots=True)
class FailedDelivery:
    tenant_id: UUID
    event_id: UUID
    subscriber_id: str
    attempt_count: int
    last_attempt_at: datetime
    last_error_code: str | None


@runtime_checkable
class EventRepository(Protocol):
    def add_event(self, event: EventEnvelope) -> None: ...

    def get_event(self, event_id: UUID) -> Optional[EventEnvelope]: ...

    def add_subscription(self, subscription: EventSubscription) -> None: ...

    def subscription_exists(
        self,
        *,
        tenant_id: UUID,
        subscriber_id: str,
        event_name: str,
    ) -> bool: ...

    def matching_subscriptions(self, event: EventEnvelope) -> list[EventSubscription]: ...

    def was_delivered(self, subscriber_id: str, event_id: UUID) -> bool: ...

    def mark_delivered(self, subscriber_id: str, event_id: UUID) -> None: ...

    def mark_failed(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> int: ...

    def mark_delivery_dead(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> None: ...

    def add_outbox(self, entry: OutboxEntry) -> None: ...

    def claim_outbox(
        self,
        *,
        tenant_id: UUID,
        worker_id: str,
        limit: int,
        now: datetime,
        lease_seconds: int,
    ) -> list[OutboxEntry]: ...

    def save_outbox(self, entry: OutboxEntry) -> None: ...

    def count_outbox(
        self,
        *,
        tenant_id: UUID,
        status: OutboxStatus,
    ) -> int: ...

    def list_retryable_failures(
        self,
        *,
        tenant_id: UUID,
        now: datetime,
        max_attempts: int,
        base_backoff_seconds: int,
    ) -> list[FailedDelivery]: ...

    def count_failed_deliveries(self, *, tenant_id: UUID) -> int: ...

    def add_dead_letter(self, entry: DeadLetterEntry) -> None: ...

    def get_dead_letter(self, dead_letter_id: UUID) -> Optional[DeadLetterEntry]: ...

    def list_dead_letters(self, *, tenant_id: UUID) -> list[DeadLetterEntry]: ...

    def save_dead_letter(self, entry: DeadLetterEntry) -> None: ...

    def count_dead_letters(self, *, tenant_id: UUID) -> int: ...


class InMemoryEventRepository:
    def __init__(self) -> None:
        self.events: dict[UUID, EventEnvelope] = {}
        self.subscriptions: dict[UUID, EventSubscription] = {}
        self.delivered: set[tuple[str, UUID]] = set()
        self.failed_attempts: dict[tuple[str, UUID], tuple[int, str]] = {}
        self.dead_deliveries: set[tuple[str, UUID]] = set()
        self.outbox: dict[UUID, OutboxEntry] = {}
        self.dead_letters: dict[UUID, DeadLetterEntry] = {}
        self._failure_times: dict[tuple[str, UUID], datetime] = {}

    def add_event(self, event: EventEnvelope) -> None:
        self.events[event.event_id] = event

    def get_event(self, event_id: UUID) -> Optional[EventEnvelope]:
        return self.events.get(event_id)

    def add_subscription(self, subscription: EventSubscription) -> None:
        self.subscriptions[subscription.id] = subscription

    def subscription_exists(
        self,
        *,
        tenant_id: UUID,
        subscriber_id: str,
        event_name: str,
    ) -> bool:
        return any(
            subscription.tenant_id == tenant_id
            and subscription.subscriber_id == subscriber_id
            and subscription.event_name == event_name
            for subscription in self.subscriptions.values()
        )

    def matching_subscriptions(self, event: EventEnvelope) -> list[EventSubscription]:
        return [
            subscription
            for subscription in self.subscriptions.values()
            if subscription.tenant_id == event.tenant_id
            and subscription.event_name in {event.event_name, "*"}
        ]

    def was_delivered(self, subscriber_id: str, event_id: UUID) -> bool:
        key = (subscriber_id, event_id)
        return key in self.delivered or key in self.dead_deliveries

    def mark_delivered(self, subscriber_id: str, event_id: UUID) -> None:
        self.delivered.add((subscriber_id, event_id))
        self.failed_attempts.pop((subscriber_id, event_id), None)
        self._failure_times.pop((subscriber_id, event_id), None)
        self.dead_deliveries.discard((subscriber_id, event_id))

    def mark_failed(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> int:
        key = (subscriber_id, event_id)
        attempts, _ = self.failed_attempts.get(key, (0, ""))
        attempts += 1
        self.failed_attempts[key] = (attempts, error_code)
        self._failure_times[key] = datetime.now(timezone.utc)
        return attempts

    def mark_delivery_dead(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> None:
        key = (subscriber_id, event_id)
        attempts, _ = self.failed_attempts.get(key, (0, error_code))
        self.failed_attempts[key] = (max(attempts, 1), error_code)
        self.dead_deliveries.add(key)

    def add_outbox(self, entry: OutboxEntry) -> None:
        self.outbox[entry.id] = deepcopy(entry)

    def claim_outbox(
        self,
        *,
        tenant_id: UUID,
        worker_id: str,
        limit: int,
        now: datetime,
        lease_seconds: int,
    ) -> list[OutboxEntry]:
        claimed: list[OutboxEntry] = []
        for entry in sorted(self.outbox.values(), key=lambda item: item.created_at):
            if len(claimed) >= limit:
                break
            if entry.tenant_id != tenant_id:
                continue
            if entry.status not in {OutboxStatus.PENDING, OutboxStatus.LEASED}:
                continue
            if entry.available_at > now:
                continue
            if (
                entry.status == OutboxStatus.LEASED
                and entry.leased_until is not None
                and entry.leased_until > now
            ):
                continue
            entry.status = OutboxStatus.LEASED
            entry.leased_by = worker_id
            entry.leased_until = now + timedelta(seconds=lease_seconds)
            entry.attempt_count += 1
            self.outbox[entry.id] = deepcopy(entry)
            claimed.append(deepcopy(entry))
        return claimed

    def save_outbox(self, entry: OutboxEntry) -> None:
        current = self.outbox.get(entry.id)
        if current is None:
            raise KernelError(
                ErrorCode.EVENT_OUTBOX_NOT_FOUND,
                "outbox entry not found",
            )
        self.outbox[entry.id] = deepcopy(entry)

    def count_outbox(
        self,
        *,
        tenant_id: UUID,
        status: OutboxStatus,
    ) -> int:
        return sum(
            1
            for entry in self.outbox.values()
            if entry.tenant_id == tenant_id and entry.status == status
        )

    def list_retryable_failures(
        self,
        *,
        tenant_id: UUID,
        now: datetime,
        max_attempts: int,
        base_backoff_seconds: int,
    ) -> list[FailedDelivery]:
        results: list[FailedDelivery] = []
        for (subscriber_id, event_id), (attempts, error) in self.failed_attempts.items():
            if (subscriber_id, event_id) in self.delivered:
                continue
            if (subscriber_id, event_id) in self.dead_deliveries:
                continue
            if attempts >= max_attempts:
                continue
            event = self.events.get(event_id)
            if event is None or event.tenant_id != tenant_id:
                continue
            last_attempt = self._failure_times.get(
                (subscriber_id, event_id),
                datetime.now(timezone.utc),
            )
            delay = base_backoff_seconds * (2 ** max(attempts - 1, 0))
            if last_attempt + timedelta(seconds=delay) > now:
                continue
            results.append(
                FailedDelivery(
                    tenant_id=tenant_id,
                    event_id=event_id,
                    subscriber_id=subscriber_id,
                    attempt_count=attempts,
                    last_attempt_at=last_attempt,
                    last_error_code=error,
                )
            )
        return results

    def count_failed_deliveries(self, *, tenant_id: UUID) -> int:
        count = 0
        for (subscriber_id, event_id), _ in self.failed_attempts.items():
            if (subscriber_id, event_id) in self.delivered:
                continue
            if (subscriber_id, event_id) in self.dead_deliveries:
                continue
            event = self.events.get(event_id)
            if event is not None and event.tenant_id == tenant_id:
                count += 1
        return count

    def add_dead_letter(self, entry: DeadLetterEntry) -> None:
        self.dead_letters[entry.id] = deepcopy(entry)

    def get_dead_letter(self, dead_letter_id: UUID) -> Optional[DeadLetterEntry]:
        entry = self.dead_letters.get(dead_letter_id)
        return deepcopy(entry) if entry is not None else None

    def list_dead_letters(self, *, tenant_id: UUID) -> list[DeadLetterEntry]:
        return [
            deepcopy(entry)
            for entry in self.dead_letters.values()
            if entry.tenant_id == tenant_id
        ]

    def save_dead_letter(self, entry: DeadLetterEntry) -> None:
        if entry.id not in self.dead_letters:
            raise KernelError(
                ErrorCode.EVENT_DEAD_LETTER_NOT_FOUND,
                "dead letter not found",
            )
        self.dead_letters[entry.id] = deepcopy(entry)

    def count_dead_letters(self, *, tenant_id: UUID) -> int:
        return sum(
            1
            for entry in self.dead_letters.values()
            if entry.tenant_id == tenant_id and entry.replayed_at is None
        )
