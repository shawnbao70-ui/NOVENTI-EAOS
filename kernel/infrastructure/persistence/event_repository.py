"""Tenant-bound SQLAlchemy adapter for Event Repository."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from kernel.event_bus.handlers import EventHandlerRegistry
from kernel.event_bus.models import EventEnvelope, deep_freeze
from kernel.event_bus.outbox import DeadLetterEntry, OutboxEntry, OutboxStatus
from kernel.event_bus.repository import (
    EventHandler,
    EventSubscription,
    FailedDelivery,
)
from kernel.event_bus.webhook import WebhookPoster, build_webhook_handler
from kernel.infrastructure.persistence.event_models import (
    EventDeadLetterRecord,
    EventDeliveryRecord,
    EventOutboxRecord,
    EventRecord,
    EventSubscriptionRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyOutboxWriter:
    """Session-scoped outbox writer for trusted domain emission (no tenant bind)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_outbox(self, entry: OutboxEntry) -> None:
        self._session.add(
            EventOutboxRecord(
                id=entry.id,
                tenant_id=entry.tenant_id,
                event_id=entry.event_id,
                event_name=entry.event_name,
                schema_version=entry.schema_version,
                producer=entry.producer,
                payload=SQLAlchemyEventRepository._thaw(entry.payload),
                correlation_id=entry.correlation_id,
                status=entry.status.value,
                attempt_count=entry.attempt_count,
                available_at=entry.available_at,
                created_at=entry.created_at,
                leased_until=entry.leased_until,
                leased_by=entry.leased_by,
                last_error_code=entry.last_error_code,
            )
        )


