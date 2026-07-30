"""Digital Twin service — PHX-E15 governed enterprise state snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4

from eaos_platform.twin.models import TwinSnapshot, TwinSnapshotStatus
from eaos_platform.twin.repository import InMemoryTwinRepository, TwinRepository
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

_SECRET_TOKENS = ("password", "secret", "token", "api_key", "private_key", "credential")


class TwinService:
    """Governed twin snapshots; never an execution authority."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: TwinRepository | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryTwinRepository()
        self._audit = audit_log or InMemoryAuditLog()

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def upsert_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        entity_ref: str,
        state: Mapping[str, Any],
        source_ref: str,
        reason: str,
        confidence: float,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned_entity = entity_ref.strip()
            cleaned_source = source_ref.strip()
            cleaned_reason = reason.strip()
            if not cleaned_entity:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "entity_ref is required",
                )
            if not cleaned_source or not cleaned_reason:
                raise KernelError(
                    ErrorCode.TWIN_PROVENANCE_REQUIRED,
                    "source_ref and reason are required",
                )
            if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
                raise KernelError(
                    ErrorCode.TWIN_CONFIDENCE_INVALID,
                    "confidence must be between 0 and 1",
                )
            payload = dict(state)
            self._reject_secrets(payload)
            self._require_permission(
                ctx,
                action="write",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="twin_snapshot",
                ),
            )
            now = datetime.now(timezone.utc)
            existing = self._repo.get_active_by_entity_ref(
                tenant_id=ctx.tenant_id,
                entity_ref=cleaned_entity,
            )
            if existing is not None:
                expected = existing.version
                existing.status = TwinSnapshotStatus.SUPERSEDED
                existing.updated_at = now
                existing.version = expected + 1
                self._repo.save_snapshot(existing, expected_version=expected)

            snapshot = TwinSnapshot(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                entity_ref=cleaned_entity,
                state=payload,
                source_ref=cleaned_source,
                reason=cleaned_reason,
                confidence=float(confidence),
                status=TwinSnapshotStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                valid_from=valid_from,
                valid_until=valid_until,
            )
            self._repo.add_snapshot(snapshot)
            audit = self._audit.record(
                ctx,
                action="Twin.UpsertSnapshot",
                resource=f"twin_snapshot:{snapshot.id}",
                result="ok",
                details={
                    "entity_ref": cleaned_entity,
                    "confidence": float(confidence),
                    "source_ref": cleaned_source,
                },
            )
            return KernelResult.success(snapshot.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[TwinSnapshot]:
        try:
            require_context(ctx, tenant_data_plane=True)
            snapshot = self._repo.get_snapshot(snapshot_id)
            if snapshot is None or snapshot.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.TWIN_NOT_FOUND, "twin snapshot not found")
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=snapshot.tenant_id,
                    resource_type="twin_snapshot",
                    resource_id=snapshot.id,
                ),
            )
            return KernelResult.success(snapshot)
        except KernelError as err:
            return KernelResult.from_error(err)

    def authorize_from_twin(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[bool]:
        """Permission-gated authorize open (PHX-G335); deny → TWIN_EXECUTION_FORBIDDEN."""
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            snapshot = self._repo.get_snapshot(snapshot_id)
            if snapshot is None or snapshot.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.TWIN_NOT_FOUND, "twin snapshot not found")
            decision = self._permission.evaluate(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="authorize",
                resource=Resource(
                    tenant_id=snapshot.tenant_id,
                    resource_type="twin_snapshot",
                    resource_id=snapshot.id,
                ),
            )
            allowed = (
                decision.ok
                and decision.data is not None
                and decision.data.effect == PermissionEffect.ALLOW
            )
            if not allowed:
                self._audit.record(
                    ctx,
                    action="Twin.AuthorizeFromTwin",
                    resource=f"twin_snapshot:{snapshot.id}",
                    result="denied",
                    details={"snapshot_id": str(snapshot.id)},
                )
                raise KernelError(
                    ErrorCode.TWIN_EXECUTION_FORBIDDEN,
                    "digital twin state is not execution authorization",
                    details={"snapshot_id": str(snapshot_id)},
                )
            audit = self._audit.record(
                ctx,
                action="Twin.AuthorizeFromTwin",
                resource=f"twin_snapshot:{snapshot.id}",
                result="ok",
                details={"snapshot_id": str(snapshot.id), "authorized": True},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _reject_secrets(self, payload: Mapping[str, Any]) -> None:
        for key in payload:
            normalized = str(key).strip().casefold().replace("-", "_")
            if any(token in normalized for token in _SECRET_TOKENS):
                raise KernelError(
                    ErrorCode.TWIN_SECRET_DENIED,
                    "secrets must not be stored in twin snapshots",
                )

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: Resource,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(ErrorCode.PERMISSION_DENIED, "permission denied")
