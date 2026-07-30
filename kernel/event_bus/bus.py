"""Permissioned Event Bus with outbox relay, retry and DLQ (PHX-P11)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from kernel.event_bus.models import (
    EVENT_NAME_PATTERN,
    DeliveryReport,
    EventEnvelope,
    deep_freeze,
)
from kernel.event_bus.outbox import (
    DeadLetterEntry,
    DeliveryStats,
    DispatchReport,
    OutboxEntry,
    OutboxStatus,
)
from kernel.event_bus.repository import (
    EventRepository,
    EventHandler,
    EventSubscription,
    InMemoryEventRepository,
)
from kernel.event_bus.webhook import (
    WebhookPoster,
    build_webhook_handler,
    resolve_subscribe_target,
)
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

DEFAULT_MAX_DELIVERY_ATTEMPTS = 5
DEFAULT_MAX_OUTBOX_ATTEMPTS = 5
DEFAULT_LEASE_SECONDS = 30
DEFAULT_BASE_BACKOFF_SECONDS = 1


class EventBus:
    """Immutable, tenant-isolated Event Bus with outbox and DLQ."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: EventRepository | None = None,
        audit_log: AuditLog | None = None,
        *,
        webhook_poster: WebhookPoster | None = None,
        max_delivery_attempts: int = DEFAULT_MAX_DELIVERY_ATTEMPTS,
        max_outbox_attempts: int = DEFAULT_MAX_OUTBOX_ATTEMPTS,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
        base_backoff_seconds: int = DEFAULT_BASE_BACKOFF_SECONDS,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryEventRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._webhook_poster = webhook_poster
        self._max_delivery_attempts = max_delivery_attempts
        self._max_outbox_attempts = max_outbox_attempts
        self._lease_seconds = lease_seconds
        self._base_backoff_seconds = base_backoff_seconds

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def subscribe(
        self,
        ctx: ExecutionContext,
        *,
        subscriber_id: str,
        event_name: str,
        handler: EventHandler | None = None,
        delivery_url: str | None = None,
        signing_secret: str | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "subscribe")
            normalized_subscriber = subscriber_id.strip()
            normalized_event = event_name.strip()
            if not normalized_subscriber:
                raise KernelError(
                    ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                    "subscriber_id is required",
                )
            in_process_handler, normalized_url, normalized_secret = resolve_subscribe_target(
                handler=handler,
                delivery_url=delivery_url,
                signing_secret=signing_secret,
            )
            if normalized_url is not None:
                resolved_handler = build_webhook_handler(
                    normalized_url,
                    poster=self._webhook_poster,
                    signing_secret=normalized_secret,
                )
            else:
                assert in_process_handler is not None
                resolved_handler = in_process_handler
            if normalized_event != "*" and not EVENT_NAME_PATTERN.fullmatch(
                normalized_event
            ):
                raise KernelError(
                    ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                    "event_name must be '*' or match domain.entity.action",
                )
            if self._repo.subscription_exists(
                tenant_id=ctx.tenant_id,
                subscriber_id=normalized_subscriber,
                event_name=normalized_event,
            ):
                raise KernelError(
                    ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                    "duplicate subscription",
                )
            subscription = EventSubscription(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                subscriber_id=normalized_subscriber,
                subscriber_subject_id=ctx.subject_id,
                event_name=normalized_event,
                handler=resolved_handler,
                delivery_url=normalized_url,
                signing_secret=normalized_secret,
            )
            self._repo.add_subscription(subscription)
            audit = self._audit.record(
                ctx,
                action="Event.Subscribe",
                resource=f"event_subscription:{subscription.id}",
                result="ok",
                details={
                    "subscriber_id": normalized_subscriber,
                    "event_name": normalized_event,
                    "transport": "webhook" if normalized_url else "in_process",
                    "hmac": bool(normalized_secret),
                },
            )
            return KernelResult.success(subscription.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def publish(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: Mapping[str, Any],
    ) -> KernelResult[DeliveryReport]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_permission(ctx, "publish")
            event = EventEnvelope.create(
                ctx,
                event_name=event_name,
                schema_version=schema_version,
                producer=producer,
                payload=payload,
            )
            self._repo.add_event(event)
            report = self._deliver(event)
            audit = self._audit.record(
                ctx,
                action="Event.Publish",
                resource=f"event:{event.event_id}",
                result="ok",
                details={
                    "event_name": event.event_name,
                    "delivered_count": report.delivered_count,
                    "failed_subscribers": list(report.failed_subscribers),
                },
            )
            return KernelResult.success(report, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def enqueue(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: Mapping[str, Any],
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "publish")
            event = EventEnvelope.create(
                ctx,
                event_name=event_name,
                schema_version=schema_version,
                producer=producer,
                payload=payload,
            )
            now = datetime.now(timezone.utc)
            entry = OutboxEntry(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                event_id=event.event_id,
                event_name=event.event_name,
                schema_version=event.schema_version,
                producer=event.producer,
                payload=dict(event.payload),
                correlation_id=event.correlation_id,
                status=OutboxStatus.PENDING,
                attempt_count=0,
                available_at=now,
                created_at=now,
            )
            self._repo.add_outbox(entry)
            audit = self._audit.record(
                ctx,
                action="Event.Enqueue",
                resource=f"event_outbox:{entry.id}",
                result="ok",
                details={
                    "event_id": str(event.event_id),
                    "event_name": event.event_name,
                },
            )
            return KernelResult.success(entry.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def dispatch_due(
        self,
        ctx: ExecutionContext,
        *,
        worker_id: str,
        limit: int = 32,
        now: datetime | None = None,
    ) -> KernelResult[DispatchReport]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "dispatch")
            normalized_worker = worker_id.strip()
            if not normalized_worker:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "worker_id is required",
                )
            if limit < 1:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be positive",
                )
            clock = now or datetime.now(timezone.utc)
            outbox_dispatched = 0
            outbox_failed = 0
            claimed = self._repo.claim_outbox(
                tenant_id=ctx.tenant_id,
                worker_id=normalized_worker,
                limit=limit,
                now=clock,
                lease_seconds=self._lease_seconds,
            )
            for entry in claimed:
                try:
                    self._relay_outbox(ctx, entry)
                    entry.status = OutboxStatus.DISPATCHED
                    entry.leased_until = None
                    entry.leased_by = None
                    entry.last_error_code = None
                    self._repo.save_outbox(entry)
                    outbox_dispatched += 1
                except Exception as exc:
                    entry.last_error_code = type(exc).__name__
                    if entry.attempt_count >= self._max_outbox_attempts:
                        entry.status = OutboxStatus.DEAD
                        entry.leased_until = None
                        entry.leased_by = None
                    else:
                        entry.status = OutboxStatus.PENDING
                        entry.leased_until = None
                        entry.leased_by = None
                        delay = self._base_backoff_seconds * (
                            2 ** max(entry.attempt_count - 1, 0)
                        )
                        entry.available_at = clock + timedelta(seconds=delay)
                    self._repo.save_outbox(entry)
                    outbox_failed += 1

            deliveries_retried = 0
            deliveries_dead = 0
            for failure in self._repo.list_retryable_failures(
                tenant_id=ctx.tenant_id,
                now=clock,
                max_attempts=self._max_delivery_attempts,
                base_backoff_seconds=self._base_backoff_seconds,
            ):
                event = self._repo.get_event(failure.event_id)
                if event is None:
                    continue
                subscription = self._subscription_for(
                    event,
                    failure.subscriber_id,
                )
                if subscription is None:
                    continue
                try:
                    subscription.handler(event)
                except Exception as exc:
                    attempts = self._repo.mark_failed(
                        failure.subscriber_id,
                        failure.event_id,
                        error_code=type(exc).__name__,
                    )
                    if attempts >= self._max_delivery_attempts:
                        self._move_to_dead_letter(
                            event,
                            subscriber_id=failure.subscriber_id,
                            reason=type(exc).__name__,
                            attempt_count=attempts,
                        )
                        deliveries_dead += 1
                    continue
                self._repo.mark_delivered(failure.subscriber_id, failure.event_id)
                deliveries_retried += 1

            report = DispatchReport(
                outbox_dispatched=outbox_dispatched,
                outbox_failed=outbox_failed,
                deliveries_retried=deliveries_retried,
                deliveries_dead_lettered=deliveries_dead,
            )
            audit = self._audit.record(
                ctx,
                action="Event.DispatchDue",
                resource=f"event_worker:{normalized_worker}",
                result="ok",
                details={
                    "outbox_dispatched": outbox_dispatched,
                    "outbox_failed": outbox_failed,
                    "deliveries_retried": deliveries_retried,
                    "deliveries_dead_lettered": deliveries_dead,
                },
            )
            return KernelResult.success(report, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_delivery_stats(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[DeliveryStats]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "read")
            stats = DeliveryStats(
                pending_outbox=self._repo.count_outbox(
                    tenant_id=ctx.tenant_id,
                    status=OutboxStatus.PENDING,
                ),
                leased_outbox=self._repo.count_outbox(
                    tenant_id=ctx.tenant_id,
                    status=OutboxStatus.LEASED,
                ),
                failed_deliveries=self._repo.count_failed_deliveries(
                    tenant_id=ctx.tenant_id,
                ),
                dead_letter_depth=self._repo.count_dead_letters(
                    tenant_id=ctx.tenant_id,
                ),
            )
            return KernelResult.success(stats)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_dead_letters(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[DeadLetterEntry]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "replay")
            return KernelResult.success(
                self._repo.list_dead_letters(tenant_id=ctx.tenant_id)
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def replay_dead_letter(
        self,
        ctx: ExecutionContext,
        *,
        dead_letter_id: UUID,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(ctx, "replay")
            entry = self._repo.get_dead_letter(dead_letter_id)
            if entry is None or entry.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.EVENT_DEAD_LETTER_NOT_FOUND,
                    "dead letter not found",
                )
            if entry.replayed_at is not None:
                return KernelResult.success(True)
            event = self._repo.get_event(entry.event_id)
            if event is None or event.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.EVENT_NOT_FOUND, "event not found")
            subscription = self._subscription_for(event, entry.subscriber_id)
            if subscription is None:
                raise KernelError(
                    ErrorCode.EVENT_SUBSCRIPTION_INVALID,
                    "subscriber is no longer registered",
                )
            try:
                subscription.handler(event)
            except Exception as exc:
                entry.reason = type(exc).__name__
                entry.attempt_count += 1
                self._repo.save_dead_letter(entry)
                raise KernelError(
                    ErrorCode.EVENT_DELIVERY_FAILED,
                    "dead letter replay failed",
                ) from exc
            self._repo.mark_delivered(entry.subscriber_id, entry.event_id)
            entry.replayed_at = datetime.now(timezone.utc)
            self._repo.save_dead_letter(entry)
            audit = self._audit.record(
                ctx,
                action="Event.ReplayDeadLetter",
                resource=f"event_dead_letter:{entry.id}",
                result="ok",
                details={
                    "event_id": str(entry.event_id),
                    "subscriber_id": entry.subscriber_id,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def replay(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[DeliveryReport]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_permission(ctx, "replay")
            event = self._repo.get_event(event_id)
            if event is None or event.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.EVENT_NOT_FOUND, "event not found")
            report = self._deliver(event)
            audit = self._audit.record(
                ctx,
                action="Event.Replay",
                resource=f"event:{event.event_id}",
                result="ok",
                details={
                    "delivered_count": report.delivered_count,
                    "skipped_count": report.skipped_count,
                    "failed_subscribers": list(report.failed_subscribers),
                },
            )
            return KernelResult.success(report, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_event(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[EventEnvelope]:
        try:
            require_context(ctx, tenant_data_plane=True)
            self._require_permission(ctx, "read")
            event = self._repo.get_event(event_id)
            if event is None or event.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.EVENT_NOT_FOUND, "event not found")
            return KernelResult.success(event)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _relay_outbox(self, ctx: ExecutionContext, entry: OutboxEntry) -> None:
        del ctx  # tenant already enforced by claim scope
        event = self._repo.get_event(entry.event_id)
        if event is None:
            event = EventEnvelope(
                event_id=entry.event_id,
                event_name=entry.event_name,
                schema_version=entry.schema_version,
                tenant_id=entry.tenant_id,
                correlation_id=entry.correlation_id,
                timestamp=entry.created_at,
                producer=entry.producer,
                payload=deep_freeze(entry.payload),
            )
            self._repo.add_event(event)
        self._deliver(event)

    def _deliver(self, event: EventEnvelope) -> DeliveryReport:
        delivered = 0
        skipped = 0
        failed: list[str] = []
        for subscription in self._repo.matching_subscriptions(event):
            if self._repo.was_delivered(subscription.subscriber_id, event.event_id):
                skipped += 1
                continue
            try:
                subscription.handler(event)
            except Exception as exc:
                attempts = self._repo.mark_failed(
                    subscription.subscriber_id,
                    event.event_id,
                    error_code=type(exc).__name__,
                )
                if attempts >= self._max_delivery_attempts:
                    self._move_to_dead_letter(
                        event,
                        subscriber_id=subscription.subscriber_id,
                        reason=type(exc).__name__,
                        attempt_count=attempts,
                    )
                failed.append(subscription.subscriber_id)
                continue
            self._repo.mark_delivered(subscription.subscriber_id, event.event_id)
            delivered += 1
        return DeliveryReport(
            event_id=event.event_id,
            delivered_count=delivered,
            skipped_count=skipped,
            failed_subscribers=tuple(failed),
        )

    def _move_to_dead_letter(
        self,
        event: EventEnvelope,
        *,
        subscriber_id: str,
        reason: str,
        attempt_count: int,
    ) -> None:
        self._repo.mark_delivery_dead(
            subscriber_id,
            event.event_id,
            error_code=reason,
        )
        self._repo.add_dead_letter(
            DeadLetterEntry(
                id=uuid4(),
                tenant_id=event.tenant_id,
                event_id=event.event_id,
                subscriber_id=subscriber_id,
                reason=reason,
                attempt_count=attempt_count,
                created_at=datetime.now(timezone.utc),
            )
        )

    def _subscription_for(
        self,
        event: EventEnvelope,
        subscriber_id: str,
    ) -> EventSubscription | None:
        for subscription in self._repo.matching_subscriptions(event):
            if subscription.subscriber_id == subscriber_id:
                return subscription
        return None

    def _require_permission(self, ctx: ExecutionContext, action: str) -> None:
        assert ctx.tenant_id is not None
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=Resource(
                tenant_id=ctx.tenant_id,
                resource_type="event_stream",
            ),
        )
        if (
            not result.ok
            or result.data is None
            or result.data.effect != PermissionEffect.ALLOW
        ):
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "event stream permission denied",
            )