class SQLAlchemyEventRepository:
    def __init__(
        self,
        session: Session,
        *,
        tenant_id: UUID,
        handler_registry: EventHandlerRegistry,
        webhook_poster: WebhookPoster | None = None,
    ) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._handler_registry = handler_registry
        self._webhook_poster = webhook_poster
        self._pending_handlers: list[tuple[UUID, EventHandler]] = []
        self._pending_event_ids: set[UUID] = set()
        self._pending_deliveries: dict[
            tuple[str, UUID],
            EventDeliveryRecord,
        ] = {}

    def add_event(self, event: EventEnvelope) -> None:
        self._require_tenant(event.tenant_id)
        self._session.add(
            EventRecord(
                event_id=event.event_id,
                tenant_id=event.tenant_id,
                event_name=event.event_name,
                schema_version=event.schema_version,
                correlation_id=event.correlation_id,
                timestamp=event.timestamp,
                producer=event.producer,
                payload=self._thaw(event.payload),
            )
        )
        # Delivery records use a composite event foreign key. Persist the
        # parent fact before direct handler delivery can add child attempts.
        self._session.flush()
        self._pending_event_ids.add(event.event_id)

    def get_event(self, event_id: UUID) -> EventEnvelope | None:
        record = self._session.scalar(
            select(EventRecord).where(
                EventRecord.event_id == event_id,
                EventRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        timestamp = record.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return EventEnvelope(
            event_id=record.event_id,
            event_name=record.event_name,
            schema_version=record.schema_version,
            tenant_id=record.tenant_id,
            correlation_id=record.correlation_id,
            timestamp=timestamp.astimezone(timezone.utc),
            producer=record.producer,
            payload=deep_freeze(record.payload),
        )

    def add_subscription(self, subscription: EventSubscription) -> None:
        self._require_tenant(subscription.tenant_id)
        self._session.add(
            EventSubscriptionRecord(
                id=subscription.id,
                tenant_id=subscription.tenant_id,
                subscriber_id=subscription.subscriber_id,
                subscriber_subject_id=subscription.subscriber_subject_id,
                event_name=subscription.event_name,
                delivery_url=subscription.delivery_url,
                signing_secret=subscription.signing_secret,
                created_at=datetime.now(timezone.utc),
            )
        )
        self._pending_handlers.append((subscription.id, subscription.handler))

    def activate_pending_handlers(self) -> None:
        for subscription_id, handler in self._pending_handlers:
            self._handler_registry.register(subscription_id, handler)
        self._pending_handlers.clear()

    def subscription_exists(
        self,
        *,
        tenant_id: UUID,
        subscriber_id: str,
        event_name: str,
    ) -> bool:
        self._require_tenant(tenant_id)
        return (
            self._session.scalar(
                select(EventSubscriptionRecord.id).where(
                    EventSubscriptionRecord.tenant_id == tenant_id,
                    EventSubscriptionRecord.subscriber_id == subscriber_id,
                    EventSubscriptionRecord.event_name == event_name,
                )
            )
            is not None
        )

    def matching_subscriptions(self, event: EventEnvelope) -> list[EventSubscription]:
        self._require_tenant(event.tenant_id)
        records = self._session.scalars(
            select(EventSubscriptionRecord).where(
                EventSubscriptionRecord.tenant_id == event.tenant_id,
                or_(
                    EventSubscriptionRecord.event_name == event.event_name,
                    EventSubscriptionRecord.event_name == "*",
                ),
            )
        )
        return [
            EventSubscription(
                id=record.id,
                tenant_id=record.tenant_id,
                subscriber_id=record.subscriber_id,
                subscriber_subject_id=record.subscriber_subject_id,
                event_name=record.event_name,
                handler=self._resolve_handler(record),
                delivery_url=record.delivery_url,
                signing_secret=record.signing_secret,
            )
            for record in records
        ]

    def was_delivered(self, subscriber_id: str, event_id: UUID) -> bool:
        record = self._delivery(subscriber_id, event_id)
        return record is not None and record.status in {"delivered", "dead"}

    def mark_delivered(self, subscriber_id: str, event_id: UUID) -> None:
        self._mark_attempt(
            subscriber_id,
            event_id,
            status="delivered",
            error_code=None,
        )

    def mark_failed(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> int:
        return self._mark_attempt(
            subscriber_id,
            event_id,
            status="failed",
            error_code=error_code,
        )

    def mark_delivery_dead(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        error_code: str,
    ) -> None:
        self._mark_attempt(
            subscriber_id,
            event_id,
            status="dead",
            error_code=error_code,
            increment=False,
        )

    def add_outbox(self, entry: OutboxEntry) -> None:
        self._require_tenant(entry.tenant_id)
        self._session.add(
            EventOutboxRecord(
                id=entry.id,
                tenant_id=entry.tenant_id,
                event_id=entry.event_id,
                event_name=entry.event_name,
                schema_version=entry.schema_version,
                producer=entry.producer,
                payload=self._thaw(entry.payload),
                correlation_id=entry.correlation_id,
                status=entry.status.value,
                attempt_count=entry.attempt_count,
                available_at=entry.available_at,
                created_at=entry.created_at,
                leased_until=entry.leased_until,
                leased_by=entry.leased_by,
                last_error_code=entry.last_error_code,
            )
        )

    def claim_outbox(
        self,
        *,
        tenant_id: UUID,
        worker_id: str,
        limit: int,
        now: datetime,
        lease_seconds: int,
    ) -> list[OutboxEntry]:
        self._require_tenant(tenant_id)
        candidates = list(
            self._session.scalars(
                select(EventOutboxRecord)
                .where(
                    EventOutboxRecord.tenant_id == tenant_id,
                    EventOutboxRecord.status.in_(
                        [OutboxStatus.PENDING.value, OutboxStatus.LEASED.value]
                    ),
                    EventOutboxRecord.available_at <= now,
                    or_(
                        EventOutboxRecord.status == OutboxStatus.PENDING.value,
                        EventOutboxRecord.leased_until.is_(None),
                        EventOutboxRecord.leased_until <= now,
                    ),
                )
                .order_by(EventOutboxRecord.created_at.asc())
                .limit(limit)
            )
        )
        claimed: list[OutboxEntry] = []
        lease_until = now + timedelta(seconds=lease_seconds)
        for record in candidates:
            result = self._session.execute(
                update(EventOutboxRecord)
                .where(
                    EventOutboxRecord.id == record.id,
                    EventOutboxRecord.status.in_(
                        [OutboxStatus.PENDING.value, OutboxStatus.LEASED.value]
                    ),
                    or_(
                        EventOutboxRecord.leased_until.is_(None),
                        EventOutboxRecord.leased_until <= now,
                        EventOutboxRecord.status == OutboxStatus.PENDING.value,
                    ),
                )
                .values(
                    status=OutboxStatus.LEASED.value,
                    leased_by=worker_id,
                    leased_until=lease_until,
                    attempt_count=EventOutboxRecord.attempt_count + 1,
                )
            )
            if result.rowcount != 1:
                continue
            self._session.refresh(record)
            claimed.append(self._to_outbox(record))
        return claimed

    def save_outbox(self, entry: OutboxEntry) -> None:
        self._require_tenant(entry.tenant_id)
        record = self._session.scalar(
            select(EventOutboxRecord).where(EventOutboxRecord.id == entry.id)
        )
        if record is None:
            raise KernelError(
                ErrorCode.EVENT_OUTBOX_NOT_FOUND,
                "outbox entry not found",
            )
        record.status = entry.status.value
        record.attempt_count = entry.attempt_count
        record.available_at = entry.available_at
        record.leased_until = entry.leased_until
        record.leased_by = entry.leased_by
        record.last_error_code = entry.last_error_code

    def count_outbox(
        self,
        *,
        tenant_id: UUID,
        status: OutboxStatus,
    ) -> int:
        self._require_tenant(tenant_id)
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(EventOutboxRecord)
                .where(
                    EventOutboxRecord.tenant_id == tenant_id,
                    EventOutboxRecord.status == status.value,
                )
            )
            or 0
        )

    def list_retryable_failures(
        self,
        *,
        tenant_id: UUID,
        now: datetime,
        max_attempts: int,
        base_backoff_seconds: int,
    ) -> list[FailedDelivery]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(EventDeliveryRecord).where(
                EventDeliveryRecord.tenant_id == tenant_id,
                EventDeliveryRecord.status == "failed",
                EventDeliveryRecord.attempt_count < max_attempts,
            )
        )
        results: list[FailedDelivery] = []
        for record in records:
            delay = base_backoff_seconds * (2 ** max(record.attempt_count - 1, 0))
            last_attempt = record.last_attempt_at
            if last_attempt.tzinfo is None:
                last_attempt = last_attempt.replace(tzinfo=timezone.utc)
            if last_attempt + timedelta(seconds=delay) > now:
                continue
            results.append(
                FailedDelivery(
                    tenant_id=tenant_id,
                    event_id=record.event_id,
                    subscriber_id=record.subscriber_id,
                    attempt_count=record.attempt_count,
                    last_attempt_at=last_attempt.astimezone(timezone.utc),
                    last_error_code=record.last_error_code,
                )
            )
        return results

    def count_failed_deliveries(self, *, tenant_id: UUID) -> int:
        self._require_tenant(tenant_id)
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(EventDeliveryRecord)
                .where(
                    EventDeliveryRecord.tenant_id == tenant_id,
                    EventDeliveryRecord.status == "failed",
                )
            )
            or 0
        )

    def add_dead_letter(self, entry: DeadLetterEntry) -> None:
        self._require_tenant(entry.tenant_id)
        self._session.add(
            EventDeadLetterRecord(
                id=entry.id,
                tenant_id=entry.tenant_id,
                event_id=entry.event_id,
                subscriber_id=entry.subscriber_id,
                reason=entry.reason,
                attempt_count=entry.attempt_count,
                created_at=entry.created_at,
                replayed_at=entry.replayed_at,
            )
        )

    def get_dead_letter(self, dead_letter_id: UUID) -> DeadLetterEntry | None:
        record = self._session.scalar(
            select(EventDeadLetterRecord).where(
                EventDeadLetterRecord.id == dead_letter_id,
                EventDeadLetterRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_dead_letter(record) if record is not None else None

    def list_dead_letters(self, *, tenant_id: UUID) -> list[DeadLetterEntry]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(EventDeadLetterRecord)
            .where(EventDeadLetterRecord.tenant_id == tenant_id)
            .order_by(EventDeadLetterRecord.created_at.asc())
        )
        return [self._to_dead_letter(record) for record in records]

    def save_dead_letter(self, entry: DeadLetterEntry) -> None:
        self._require_tenant(entry.tenant_id)
        record = self._session.scalar(
            select(EventDeadLetterRecord).where(
                EventDeadLetterRecord.id == entry.id,
                EventDeadLetterRecord.tenant_id == entry.tenant_id,
            )
        )
        if record is None:
            raise KernelError(
                ErrorCode.EVENT_DEAD_LETTER_NOT_FOUND,
                "dead letter not found",
            )
        record.reason = entry.reason
        record.attempt_count = entry.attempt_count
        record.replayed_at = entry.replayed_at

    def count_dead_letters(self, *, tenant_id: UUID) -> int:
        self._require_tenant(tenant_id)
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(EventDeadLetterRecord)
                .where(
                    EventDeadLetterRecord.tenant_id == tenant_id,
                    EventDeadLetterRecord.replayed_at.is_(None),
                )
            )
            or 0
        )

    def _mark_attempt(
        self,
        subscriber_id: str,
        event_id: UUID,
        *,
        status: str,
        error_code: str | None,
        increment: bool = True,
    ) -> int:
        if event_id not in self._pending_event_ids and self.get_event(event_id) is None:
            raise KernelError(ErrorCode.EVENT_NOT_FOUND, "event not found")
        record = self._delivery(subscriber_id, event_id)
        if record is None:
            record = EventDeliveryRecord(
                event_id=event_id,
                subscriber_id=subscriber_id,
                tenant_id=self._tenant_id,
                status=status,
                attempt_count=1,
                last_attempt_at=datetime.now(timezone.utc),
                last_error_code=error_code,
            )
            self._session.add(record)
            self._pending_deliveries[(subscriber_id, event_id)] = record
            return 1
        record.status = status
        if increment:
            record.attempt_count += 1
        record.last_attempt_at = datetime.now(timezone.utc)
        record.last_error_code = error_code
        return record.attempt_count

    @staticmethod
    def _to_outbox(record: EventOutboxRecord) -> OutboxEntry:
        available_at = record.available_at
        created_at = record.created_at
        leased_until = record.leased_until
        if available_at.tzinfo is None:
            available_at = available_at.replace(tzinfo=timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if leased_until is not None and leased_until.tzinfo is None:
            leased_until = leased_until.replace(tzinfo=timezone.utc)
        return OutboxEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            event_id=record.event_id,
            event_name=record.event_name,
            schema_version=record.schema_version,
            producer=record.producer,
            payload=dict(record.payload or {}),
            correlation_id=record.correlation_id,
            status=OutboxStatus(record.status),
            attempt_count=record.attempt_count,
            available_at=available_at.astimezone(timezone.utc),
            created_at=created_at.astimezone(timezone.utc),
            leased_until=(
                leased_until.astimezone(timezone.utc) if leased_until is not None else None
            ),
            leased_by=record.leased_by,
            last_error_code=record.last_error_code,
        )

    @staticmethod
    def _to_dead_letter(record: EventDeadLetterRecord) -> DeadLetterEntry:
        created_at = record.created_at
        replayed_at = record.replayed_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if replayed_at is not None and replayed_at.tzinfo is None:
            replayed_at = replayed_at.replace(tzinfo=timezone.utc)
        return DeadLetterEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            event_id=record.event_id,
            subscriber_id=record.subscriber_id,
            reason=record.reason,
            attempt_count=record.attempt_count,
            created_at=created_at.astimezone(timezone.utc),
            replayed_at=(
                replayed_at.astimezone(timezone.utc) if replayed_at is not None else None
            ),
        )

    def _delivery(
        self,
        subscriber_id: str,
        event_id: UUID,
    ) -> EventDeliveryRecord | None:
        pending = self._pending_deliveries.get((subscriber_id, event_id))
        if pending is not None:
            return pending
        return self._session.scalar(
            select(EventDeliveryRecord).where(
                EventDeliveryRecord.event_id == event_id,
                EventDeliveryRecord.subscriber_id == subscriber_id,
                EventDeliveryRecord.tenant_id == self._tenant_id,
            )
        )

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.EVENT_NOT_FOUND,
                "event resource not found",
            )

    def _resolve_handler(self, record: EventSubscriptionRecord) -> EventHandler:
        registered = self._handler_registry.resolve(record.id)
        if registered is not None:
            return registered
        if record.delivery_url:
            return build_webhook_handler(
                record.delivery_url,
                poster=self._webhook_poster,
                signing_secret=record.signing_secret,
            )
        return self._missing_handler(record.id)

    @staticmethod
    def _missing_handler(subscription_id: UUID):
        def unavailable(_: EventEnvelope) -> None:
            raise RuntimeError(f"handler unavailable for subscription {subscription_id}")

        return unavailable

    @classmethod
    def _thaw(cls, value: Any) -> Any:
        if isinstance(value, MappingProxyType | Mapping):
            return {key: cls._thaw(item) for key, item in value.items()}
        if isinstance(value, tuple):
            return [cls._thaw(item) for item in value]
        return value
