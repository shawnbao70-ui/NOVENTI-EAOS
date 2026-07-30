"""Event Bus contract tests — E-01..E-04 and tenant isolation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from kernel.event_bus.bus import EventBus
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

GRANT_ADMIN_ID = uuid4()
PUBLISHER_ID = uuid4()
SUBSCRIBER_ID = uuid4()
REPLAYER_ID = uuid4()


class _AllowAllPrincipalEligibility:
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


def _services() -> tuple[PermissionService, EventBus]:
    permission = PermissionService(
        grant_administrators={GRANT_ADMIN_ID},
        principal_eligibility=_AllowAllPrincipalEligibility(),
    )
    return permission, EventBus(permission)


def _grant(
    permission: PermissionService,
    tenant_id: UUID,
    principal_id: UUID,
    *actions: str,
) -> None:
    result = permission.grant(
        _ctx(tenant_id, GRANT_ADMIN_ID),
        principal_subject_id=principal_id,
        resource_type="event_stream",
        actions=set(actions),
    )
    assert result.ok


def test_e01_publish_complete_immutable_envelope() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, SUBSCRIBER_ID, "subscribe")
    received = []
    subscribed = bus.subscribe(
        _ctx(tenant_id, SUBSCRIBER_ID),
        subscriber_id="projection.customer",
        event_name="crm.customer.created",
        handler=received.append,
    )
    assert subscribed.ok
    mutable_payload = {"customer_id": "C-1", "tags": ["new"]}
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1.0",
        producer="pkg.crm",
        payload=mutable_payload,
    )
    assert published.ok and published.data is not None
    assert published.data.delivered_count == 1
    assert len(received) == 1
    event = received[0]
    assert event.tenant_id == tenant_id
    assert event.correlation_id

    mutable_payload["customer_id"] = "MUTATED"
    mutable_payload["tags"].append("changed")
    assert event.payload["customer_id"] == "C-1"
    assert event.payload["tags"] == ("new",)
    with pytest.raises(TypeError):
        event.payload["customer_id"] = "forbidden"
    with pytest.raises(FrozenInstanceError):
        event.producer = "forbidden"


def test_e02_invalid_envelope_is_rejected_before_storage() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    result = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="CustomerCreated",
        schema_version="1.0",
        producer="pkg.crm",
        payload={},
    )
    assert not result.ok
    assert result.error_code == ErrorCode.EVENT_ENVELOPE_INVALID
    assert bus._repo.events == {}


def test_payload_rejects_non_json_mutable_objects() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    result = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={"unsafe": object()},
    )
    assert not result.ok
    assert result.error_code == ErrorCode.EVENT_ENVELOPE_INVALID


def test_publish_without_permission_is_denied() -> None:
    tenant_id = uuid4()
    _, bus = _services()
    result = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_e03_replay_without_permission_is_denied() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert published.data is not None
    replay = bus.replay(
        _ctx(tenant_id, REPLAYER_ID),
        event_id=published.data.event_id,
    )
    assert not replay.ok
    assert replay.error_code == ErrorCode.PERMISSION_DENIED


def test_e04_authorized_replay_preserves_subscriber_idempotency() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, SUBSCRIBER_ID, "subscribe")
    _grant(permission, tenant_id, REPLAYER_ID, "replay")
    received = []
    assert bus.subscribe(
        _ctx(tenant_id, SUBSCRIBER_ID),
        subscriber_id="projection.customer",
        event_name="crm.customer.created",
        handler=received.append,
    ).ok
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={"customer_id": "C-1"},
    )
    assert published.data is not None
    replay = bus.replay(
        _ctx(tenant_id, REPLAYER_ID),
        event_id=published.data.event_id,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.delivered_count == 0
    assert replay.data.skipped_count == 1
    assert len(received) == 1
    assert replay.audit_id is not None


def test_failed_delivery_remains_eligible_for_replay() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    _grant(permission, tenant_id, SUBSCRIBER_ID, "subscribe")
    _grant(permission, tenant_id, REPLAYER_ID, "replay")
    attempts = {"count": 0}

    def flaky_handler(event) -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary failure")

    assert bus.subscribe(
        _ctx(tenant_id, SUBSCRIBER_ID),
        subscriber_id="projection.flaky",
        event_name="crm.customer.created",
        handler=flaky_handler,
    ).ok
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert published.data is not None
    assert published.data.failed_subscribers == ("projection.flaky",)
    replay = bus.replay(
        _ctx(tenant_id, REPLAYER_ID),
        event_id=published.data.event_id,
    )
    assert replay.data is not None
    assert replay.data.delivered_count == 1
    assert attempts["count"] == 2


def test_cross_tenant_subscription_and_event_read_are_isolated() -> None:
    tenant_a = uuid4()
    tenant_b = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_a, PUBLISHER_ID, "publish")
    _grant(permission, tenant_b, SUBSCRIBER_ID, "subscribe")
    _grant(permission, tenant_b, SUBSCRIBER_ID, "read")
    received = []
    assert bus.subscribe(
        _ctx(tenant_b, SUBSCRIBER_ID),
        subscriber_id="tenant-b-projection",
        event_name="crm.customer.created",
        handler=received.append,
    ).ok
    published = bus.publish(
        _ctx(tenant_a, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert published.data is not None
    assert published.data.delivered_count == 0
    assert received == []
    hidden = bus.get_event(
        _ctx(tenant_b, SUBSCRIBER_ID),
        event_id=published.data.event_id,
    )
    assert not hidden.ok
    assert hidden.error_code == ErrorCode.EVENT_NOT_FOUND


def test_same_tenant_event_read_requires_explicit_permission() -> None:
    tenant_id = uuid4()
    permission, bus = _services()
    _grant(permission, tenant_id, PUBLISHER_ID, "publish")
    published = bus.publish(
        _ctx(tenant_id, PUBLISHER_ID),
        event_name="crm.customer.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert published.data is not None
    denied = bus.get_event(
        _ctx(tenant_id, SUBSCRIBER_ID),
        event_id=published.data.event_id,
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
