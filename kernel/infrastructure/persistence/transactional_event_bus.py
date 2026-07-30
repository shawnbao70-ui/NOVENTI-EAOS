"""Transactional SQLAlchemy composition for Event Bus operations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.event_bus.bus import EventBus
from kernel.event_bus.handlers import EventHandlerRegistry
from kernel.event_bus.models import DeliveryReport, EventEnvelope
from kernel.event_bus.outbox import DeadLetterEntry, DeliveryStats, DispatchReport
from kernel.event_bus.repository import EventHandler
from kernel.event_bus.webhook import WebhookPoster
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.event_repository import SQLAlchemyEventRepository
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalEventBus:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        handler_registry: EventHandlerRegistry | None = None,
        webhook_poster: WebhookPoster | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._handler_registry = handler_registry or EventHandlerRegistry()
        self._webhook_poster = webhook_poster

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
        return self._execute(
            ctx,
            lambda bus: bus.subscribe(
                ctx,
                subscriber_id=subscriber_id,
                event_name=event_name,
                handler=handler,
                delivery_url=delivery_url,
                signing_secret=signing_secret,
            ),
            conflict_code=ErrorCode.EVENT_SUBSCRIPTION_INVALID,
        )

    def publish(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: Mapping[str, Any],
    ) -> KernelResult[DeliveryReport]:
        return self._execute(
            ctx,
            lambda bus: bus.publish(
                ctx,
                event_name=event_name,
                schema_version=schema_version,
                producer=producer,
                payload=payload,
            ),
        )

    def enqueue(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: Mapping[str, Any],
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda bus: bus.enqueue(
                ctx,
                event_name=event_name,
                schema_version=schema_version,
                producer=producer,
                payload=payload,
            ),
        )

    def dispatch_due(
        self,
        ctx: ExecutionContext,
        *,
        worker_id: str,
        limit: int = 32,
        now: datetime | None = None,
    ) -> KernelResult[DispatchReport]:
        return self._execute(
            ctx,
            lambda bus: bus.dispatch_due(
                ctx,
                worker_id=worker_id,
                limit=limit,
                now=now,
            ),
        )

    def get_delivery_stats(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[DeliveryStats]:
        return self._execute(
            ctx,
            lambda bus: bus.get_delivery_stats(ctx),
        )

    def list_dead_letters(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[DeadLetterEntry]]:
        return self._execute(
            ctx,
            lambda bus: bus.list_dead_letters(ctx),
        )

    def replay_dead_letter(
        self,
        ctx: ExecutionContext,
        *,
        dead_letter_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda bus: bus.replay_dead_letter(
                ctx,
                dead_letter_id=dead_letter_id,
            ),
        )

    def replay(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[DeliveryReport]:
        return self._execute(
            ctx,
            lambda bus: bus.replay(ctx, event_id=event_id),
        )

    def get_event(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[EventEnvelope]:
        return self._execute(
            ctx,
            lambda bus: bus.get_event(ctx, event_id=event_id),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[EventBus], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "event persistence requires tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                event_repository = SQLAlchemyEventRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                    handler_registry=self._handler_registry,
                    webhook_poster=self._webhook_poster,
                )
                permission_repository = SQLAlchemyPermissionRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                result = operation(
                    EventBus(
                        PermissionService(
                            repository=permission_repository,
                            audit_log=audit_log,
                            principal_eligibility=SQLAlchemyPrincipalEligibility(
                                unit_of_work.session
                            ),
                        ),
                        repository=event_repository,
                        audit_log=audit_log,
                        webhook_poster=self._webhook_poster,
                    )
                )
                if not result.ok:
                    if result.error_code == ErrorCode.PERMISSION_DENIED:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                event_repository.activate_pending_handlers()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "event persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "event persistence operation failed",
            )
