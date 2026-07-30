"""PHX-P11 outbox, worker lease, retry and DLQ contracts."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from kernel.event_bus.bus import EventBus
from kernel.event_bus.outbox import OutboxStatus
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
PUBLISHER_ID = uuid4()
WORKER_ID = uuid4()
REPLAYER_ID = uuid4()
SUBSCRIBER_ID = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _services(**kwargs) -> tuple[PermissionService, EventBus]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    return permission, EventBus(permission, **kwargs)


def _grant(permission, tenant_id, principal_id, *actions: str) -> None:
    assert permission.grant(
        _ctx(tenant_id, ADMIN_ID),
        principal_subject_id=principal_id,
        resource_type="event_stream",
        actions=set(actions),
    ).ok


def test_enqueue_does_not_deliver_until_dispatch() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, SUBSCRIBER_ID, "subscribe")
    _grant(permission, tenant_id, WORKER_ID, "dispatch", "read")
    received: list[str] = []
    assert bus.subscribe(
        _ctx(tenant_id, SUBSCRIBER_ID),
        subscriber_id="projection.orders",
        event_name="crm.order.created",
        handler=lambda event: received.append(event.event_name),
    ).ok

    enqueued = bus.enqueue(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.order.created",
        schema_version="1",
        producer="pkg.crm",
        payload={"order_id": "O-1"},
    )
    assert enqueued.ok
    assert received == []

    stats = bus.get_delivery_stats(_ctx(tenant_id, WORKER_ID))
    assert stats.data is not None
    assert stats.data.pending_outbox == 1

    dispatched = bus.dispatch_due(
        _ctx(tenant_id, WORKER_ID),
        worker_id="worker-1",
    )
    assert dispatched.ok and dispatched.data is not None
    assert dispatched.data.outbox_dispatched == 1
    assert received == ["crm.order.created"]

    stats_after = bus.get_delivery_stats(_ctx(tenant_id, WORKER_ID))
    assert stats_after.data is not None
    assert stats_after.data.pending_outbox == 0


def test_failed_delivery_retries_then_dead_letters() -> None:
    tenant_id = uuid4()
    permission, bus = _services(max_delivery_attempts=2, base_backoff_seconds=0)
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, SUBSCRIBER_ID, "subscribe")
    _grant(permission, tenant_id, WORKER_ID, "dispatch", "read")
    _grant(permission, tenant_id, REPLAYER_ID, "replay")

    def boom(_event) -> None:
        raise RuntimeError("transient")

    assert bus.subscribe(
        _ctx(tenant_id, SUBSCRIBER_ID),
        subscriber_id="projection.failing",
        event_name="crm.order.failed",
        handler=boom,
    ).ok
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.order.failed",
        schema_version="1",
        producer="pkg.crm",
        payload={"order_id": "O-2"},
    )
    assert published.ok and published.data is not None
    assert published.data.failed_subscribers == ("projection.failing",)

    # First failure already consumed one attempt; one retry then DLQ.
    now = ExecutionContext.utc_now() + timedelta(seconds=1)
    first = bus.dispatch_due(
        _ctx(tenant_id, WORKER_ID),
        worker_id="worker-1",
        now=now,
    )
    assert first.data is not None
    assert first.data.deliveries_dead_lettered == 1

    stats = bus.get_delivery_stats(_ctx(tenant_id, WORKER_ID))
    assert stats.data is not None
    assert stats.data.dead_letter_depth == 1
    assert stats.data.failed_deliveries == 0

    letters = bus.list_dead_letters(_ctx(tenant_id, REPLAYER_ID))
    assert letters.ok and letters.data is not None
    assert len(letters.data) == 1

    recovered: list[UUID] = []

    def recover(event) -> None:
        recovered.append(event.event_id)

    from dataclasses import replace

    repo = bus._repo
    for subscription in list(repo.subscriptions.values()):
        if subscription.subscriber_id == "projection.failing":
            repo.subscriptions[subscription.id] = replace(
                subscription,
                handler=recover,
            )

    replayed = bus.replay_dead_letter(
        _ctx(tenant_id, REPLAYER_ID),
        dead_letter_id=letters.data[0].id,
    )
    assert replayed.ok
    assert recovered == [published.data.event_id]

    stats_after = bus.get_delivery_stats(_ctx(tenant_id, WORKER_ID))
    assert stats_after.data is not None
    assert stats_after.data.dead_letter_depth == 0


def test_dispatch_requires_permission() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    assert bus.enqueue(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.order.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    ).ok
    denied = bus.dispatch_due(
        _ctx(tenant_id, WORKER_ID),
        worker_id="worker-1",
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED


def test_outbox_status_transitions_to_dispatched() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, WORKER_ID, "dispatch")
    enqueued = bus.enqueue(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="org.tenant.created",
        schema_version="1",
        producer="kernel.organization",
        payload={"tenant": "demo"},
    )
    assert enqueued.data is not None
    entry = bus._repo.outbox[enqueued.data]
    assert entry.status == OutboxStatus.PENDING
    assert bus.dispatch_due(
        _ctx(tenant_id, WORKER_ID),
        worker_id="worker-1",
    ).ok
    entry = bus._repo.outbox[enqueued.data]
    assert entry.status == OutboxStatus.DISPATCHED
