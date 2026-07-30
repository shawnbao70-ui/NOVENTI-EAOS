"""EAOS FastAPI gateway application (PHX-G18 / G20–G35)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api.adapters import list_adapters
from api.gateway.context import (
    derive_tenant_context,
    reject_body_elevation,
    serialize_context,
)
from api.gateway.schemas.ops import (
    AdaptersEnvelope,
    ContextEchoEnvelope,
    ContextEchoRequest,
    ContextEnvelope,
    HealthEnvelope,
    ReleaseEnvelope,
)
from api.gateway.deploy_region import deploy_region
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.production_auth import validate_production_auth
from api.gateway.sample_knowledge_pack import sample_knowledge_pack_product_posture
from api.gateway.deps import (
    AIRuntimeGatewayService,
    BrainGatewayService,
    CommercialHandoffGatewayService,
    CRMGatewayService,
    Customer360GatewayService,
    CustomerAdvisoryGatewayService,
    FinanceGatewayService,
    InventoryGatewayService,
    PurchaseGatewayService,
    Supplier360GatewayService,
    EventGatewayService,
    IdentityGatewayService,
    KnowledgeGatewayService,
    MarketplaceGatewayService,
    OrganizationGatewayService,
    PackageGatewayService,
    PermissionGatewayService,
    TerminalGatewayService,
    TwinGatewayService,
    WorkflowGatewayService,
)
from api.gateway.routers.ai import router as ai_router
from api.gateway.routers.auth import idp_router as auth_idp_router
from api.gateway.routers.auth import jwt_router as auth_jwt_router
from api.gateway.routers.auth import router as auth_router
from api.gateway.routers.webauthn import router as auth_webauthn_router
from api.gateway.routers.brain import router as brain_router
from api.gateway.routers.commercial_handoff import router as commercial_handoff_router
from api.gateway.routers.ai_workforce import router as ai_workforce_router
from api.gateway.routers.digital_employee import router as digital_employee_router
from api.gateway.routers.industry_package import router as industry_package_router
from api.gateway.routers.crm import conversion_router as crm_conversion_router
from api.gateway.routers.crm import ar_invoice_router as crm_ar_invoice_router
from api.gateway.routers.crm import delivery_order_router as crm_delivery_order_router
from api.gateway.routers.crm import opportunity_router as crm_opportunity_router
from api.gateway.routers.crm import policy_router as crm_policy_router
from api.gateway.routers.crm import quote_router as crm_quote_router
from api.gateway.routers.crm import requirement_router as crm_requirement_router
from api.gateway.routers.crm import (
    return_authorization_router as crm_return_authorization_router,
)
from api.gateway.routers.crm import router as crm_router
from api.gateway.routers.crm import sales_order_router as crm_sales_order_router
from api.gateway.routers.finance import (
    adapter_router as finance_adapter_router,
)
from api.gateway.routers.finance import (
    status_router as finance_status_router,
)
from api.gateway.routers.finance import (
    commission_router as finance_commission_router,
)
from api.gateway.routers.finance import (
    ar_invoice_close_router as finance_ar_invoice_close_router,
)
from api.gateway.routers.finance import (
    ar_write_off_router as finance_ar_write_off_router,
)
from api.gateway.routers.finance import (
    ar_refund_router as finance_ar_refund_router,
)
from api.gateway.routers.finance import (
    treasury_transfer_router as finance_treasury_transfer_router,
)
from api.gateway.routers.finance import credit_note_router as finance_credit_note_router
from api.gateway.routers.finance import policy_router as finance_policy_router
from api.gateway.routers.finance import router as finance_router
from api.gateway.routers.finance import (
    tax_credit_link_router as finance_tax_credit_link_router,
)
from api.gateway.routers.finance import (
    tax_invoice_router as finance_tax_invoice_router,
)
from api.gateway.routers.finance import (
    gl_account_router as finance_gl_account_router,
)
from api.gateway.routers.finance import (
    gl_period_router as finance_gl_period_router,
)
from api.gateway.routers.finance import (
    journal_entry_router as finance_journal_entry_router,
)
from api.gateway.routers.finance import (
    gl_bridge_map_router as finance_gl_bridge_map_router,
)
from api.gateway.routers.finance import (
    gl_bridge_router as finance_gl_bridge_router,
)
from api.gateway.routers.finance import (
    gl_fx_revaluation_router as finance_gl_fx_revaluation_router,
)
from api.gateway.routers.finance import (
    bank_statement_router as finance_bank_statement_router,
)
from api.gateway.routers.finance import (
    tax_rate_router as finance_tax_rate_router,
)
from api.gateway.routers.inventory import (
    policy_router as inventory_policy_router,
    router as inventory_router,
)
from api.gateway.routers.purchase import (
    ap_bill_router as purchase_ap_bill_router,
    ap_payment_router as purchase_ap_payment_router,
    ap_write_off_router as purchase_ap_write_off_router,
    policy_router as purchase_policy_router,
    purchase_order_router as purchase_purchase_order_router,
    supplier_router as purchase_supplier_router,
    three_way_match_router as purchase_three_way_match_router,
)
from api.gateway.routers.event import router as event_router
from api.gateway.routers.identity import router as identity_router
from api.gateway.routers.knowledge import router as knowledge_router
from api.gateway.routers.marketplace import router as marketplace_router
from api.gateway.routers.organization import router as organization_router
from api.gateway.routers.package import router as package_router
from api.gateway.routers.permission import router as permission_router
from api.gateway.routers.role_grants import router as permission_role_grants_router
from api.gateway.routers.platform_idp import router as platform_idp_router
from api.gateway.routers.platform_roles import router as platform_roles_router
from api.gateway.routers.platform_organization import router as platform_organization_router
from api.gateway.routers.terminal import router as terminal_router
from api.gateway.routers.twin import router as twin_router
from api.gateway.routers.workflow import router as workflow_router
from eaos_platform.brain.service import BrainService
from eaos_platform.commercial_handoff.service import CommercialHandoffService
from eaos_platform.knowledge.service import KnowledgeService
from eaos_platform.marketplace.service import MarketplaceService
from eaos_platform.package.service import PackageService
from eaos_platform.twin.service import TwinService
from eaos_sdk import __version__ as sdk_version
from eaos_sdk.catalog import load_release_manifest
from kernel.event_bus.bus import EventBus
from kernel.identity.service import IdentityService
from kernel.organization.service import OrganizationService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.workflow.service import WorkflowService
from noventi.crm.approval import (
    WorkflowDeliveryOrderReleaseApprovalGate,
    WorkflowSalesOrderConfirmApprovalGate,
    WorkflowQuoteConvertApprovalGate,
    WorkflowQuoteIssueApprovalGate,
)
from noventi.inventory.approval import WorkflowDeliveryOrderShipApprovalGate
from runtime.ai.service import AIRuntimeService
import smart_terminal
from smart_terminal.extension_runtime import EXTENSION_PANEL_CSP
from smart_terminal.service import SmartTerminalService

_TERMINAL_UI_ROOT = Path(smart_terminal.__file__).resolve().parent / "ui"


class ExtensionPanelCspMiddleware(BaseHTTPMiddleware):
    """Attach strict CSP to first-party Extension panel assets (PHX-G42)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/terminal/extensions/"):
            response.headers["Content-Security-Policy"] = EXTENSION_PANEL_CSP
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response


