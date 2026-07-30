"""Enterprise Brain service — PHX-E15 advisory insights only."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid4

from eaos_platform.brain.models import BrainInsight, InsightKind
from eaos_platform.brain.repository import BrainRepository, InMemoryBrainRepository
from eaos_platform.twin.models import TwinSnapshot
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

_SECRET_TOKENS = ("password", "secret", "token", "api_key", "private_key", "credential")


class TwinReader(Protocol):
    def get_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[TwinSnapshot]: ...


class BrainService:
    """Advisory enterprise intelligence; never an execution authority."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: BrainRepository | None = None,
        audit_log: AuditLog | None = None,
        twin_reader: TwinReader | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryBrainRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._twin = twin_reader

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def publish_insight(
        self,
        ctx: ExecutionContext,
        *,
        kind: str,
        summary: str,
        confidence: float,
        source_ref: str,
        reason: str,
        bias_notes: str = "",
        twin_ref: UUID | None = None,
        knowledge_refs: list[str] | None = None,
        details: Mapping[str, Any] | None = None,
        advisory: bool = True,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if not advisory:
                raise KernelError(
                    ErrorCode.BRAIN_ADVISORY_REQUIRED,
                    "enterprise brain outputs must remain advisory",
                )
            try:
                insight_kind = InsightKind(kind.strip().casefold())
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "kind must be insight, recommendation, or simulation",
                ) from exc
            cleaned_summary = summary.strip()
            cleaned_source = source_ref.strip()
            cleaned_reason = reason.strip()
            if not cleaned_summary:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "summary is required",
                )
            if not cleaned_source or not cleaned_reason:
                raise KernelError(
                    ErrorCode.BRAIN_PROVENANCE_REQUIRED,
                    "source_ref and reason are required",
                )
            if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
                raise KernelError(
                    ErrorCode.BRAIN_CONFIDENCE_INVALID,
                    "confidence must be between 0 and 1",
                )
            payload = dict(details or {})
            self._reject_secrets(payload)
            self._reject_secrets({"summary": cleaned_summary, "bias_notes": bias_notes})

            self._require_permission(
                ctx,
                action="publish",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="brain_insight",
                ),
            )
            if twin_ref is not None:
                if self._twin is None:
                    raise KernelError(
                        ErrorCode.TWIN_NOT_FOUND,
                        "twin reader is not configured",
                    )
                twin = self._twin.get_snapshot(ctx, snapshot_id=twin_ref)
                if not twin.ok or twin.data is None:
                    raise KernelError(
                        twin.error_code or ErrorCode.TWIN_NOT_FOUND,
                        twin.error_message or "twin snapshot not readable",
                    )

            now = datetime.now(timezone.utc)
            insight = BrainInsight(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                kind=insight_kind,
                summary=cleaned_summary,
                confidence=float(confidence),
                source_ref=cleaned_source,
                reason=cleaned_reason,
                advisory=True,
                created_at=now,
                updated_at=now,
                bias_notes=bias_notes.strip(),
                twin_ref=twin_ref,
                knowledge_refs=[item.strip() for item in (knowledge_refs or []) if item.strip()],
                details=payload,
            )
            self._repo.add_insight(insight)
            audit = self._audit.record(
                ctx,
                action="Brain.PublishInsight",
                resource=f"brain_insight:{insight.id}",
                result="ok",
                details={
                    "kind": insight_kind.value,
                    "confidence": float(confidence),
                    "advisory": True,
                    "twin_ref": str(twin_ref) if twin_ref else None,
                },
            )
            return KernelResult.success(insight.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_insight(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[BrainInsight]:
        try:
            require_context(ctx, tenant_data_plane=True)
            insight = self._repo.get_insight(insight_id)
            if insight is None or insight.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.BRAIN_NOT_FOUND, "brain insight not found")
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=insight.tenant_id,
                    resource_type="brain_insight",
                    resource_id=insight.id,
                ),
            )
            return KernelResult.success(insight)
        except KernelError as err:
            return KernelResult.from_error(err)

    def request_execution(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[bool]:
        """Permission-gated execute open (PHX-G335); deny → BRAIN_EXECUTION_FORBIDDEN."""
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            insight = self._repo.get_insight(insight_id)
            if insight is None or insight.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.BRAIN_NOT_FOUND, "brain insight not found")
            decision = self._permission.evaluate(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="execute",
                resource=Resource(
                    tenant_id=insight.tenant_id,
                    resource_type="brain_insight",
                    resource_id=insight.id,
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
                    action="Brain.RequestExecution",
                    resource=f"brain_insight:{insight.id}",
                    result="denied",
                    details={"insight_id": str(insight.id)},
                )
                raise KernelError(
                    ErrorCode.BRAIN_EXECUTION_FORBIDDEN,
                    "enterprise brain insights are advisory and cannot authorize execution",
                    details={"insight_id": str(insight_id)},
                )
            audit = self._audit.record(
                ctx,
                action="Brain.RequestExecution",
                resource=f"brain_insight:{insight.id}",
                result="ok",
                details={"insight_id": str(insight.id), "authorized": True},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _reject_secrets(self, payload: Mapping[str, Any]) -> None:
        for key in payload:
            normalized = str(key).strip().casefold().replace("-", "_")
            if any(token in normalized for token in _SECRET_TOKENS):
                raise KernelError(
                    ErrorCode.BRAIN_SECRET_DENIED,
                    "secrets must not be stored in brain insights",
                )
            value = payload[key]
            if isinstance(value, str):
                lowered = value.casefold()
                if any(token in lowered for token in _SECRET_TOKENS):
                    raise KernelError(
                        ErrorCode.BRAIN_SECRET_DENIED,
                        "secrets must not be stored in brain insights",
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
