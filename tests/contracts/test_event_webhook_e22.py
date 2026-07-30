"""PHX-E22 Event webhook HMAC contracts."""

from __future__ import annotations

from uuid import uuid4

from kernel.event_bus.bus import EventBus
from kernel.event_bus.webhook import (
    SIGNATURE_HEADER,
    TIMESTAMP_HEADER,
    RecordingWebhookPoster,
    serialize_webhook_body,
    verify_webhook_signature,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()
SECRET = "eaos-webhook-test-secret"


class _AllowAll:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ACTOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _admin() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _bus(poster: RecordingWebhookPoster) -> EventBus:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    assert permission.grant(
        _admin(),
        principal_subject_id=ACTOR,
        resource_type="event_stream",
        actions={"subscribe", "publish", "dispatch", "read"},
    ).ok
    return EventBus(permission, webhook_poster=poster)


def test_signed_webhook_dispatch_verifies() -> None:
    poster = RecordingWebhookPoster()
    bus = _bus(poster)
    ctx = _ctx()
    assert bus.subscribe(
        ctx,
        subscriber_id="webhook.signed",
        event_name="organization.tenant.created",
        delivery_url="https://hooks.example.com/signed",
        signing_secret=SECRET,
    ).ok
    assert bus.enqueue(
        ctx,
        event_name="organization.tenant.created",
        schema_version="1",
        producer="organization.kernel",
        payload={"tenant_id": str(TENANT)},
    ).ok
    assert bus.dispatch_due(ctx, worker_id="worker-e22", limit=8).ok
    assert len(poster.calls) == 1
    call = poster.calls[0]
    body = serialize_webhook_body(call["payload"])
    assert verify_webhook_signature(
        secret=SECRET,
        body=body,
        timestamp=call["headers"][TIMESTAMP_HEADER],
        signature_header=call["headers"][SIGNATURE_HEADER],
    )


def test_signing_secret_requires_delivery_url() -> None:
    bus = _bus(RecordingWebhookPoster())
    denied = bus.subscribe(
        _ctx(),
        subscriber_id="no.url",
        event_name="organization.tenant.created",
        handler=lambda _event: None,
        signing_secret=SECRET,
    )
    assert denied.error_code == ErrorCode.EVENT_SUBSCRIPTION_INVALID


def test_short_signing_secret_rejected() -> None:
    bus = _bus(RecordingWebhookPoster())
    denied = bus.subscribe(
        _ctx(),
        subscriber_id="short.secret",
        event_name="organization.tenant.created",
        delivery_url="https://hooks.example.com/x",
        signing_secret="too-short",
    )
    assert denied.error_code == ErrorCode.EVENT_SUBSCRIPTION_INVALID
