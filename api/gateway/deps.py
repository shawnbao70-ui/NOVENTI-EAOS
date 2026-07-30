"""Gateway dependencies."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from fastapi import HTTPException, Request, status

from kernel.event_bus.models import DeliveryReport, EventEnvelope
from kernel.event_bus.outbox import DeadLetterEntry, DeliveryStats, DispatchReport
from kernel.event_bus.repository import EventHandler
from kernel.identity.models import ExternalRef, Subject
from kernel.organization.models import (
    Enterprise,
    Membership,
    OrganizationStatus,
    OrganizationUnit,
    Tenant,
)
from eaos_platform.knowledge.models import (
    KnowledgeEntity,
    KnowledgeLayer,
    ProvenanceRecord,
)
from eaos_platform.brain.models import BrainInsight
from eaos_platform.package.models import (
    PackageManifest,
    ResolvedAction,
    SurfaceDeclaration,
)
from eaos_platform.twin.models import TwinSnapshot
from kernel.permission.models import Grant, PermissionDecision, PolicyRule, Resource
from kernel.shared.context import ExecutionContext
from kernel.shared.results import KernelResult
from kernel.workflow.models import TaskStatus, WorkflowInstance, WorkflowStatus, WorkflowTask
from noventi.crm.models import (
    ARInvoice,
    Contact,
    Customer,
    DeliveryOrder,
    Opportunity,
    Page,
    Quote,
    QuoteConversion,
    QuoteLine,
    Requirement,
    SalesOrder,
    SalesOrderLine,
)
from noventi.purchase.models import (
    ApBill,
    ApPayment,
    ApWriteOff,
    GoodsReceipt,
    PurchaseOrder,
    PurchaseOrderLine,
    Supplier,
    ThreeWayMatch,
)
from runtime.ai.models import AgentRun, MemoryEntry, ToolInvocationResult
from smart_terminal.models import (
    ApprovalPresentation,
    CommitReceipt,
    PlanPreview,
    TerminalIntent,
    TerminalSession,
)


class IdentityGatewayService(Protocol):
    def register_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_type: Any,
        display_name: str,
        external_refs: list[ExternalRef] | None = None,
    ) -> KernelResult[UUID]: ...

    def resolve_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        external_ref: ExternalRef | None = None,
    ) -> KernelResult[Subject]: ...

    def bind_credential(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        credential_kind: str,
        secret_handle: str,
        expires_at: Any = None,
    ) -> KernelResult[UUID]: ...

    def validate_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
    ) -> KernelResult[Any]: ...

    def revoke_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        reason: str,
    ) -> KernelResult[bool]: ...

    def create_session(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        ttl_seconds: int = 3600,
    ) -> KernelResult[dict]: ...

    def validate_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
    ) -> KernelResult[Any]: ...

    def revoke_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
        reason: str,
    ) -> KernelResult[bool]: ...

    def grant_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
    ) -> KernelResult[UUID]: ...

    def revoke_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        reason: str,
    ) -> KernelResult[bool]: ...

    def register_ai_employee(
        self,
        ctx: ExecutionContext,
        *,
        display_name: str,
        capabilities_profile: str = "default",
        owner_policy: str = "platform",
    ) -> KernelResult[UUID]: ...

    def get_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
    ) -> KernelResult[Any]: ...

    def update_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        expected_version: int,
        capabilities_profile: str,
        owner_policy: str,
    ) -> KernelResult[Any]: ...

    def assign_ai_to_tenant(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]: ...

    def reassign_ai(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        to_tenant_id: UUID | None = None,
        mode: Any = "reassign",
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]: ...


def get_identity_service(request: Request) -> IdentityGatewayService:
    service = getattr(request.app.state, "identity", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_IDENTITY_UNAVAILABLE",
                "message": "identity service is not configured on the gateway",
            },
        )
    return service


class OrganizationGatewayService(Protocol):
    def create_tenant(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
        region_policy_ref: str | None = None,
    ) -> KernelResult[UUID]: ...

    def suspend_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def reactivate_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def get_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
    ) -> KernelResult[Tenant]: ...

    def create_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
    ) -> KernelResult[UUID]: ...

    def list_enterprises(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[Enterprise]]: ...

    def get_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
    ) -> KernelResult[Enterprise]: ...

    def suspend_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def reactivate_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def close_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def upsert_unit(
        self,
        ctx: ExecutionContext,
        *,
        unit_type: Any,
        name: str,
        unit_id: UUID | None = None,
        enterprise_id: UUID | None = None,
        parent_unit_id: UUID | None = None,
        status: Any = None,
        expected_version: int | None = None,
    ) -> KernelResult[UUID]: ...

    def set_unit_status(
        self,
        ctx: ExecutionContext,
        *,
        unit_id: UUID,
        status: OrganizationStatus | str,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def get_unit_tree(
        self,
        ctx: ExecutionContext,
        *,
        root_unit_id: UUID | None = None,
    ) -> KernelResult[list[OrganizationUnit]]: ...

    def add_membership(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        membership_role_label: str | None = None,
    ) -> KernelResult[UUID]: ...

    def remove_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def suspend_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def reactivate_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def transfer_membership_unit(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        to_org_unit_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def list_memberships(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        status: OrganizationStatus | None = None,
    ) -> KernelResult[list[Membership]]: ...


def get_organization_service(request: Request) -> OrganizationGatewayService:
    service = getattr(request.app.state, "organization", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_ORGANIZATION_UNAVAILABLE",
                "message": "organization service is not configured on the gateway",
            },
        )
    return service


class PermissionGatewayService(Protocol):
    def grant_capability(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        capability: str,
        resource_type: str,
        actions: set[str] | frozenset[str],
        idempotency_key: str | None = None,
    ) -> KernelResult[UUID]: ...

    def revoke_capability(
        self,
        ctx: ExecutionContext,
        *,
        grant_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[bool]: ...

    def list_tenant_grants(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID | None = None,
    ) -> KernelResult[list[Grant]]: ...

    def create_policy(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        policy_version: str,
        rules: list[PolicyRule],
    ) -> KernelResult[UUID]: ...

    def activate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def deprecate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def grant(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str,
        actions: set[str] | frozenset[str],
        resource_id: UUID | None = None,
        scope_level: Any = None,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        conditions_ref: str | None = None,
        expires_at: Any = None,
        delegable: bool = False,
        remaining_depth: int = 0,
    ) -> KernelResult[UUID]: ...

    def revoke(
        self,
        ctx: ExecutionContext,
        *,
        grant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def delegate(
        self,
        ctx: ExecutionContext,
        *,
        parent_grant_id: UUID,
        to_principal_subject_id: UUID,
        actions: set[str] | frozenset[str] | None = None,
        scope_level: Any = None,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        resource_id: UUID | None = None,
        expires_at: Any = None,
        conditions_ref: str | None = None,
        remaining_depth: int | None = None,
        delegable: bool = False,
    ) -> KernelResult[UUID]: ...

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult[PermissionDecision]: ...

    def explain(
        self,
        ctx: ExecutionContext,
        *,
        decision_id: UUID,
    ) -> KernelResult[dict[str, str]]: ...

    def list_effective(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str | None = None,
    ) -> KernelResult[list[Grant]]: ...


def get_permission_service(request: Request) -> PermissionGatewayService:
    service = getattr(request.app.state, "permission", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_PERMISSION_UNAVAILABLE",
                "message": "permission service is not configured on the gateway",
            },
        )
    return service


class WorkflowGatewayService(Protocol):
    def register_definition(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        definition_document_ref: str,
        version: str,
    ) -> KernelResult[UUID]: ...

    def deprecate_definition(
        self,
        ctx: ExecutionContext,
        *,
        definition_id: UUID,
    ) -> KernelResult[bool]: ...

    def start(
        self,
        ctx: ExecutionContext,
        *,
        definition_id: UUID,
        payload: dict[str, Any],
        business_key: str | None = None,
        initiator_subject_id: UUID | None = None,
        approval_subject_id: UUID | None = None,
        approval_principal_subject_id: UUID | None = None,
        approval_action: str | None = None,
        approval_resource_ref: str | None = None,
        approval_plan_version: str | None = None,
        approval_scope: str | None = None,
        approval_expires_at: Any = None,
        due_at: Any = None,
    ) -> KernelResult[dict[str, Any]]: ...

    def get_instance(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
    ) -> KernelResult[WorkflowInstance]: ...

    def approve(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        comment: str | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def reject(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def signal(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        signal_name: str,
        idempotency_key: str,
        payload: dict[str, Any] | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def cancel(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def compensate(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def escalate(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        to_subject_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]: ...

    def list_tasks(
        self,
        ctx: ExecutionContext,
        *,
        assignee_subject_id: UUID | None = None,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> KernelResult[list[WorkflowTask]]: ...

    def verify_approved_action(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]: ...


def get_workflow_service(request: Request) -> WorkflowGatewayService:
    service = getattr(request.app.state, "workflow", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_WORKFLOW_UNAVAILABLE",
                "message": "workflow service is not configured on the gateway",
            },
        )
    return service


class KnowledgeGatewayService(Protocol):
    def upsert_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str,
        name: str,
        layer: KnowledgeLayer,
        attributes: dict[str, Any] | None = None,
        labels: set[str] | frozenset[str] | None = None,
        source_ref: str,
        reason: str,
        retain_until: Any = None,
        entity_id: UUID | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[UUID]: ...

    def get_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]: ...

    def query(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str | None = None,
        layer: KnowledgeLayer | None = None,
        include_archived: bool = False,
    ) -> KernelResult[list[KnowledgeEntity]]: ...

    def search(
        self,
        ctx: ExecutionContext,
        *,
        text: str,
    ) -> KernelResult[list[KnowledgeEntity]]: ...

    def link(
        self,
        ctx: ExecutionContext,
        *,
        from_entity_id: UUID,
        to_entity_id: UUID,
        relation_type: str,
        source_ref: str,
        reason: str,
        attributes: dict[str, Any] | None = None,
    ) -> KernelResult[UUID]: ...

    def get_provenance(
        self,
        ctx: ExecutionContext,
        *,
        subject_kind: str,
        subject_id: UUID,
    ) -> KernelResult[list[ProvenanceRecord]]: ...

    def archive_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
        reason: str,
        source_ref: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...

    def share(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
        share_with_subject_id: UUID,
        source_ref: str,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]: ...


def get_knowledge_service(request: Request) -> KnowledgeGatewayService:
    service = getattr(request.app.state, "knowledge", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_KNOWLEDGE_UNAVAILABLE",
                "message": "knowledge service is not configured on the gateway",
            },
        )
    return service


class CRMGatewayService(Protocol):
    def create_customer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Customer]: ...

    def get_customer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Customer]: ...

    def list_customers(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[Customer]]: ...

    def update_customer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Customer]: ...

    def archive_customer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Customer]: ...

    def set_customer_commercial_hold(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Customer]: ...

    def create_contact(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Contact]: ...

    def get_contact(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Contact]: ...

    def list_contacts(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[Contact]]: ...

    def update_contact(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Contact]: ...

    def archive_contact(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Contact]: ...

    def create_opportunity(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Opportunity]: ...

    def get_opportunity(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Opportunity]: ...

    def list_opportunities(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[Opportunity]]: ...

    def update_opportunity(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Opportunity]: ...

    def archive_opportunity(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Opportunity]: ...

    def create_requirement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Requirement]: ...

    def get_requirement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Requirement]: ...

    def list_requirements(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[Requirement]]: ...

    def update_requirement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Requirement]: ...

    def archive_requirement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Requirement]: ...

    def create_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Quote]: ...

    def get_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Quote]: ...

    def list_quotes(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[Quote]]: ...

    def update_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Quote]: ...

    def archive_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Quote]: ...

    def issue_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Quote]: ...

    def convert_quote(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteConversion]: ...

    def get_conversion(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteConversion]: ...

    def create_sales_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[SalesOrder]: ...

    def get_sales_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[SalesOrder]: ...

    def list_sales_orders(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Page[SalesOrder]]: ...

    def create_quote_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteLine]: ...

    def get_quote_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteLine]: ...

    def list_quote_lines(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[list[QuoteLine]]: ...

    def update_quote_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteLine]: ...

    def archive_quote_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[QuoteLine]: ...

    def confirm_sales_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[SalesOrder]: ...

    def list_sales_order_lines(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[list[SalesOrderLine]]: ...

    def create_delivery_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[DeliveryOrder]: ...

    def get_delivery_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[DeliveryOrder]: ...

    def release_delivery_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[DeliveryOrder]: ...

    def create_ar_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ARInvoice]: ...

    def issue_ar_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ARInvoice]: ...

    def void_ar_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ARInvoice]: ...

    def get_ar_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ARInvoice]: ...

    def create_return_authorization(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_return_authorization(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def restock_return_authorization(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_credit_note_from_return_authorization(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_confirm_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_confirm_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_quote_issue_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_quote_issue_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_quote_convert_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_quote_convert_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_so_confirm_workflow_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_so_confirm_workflow_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_do_ship_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_do_ship_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_do_release_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_do_release_approval_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...


def get_crm_service(request: Request) -> CRMGatewayService:
    service = getattr(request.app.state, "crm", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_CRM_UNAVAILABLE",
                "message": "CRM service is not configured on the gateway",
            },
        )
    return service


class Customer360GatewayService(Protocol):
    def get_customer360(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[Any]: ...


def get_customer360_service(request: Request) -> Customer360GatewayService:
    service = getattr(request.app.state, "customer360", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_CUSTOMER360_UNAVAILABLE",
                "message": "Customer360 service is not configured on the gateway",
            },
        )
    return service


class Supplier360GatewayService(Protocol):
    def get_supplier360(
        self, ctx: ExecutionContext, supplier_id: UUID
    ) -> KernelResult[Any]: ...


def get_supplier360_service(request: Request) -> Supplier360GatewayService:
    service = getattr(request.app.state, "supplier360", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_SUPPLIER360_UNAVAILABLE",
                "message": "Supplier360 service is not configured on the gateway",
            },
        )
    return service


class CustomerAdvisoryGatewayService(Protocol):
    def get_customer_advisory(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[Any]: ...


def get_customer_advisory_service(
    request: Request,
) -> CustomerAdvisoryGatewayService:
    service = getattr(request.app.state, "customer_advisory", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_CUSTOMER_ADVISORY_UNAVAILABLE",
                "message": "Customer advisory service is not configured on the gateway",
            },
        )
    return service


class FinanceGatewayService(Protocol):
    def get_customer_balance(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_ar_write_off(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def close_ar_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_receipt(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def apply_receipt_to_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def allocate_receipt_to_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def list_receipt_allocations(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_receipt(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_receipt_psp_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_receipt_psp_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_tax_authority_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_tax_authority_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_credit_note(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def issue_credit_note(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_credit_note(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_ar_refund(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def post_ar_refund(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def post_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def link_tax_invoice_to_credit_note(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_tax_credit_link(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_tax_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_tax_red_credit(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def issue_tax_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def void_tax_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_tax_invoice(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_tax_rate(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_tax_rate(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_tax_rate_by_code(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def archive_tax_rate(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def accrue_commission(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def mark_commission_payable(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def mark_commission_paid(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_commission(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_gl_account(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_gl_account(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_gl_account_by_code(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def archive_gl_account(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_gl_period(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_gl_period(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_gl_period_by_code(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def close_gl_period(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_journal_entry(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_journal_entry(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def post_journal_entry(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_gl_bridge_map(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_gl_bridge_map(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_ar_invoice_issue(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_ar_receipt_apply(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_ap_bill_post(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_ap_payment_apply(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_tax_invoice_issue(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_commission_accrue(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def bridge_realized_fx(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def post_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_bank_statement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_bank_statement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def match_bank_statement_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def clear_bank_statement(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...


def get_finance_service(request: Request) -> FinanceGatewayService:
    service = getattr(request.app.state, "finance", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_FINANCE_UNAVAILABLE",
                "message": "Finance service is not configured on the gateway",
            },
        )
    return service


class InventoryGatewayService(Protocol):
    def adjust_stock(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_stock_balance(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def ship_delivery_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def unship_delivery_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_ship_posting(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_ship_pod_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_ship_pod_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...


def get_inventory_service(request: Request) -> InventoryGatewayService:
    service = getattr(request.app.state, "inventory", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_INVENTORY_UNAVAILABLE",
                "message": "Inventory service is not configured on the gateway",
            },
        )
    return service


class PurchaseGatewayService(Protocol):
    def get_supplier_balance(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_supplier(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Supplier]: ...

    def get_supplier(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Supplier]: ...

    def update_supplier(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Supplier]: ...

    def archive_supplier(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Supplier]: ...

    def create_ap_bill(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApBill]: ...

    def get_ap_bill(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApBill]: ...

    def post_ap_bill(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApBill]: ...

    def create_ap_write_off(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApWriteOff]: ...

    def close_ap_bill(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApBill]: ...

    def create_ap_payment(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApPayment]: ...

    def get_ap_payment(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApPayment]: ...

    def apply_ap_payment_to_bill(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ApPayment]: ...

    def create_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def get_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def list_ap_bill_lines(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def archive_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def create_purchase_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[PurchaseOrder]: ...

    def get_purchase_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[PurchaseOrder]: ...

    def archive_purchase_order(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[PurchaseOrder]: ...

    def create_purchase_order_line(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[PurchaseOrderLine]: ...

    def create_goods_receipt(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[GoodsReceipt]: ...

    def create_three_way_match(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[ThreeWayMatch]: ...

    def get_three_way_match_tolerance_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def set_three_way_match_tolerance_policy(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...


def get_purchase_service(request: Request) -> PurchaseGatewayService:
    service = getattr(request.app.state, "purchase", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_PURCHASE_UNAVAILABLE",
                "message": "Purchase service is not configured on the gateway",
            },
        )
    return service


class EventGatewayService(Protocol):
    def subscribe(
        self,
        ctx: ExecutionContext,
        *,
        subscriber_id: str,
        event_name: str,
        handler: EventHandler | None = None,
        delivery_url: str | None = None,
        signing_secret: str | None = None,
    ) -> KernelResult[UUID]: ...

    def publish(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: dict[str, Any],
    ) -> KernelResult[DeliveryReport]: ...

    def enqueue(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: dict[str, Any],
    ) -> KernelResult[UUID]: ...

    def dispatch_due(
        self,
        ctx: ExecutionContext,
        *,
        worker_id: str,
        limit: int = 32,
        now: Any = None,
    ) -> KernelResult[DispatchReport]: ...

    def get_delivery_stats(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[DeliveryStats]: ...

    def list_dead_letters(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[DeadLetterEntry]]: ...

    def replay_dead_letter(
        self,
        ctx: ExecutionContext,
        *,
        dead_letter_id: UUID,
    ) -> KernelResult[bool]: ...

    def replay(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[DeliveryReport]: ...

    def get_event(
        self,
        ctx: ExecutionContext,
        *,
        event_id: UUID,
    ) -> KernelResult[EventEnvelope]: ...


def get_event_service(request: Request) -> EventGatewayService:
    service = getattr(request.app.state, "event_bus", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_EVENT_UNAVAILABLE",
                "message": "event bus is not configured on the gateway",
            },
        )
    return service


class PackageGatewayService(Protocol):
    def register_manifest(
        self,
        ctx: ExecutionContext,
        *,
        package_key: str,
        version: str,
        package_type: str,
        surfaces: list[dict[str, str]] | None = None,
        actions: list[dict[str, object]] | None = None,
        required_permissions: list[dict[str, object]] | None = None,
        declared_events: list[str] | None = None,
    ) -> KernelResult[UUID]: ...

    def publish_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[bool]: ...

    def get_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[PackageManifest]: ...

    def install_package(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[UUID]: ...

    def disable_installation(
        self,
        ctx: ExecutionContext,
        *,
        installation_id: UUID,
    ) -> KernelResult[bool]: ...

    def list_surfaces(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[SurfaceDeclaration]]: ...

    def resolve_action(
        self,
        ctx: ExecutionContext,
        *,
        action_key: str,
    ) -> KernelResult[ResolvedAction]: ...


def get_package_service(request: Request) -> PackageGatewayService:
    service = getattr(request.app.state, "package", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_PACKAGE_UNAVAILABLE",
                "message": "package service is not configured on the gateway",
            },
        )
    return service


class TwinGatewayService(Protocol):
    def upsert_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        entity_ref: str,
        state: dict[str, Any],
        source_ref: str,
        reason: str,
        confidence: float,
        valid_from: Any = None,
        valid_until: Any = None,
    ) -> KernelResult[UUID]: ...

    def get_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[TwinSnapshot]: ...

    def authorize_from_twin(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[bool]: ...


def get_twin_service(request: Request) -> TwinGatewayService:
    service = getattr(request.app.state, "twin", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TWIN_UNAVAILABLE",
                "message": "twin service is not configured on the gateway",
            },
        )
    return service


class BrainGatewayService(Protocol):
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
        details: dict[str, Any] | None = None,
        advisory: bool = True,
    ) -> KernelResult[UUID]: ...

    def get_insight(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[BrainInsight]: ...

    def request_execution(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[bool]: ...


def get_brain_service(request: Request) -> BrainGatewayService:
    service = getattr(request.app.state, "brain", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_BRAIN_UNAVAILABLE",
                "message": "brain service is not configured on the gateway",
            },
        )
    return service


class CommercialHandoffGatewayService(Protocol):
    def handoff_rma_credit_note(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...

    def handoff_so_confirm(
        self, ctx: ExecutionContext, **kwargs: Any
    ) -> KernelResult[Any]: ...


def get_commercial_handoff_service(
    request: Request,
) -> CommercialHandoffGatewayService:
    service = getattr(request.app.state, "commercial_handoff", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_COMMERCIAL_HANDOFF_UNAVAILABLE",
                "message": "commercial handoff service is not configured on the gateway",
            },
        )
    return service


class AIRuntimeGatewayService(Protocol):
    def create_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        goal: str,
        plan_summary: str = "",
    ) -> KernelResult[UUID]: ...

    def get_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
    ) -> KernelResult[AgentRun]: ...

    def register_tool(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        description: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]: ...

    def invoke_tool(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[ToolInvocationResult]: ...

    def write_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
        value: dict[str, Any],
    ) -> KernelResult[UUID]: ...

    def read_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
    ) -> KernelResult[MemoryEntry]: ...

    def request_approval(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        definition_id: UUID,
        approval_subject_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[UUID]: ...

    def commit_action(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]: ...


def get_ai_service(request: Request) -> AIRuntimeGatewayService:
    service = getattr(request.app.state, "ai", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_AI_UNAVAILABLE",
                "message": "ai runtime is not configured on the gateway",
            },
        )
    return service


class TerminalGatewayService(Protocol):
    def open_session(
        self,
        ctx: ExecutionContext,
        *,
        device_trust: str = "trusted",
        claimed_tenant_id: UUID | None = None,
        claimed_subject_id: UUID | None = None,
    ) -> KernelResult[UUID]: ...

    def get_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[TerminalSession]: ...

    def close_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[bool]: ...

    def compose_intent(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
        text: str,
    ) -> KernelResult[UUID]: ...

    def get_intent(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
    ) -> KernelResult[TerminalIntent]: ...

    def build_preview(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str,
        scope: str,
        impact_summary: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]: ...

    def get_preview(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[PlanPreview]: ...

    def request_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
        definition_id: UUID,
        approval_subject_id: UUID,
    ) -> KernelResult[UUID]: ...

    def present_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[ApprovalPresentation]: ...

    def commit(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[CommitReceipt]: ...

    def register_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_key: str,
        version: str,
        signature_ref: str | None = None,
        declared_capabilities: list[str] | None = None,
        declared_actions: list[str] | None = None,
        allowed_surfaces: list[str] | None = None,
        data_scope: str = "",
    ) -> KernelResult[UUID]: ...

    def activate_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]: ...

    def revoke_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]: ...

    def list_extensions(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[Any]]: ...

    def invoke_extension_action(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
        action: str,
        surface: str,
    ) -> KernelResult[dict[str, object]]: ...


def get_terminal_service(request: Request) -> TerminalGatewayService:
    service = getattr(request.app.state, "terminal", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TERMINAL_UNAVAILABLE",
                "message": "terminal service is not configured on the gateway",
            },
        )
    return service


class MarketplaceGatewayService(Protocol):
    def create_listing(
        self,
        ctx: ExecutionContext,
        *,
        package_key: str,
        package_version: str,
        required_permissions: list[str],
        declared_events: list[str],
        data_scope: str,
    ) -> KernelResult[UUID]: ...

    def attach_signature(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        signature_ref: str,
    ) -> KernelResult[bool]: ...

    def submit_for_review(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]: ...

    def review_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        approve: bool,
        notes: str = "",
    ) -> KernelResult[bool]: ...

    def publish_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]: ...

    def revoke_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]: ...

    def get_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[Any]: ...

    def acquire_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]: ...

    def set_pricing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        price: str,
        currency: str | None = None,
    ) -> KernelResult[bool]: ...

    def create_invoice(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]: ...

    def open_dispute(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        reason: str,
    ) -> KernelResult[UUID]: ...

    def resolve_dispute(
        self,
        ctx: ExecutionContext,
        *,
        dispute_id: UUID,
        resolution: str,
    ) -> KernelResult[bool]: ...

    def set_revenue_share(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        platform_share_bps: int | None = None,
        share_ratio: float | None = None,
    ) -> KernelResult[bool]: ...


def get_marketplace_service(request: Request) -> MarketplaceGatewayService:
    service = getattr(request.app.state, "marketplace", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_MARKETPLACE_UNAVAILABLE",
                "message": "marketplace service is not configured on the gateway",
            },
        )
    return service