def create_app(
    *,
    identity_service: IdentityGatewayService | None = None,
    organization_service: OrganizationGatewayService | None = None,
    permission_service: PermissionGatewayService | None = None,
    workflow_service: WorkflowGatewayService | None = None,
    knowledge_service: KnowledgeGatewayService | None = None,
    event_service: EventGatewayService | None = None,
    package_service: PackageGatewayService | None = None,
    twin_service: TwinGatewayService | None = None,
    brain_service: BrainGatewayService | None = None,
    commercial_handoff_service: CommercialHandoffGatewayService | None = None,
    ai_service: AIRuntimeGatewayService | None = None,
    terminal_service: TerminalGatewayService | None = None,
    marketplace_service: MarketplaceGatewayService | None = None,
    crm_service: CRMGatewayService | None = None,
    customer360_service: Customer360GatewayService | None = None,
    customer_advisory_service: CustomerAdvisoryGatewayService | None = None,
    finance_service: FinanceGatewayService | None = None,
    inventory_service: InventoryGatewayService | None = None,
    purchase_service: PurchaseGatewayService | None = None,
    supplier360_service: Supplier360GatewayService | None = None,
) -> FastAPI:
    validate_production_auth()
    application = FastAPI(
        title="NOVENTI EAOS API Gateway",
        version=sdk_version,
        description=(
            "Phoenix Foundation gateway — trusted context derivation; "
            "thin domain HTTP surfaces (Identity through Marketplace technical), "
            "platform tenant lifecycle, and Smart Terminal operator shell; "
            "no business rule host."
        ),
    )
    injected = any(
        service is not None
        for service in (
            identity_service,
            organization_service,
            permission_service,
            workflow_service,
            knowledge_service,
            event_service,
            package_service,
            twin_service,
            brain_service,
            commercial_handoff_service,
            ai_service,
            terminal_service,
            marketplace_service,
            crm_service,
            customer360_service,
            customer_advisory_service,
            finance_service,
            inventory_service,
            purchase_service,
            supplier360_service,
        )
    )
    from api.gateway.sql_composition import compose_sql_gateway_services, gateway_store_mode

    if not injected and gateway_store_mode() == "sql":
        sql = compose_sql_gateway_services()
        application.state.identity = sql.identity
        application.state.organization = sql.organization
        application.state.permission = sql.permission
        application.state.workflow = sql.workflow
        application.state.knowledge = sql.knowledge
        application.state.event_bus = sql.event_bus
        application.state.package = sql.package
        application.state.twin = sql.twin
        application.state.brain = sql.brain
        application.state.ai = sql.ai
        application.state.terminal = sql.terminal
        application.state.marketplace = sql.marketplace
        application.state.crm = sql.crm
        application.state.customer360 = sql.customer360
        application.state.customer_advisory = sql.customer_advisory
        application.state.finance = sql.finance
        application.state.inventory = sql.inventory
        application.state.purchase = sql.purchase
        application.state.supplier360 = sql.supplier360
        application.state.commercial_handoff = CommercialHandoffService(
            sql.permission,
            brain=sql.brain,
            twin=sql.twin,
            crm=sql.crm,
            sales_orders=sql.crm,
        )
        application.state.gateway_store = "sql"
    else:
        permission = permission_service or PermissionService()
        workflow = workflow_service or WorkflowService(permission)
        knowledge = knowledge_service or KnowledgeService(permission)
        twin = twin_service or TwinService(permission)
        application.state.identity = identity_service or IdentityService()
        application.state.organization = organization_service or OrganizationService()
        application.state.permission = permission
        application.state.workflow = workflow
        application.state.knowledge = knowledge
        application.state.event_bus = event_service or EventBus(permission)
        application.state.package = package_service or PackageService(permission)
        application.state.twin = twin
        application.state.brain = brain_service or BrainService(permission, twin_reader=twin)
        application.state.ai = ai_service or AIRuntimeService(
            permission,
            workflow,
            knowledge_reader=knowledge,
        )
        application.state.terminal = terminal_service or SmartTerminalService(
            permission,
            workflow,
        )
        application.state.marketplace = marketplace_service or MarketplaceService(permission)
        application.state.crm = crm_service
        application.state.customer360 = customer360_service
        application.state.customer_advisory = customer_advisory_service
        application.state.finance = finance_service
        application.state.inventory = inventory_service
        application.state.purchase = purchase_service
        application.state.supplier360 = supplier360_service
        application.state.commercial_handoff = commercial_handoff_service or (
            CommercialHandoffService(
                permission,
                brain=application.state.brain,
                twin=twin,
                crm=application.state.crm,
                sales_orders=application.state.crm,
            )
            if application.state.crm is not None
            else None
        )
        application.state.gateway_store = "memory"
    if application.state.crm is not None:
        configure_issue_gate = getattr(
            application.state.crm, "set_quote_issue_approval_gate", None
        )
        if callable(configure_issue_gate):
            configure_issue_gate(
                WorkflowQuoteIssueApprovalGate(application.state.workflow)
            )
        configure_convert_gate = getattr(
            application.state.crm, "set_quote_convert_approval_gate", None
        )
        if callable(configure_convert_gate):
            configure_convert_gate(
                WorkflowQuoteConvertApprovalGate(application.state.workflow)
            )
        configure_so_confirm_gate = getattr(
            application.state.crm, "set_sales_order_confirm_approval_gate", None
        )
        if callable(configure_so_confirm_gate):
            configure_so_confirm_gate(
                WorkflowSalesOrderConfirmApprovalGate(application.state.workflow)
            )
        configure_do_release_gate = getattr(
            application.state.crm, "set_delivery_order_release_approval_gate", None
        )
        if callable(configure_do_release_gate):
            configure_do_release_gate(
                WorkflowDeliveryOrderReleaseApprovalGate(application.state.workflow)
            )
    if application.state.inventory is not None:
        configure_do_ship_gate = getattr(
            application.state.inventory, "set_do_ship_approval_gate", None
        )
        if callable(configure_do_ship_gate):
            configure_do_ship_gate(
                WorkflowDeliveryOrderShipApprovalGate(application.state.workflow)
            )
    application.add_middleware(ExtensionPanelCspMiddleware)
    _register_routes(application)
    return application


def _register_routes(application: FastAPI) -> None:
    @application.get("/v1/health", response_model=HealthEnvelope)
    def health(request: Request) -> HealthEnvelope:
        return HealthEnvelope.model_validate(
            {
                "data": {
                    "status": "ok",
                    "service": "eaos-gateway",
                    "gateway_store": getattr(request.app.state, "gateway_store", "memory"),
                }
            }
        )

    @application.get("/v1/release", response_model=ReleaseEnvelope)
    def release() -> ReleaseEnvelope:
        manifest = load_release_manifest()
        return ReleaseEnvelope.model_validate(
            {
                "data": {
                    "baseline_name": manifest["baseline_name"],
                    "version": manifest["version"],
                    "alembic_head": manifest["alembic_head"],
                    "sdk_version": sdk_version,
                    "deploy_region": deploy_region(),
                }
            }
        )

    @application.get("/v1/adapters", response_model=AdaptersEnvelope)
    def adapters() -> AdaptersEnvelope:
        items = [
            {
                "name": item.name,
                "openapi_path": item.openapi_path,
                "transport": item.transport,
                "status": item.status,
            }
            for item in list_adapters()
        ]
        return AdaptersEnvelope.model_validate(
            {
                "data": items,
                "meta": {
                    "count": len(items),
                    "openapi_inventory_product": openapi_inventory_product_posture(),
                    "sample_knowledge_pack_product": sample_knowledge_pack_product_posture(),
                },
            }
        )

    @application.get("/v1/context", response_model=ContextEnvelope)
    def get_context(
        ctx: ExecutionContext = Depends(derive_tenant_context),
    ) -> ContextEnvelope:
        return ContextEnvelope.model_validate({"data": serialize_context(ctx)})

    @application.post("/v1/context/echo", response_model=ContextEchoEnvelope)
    async def echo_context(
        body: ContextEchoRequest | None = None,
        ctx: ExecutionContext = Depends(derive_tenant_context),
    ) -> ContextEchoEnvelope:
        payload = (body or ContextEchoRequest()).model_dump()
        reject_body_elevation(payload)
        return ContextEchoEnvelope.model_validate(
            {
                "data": {
                    "context": serialize_context(ctx),
                    "echo": payload,
                }
            }
        )

    application.include_router(auth_router)
    application.include_router(auth_idp_router)
    application.include_router(auth_jwt_router)
    application.include_router(auth_webauthn_router)
    application.include_router(identity_router)
    application.include_router(organization_router)
    application.include_router(platform_organization_router)
    application.include_router(platform_idp_router)
    application.include_router(platform_roles_router)
    application.include_router(permission_router)
    application.include_router(permission_role_grants_router)
    application.include_router(workflow_router)
    application.include_router(knowledge_router)
    application.include_router(event_router)
    application.include_router(package_router)
    application.include_router(crm_router)
    application.include_router(crm_opportunity_router)
    application.include_router(crm_requirement_router)
    application.include_router(crm_quote_router)
    application.include_router(crm_conversion_router)
    application.include_router(crm_sales_order_router)
    application.include_router(crm_delivery_order_router)
    application.include_router(crm_ar_invoice_router)
    application.include_router(crm_return_authorization_router)
    application.include_router(crm_policy_router)
    application.include_router(finance_router)
    application.include_router(finance_ar_write_off_router)
    application.include_router(finance_ar_refund_router)
    application.include_router(finance_treasury_transfer_router)
    application.include_router(finance_ar_invoice_close_router)
    application.include_router(finance_policy_router)
    application.include_router(finance_adapter_router)
    application.include_router(finance_status_router)
    application.include_router(finance_credit_note_router)
    application.include_router(finance_tax_credit_link_router)
    application.include_router(finance_tax_invoice_router)
    application.include_router(finance_tax_rate_router)
    application.include_router(finance_gl_account_router)
    application.include_router(finance_gl_period_router)
    application.include_router(finance_journal_entry_router)
    application.include_router(finance_gl_bridge_map_router)
    application.include_router(finance_gl_bridge_router)
    application.include_router(finance_gl_fx_revaluation_router)
    application.include_router(finance_bank_statement_router)
    application.include_router(finance_commission_router)
    application.include_router(inventory_router)
    application.include_router(inventory_policy_router)
    application.include_router(purchase_supplier_router)
    application.include_router(purchase_ap_bill_router)
    application.include_router(purchase_ap_payment_router)
    application.include_router(purchase_ap_write_off_router)
    application.include_router(purchase_purchase_order_router)
    application.include_router(purchase_three_way_match_router)
    application.include_router(purchase_policy_router)
    application.include_router(twin_router)
    application.include_router(brain_router)
    application.include_router(commercial_handoff_router)
    application.include_router(digital_employee_router)
    application.include_router(industry_package_router)
    application.include_router(ai_workforce_router)
    application.include_router(ai_router)
    application.include_router(terminal_router)
    application.include_router(marketplace_router)

    if _TERMINAL_UI_ROOT.is_dir():
        application.mount(
            "/terminal",
            StaticFiles(directory=str(_TERMINAL_UI_ROOT), html=True),
            name="terminal_operator_shell",
        )


app = create_app()
