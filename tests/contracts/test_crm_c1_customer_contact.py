"""PHX-G294 CRM Customer + Contact C1 package contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CONTACT_RESOURCE, CUSTOMER_RESOURCE, CRMService


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=f"corr-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext,
    *,
    grant: bool,
) -> tuple[CRMService, InMemoryCRMRepository, InMemoryAuditLog]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        for resource_type in (CUSTOMER_RESOURCE, CONTACT_RESOURCE):
            result = permission.grant(
                ctx,
                principal_subject_id=ctx.subject_id,
                resource_type=resource_type,
                actions={"create", "read", "update", "archive"},
                scope_level=ScopeLevel.TENANT,
            )
            assert result.ok
    repository = InMemoryCRMRepository(tenant_id=ctx.tenant_id)
    return (
        CRMService(permission, repository=repository, audit_log=audit),
        repository,
        audit,
    )


def test_c1_default_deny_and_owner_never_authorizes() -> None:
    ctx = _ctx(uuid4())
    service, repository, audit = _service(ctx, grant=False)

    denied = service.create_customer(
        ctx,
        code="C-001",
        display_name="Denied Customer",
        owner_subject_id=ctx.subject_id,
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    assert repository.get_customer(uuid4()) is None
    crm_events = [event for event in audit.list_events() if event.action.startswith("CRM.")]
    assert [event.result for event in crm_events] == ["attempted", "denied"]


def test_c1_customer_contact_lifecycle_is_audited_without_pii() -> None:
    ctx = _ctx(uuid4())
    service, _, audit = _service(ctx, grant=True)
    customer = service.create_customer(
        ctx,
        code="C-100",
        display_name="Acme",
        owner_subject_id=uuid4(),
    )
    assert customer.ok and customer.data is not None
    contact = service.create_contact(
        ctx,
        customer_id=customer.data.id,
        display_name="Ada",
        title="Operations",
        email="ada@example.test",
        phone="+1-555-0100",
    )
    assert contact.ok and contact.data is not None

    updated = service.update_contact(
        ctx,
        customer_id=customer.data.id,
        contact_id=contact.data.id,
        display_name="Ada Lovelace",
        title=None,
        email="ada@example.test",
        phone=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived_customer = service.archive_customer(
        ctx,
        customer_id=customer.data.id,
        reason="account retired",
        expected_version=1,
    )
    assert archived_customer.ok

    retained_contact = service.get_contact(
        ctx,
        customer_id=customer.data.id,
        contact_id=contact.data.id,
    )
    assert retained_contact.ok
    audit_text = repr([event.details for event in audit.list_events()])
    assert "ada@example.test" not in audit_text
    assert "+1-555-0100" not in audit_text


def test_c1_cross_tenant_resource_is_not_visible() -> None:
    subject = uuid4()
    tenant_a = uuid4()
    tenant_b = uuid4()
    service_a, _, _ = _service(_ctx(tenant_a, subject), grant=True)
    ctx_a = _ctx(tenant_a, subject)
    created = service_a.create_customer(
        ctx_a,
        code="A-1",
        display_name="Tenant A",
    )
    assert created.ok and created.data is not None

    ctx_b = _ctx(tenant_b, subject)
    service_b, _, _ = _service(ctx_b, grant=True)
    hidden = service_b.get_customer(ctx_b, customer_id=created.data.id)
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND
