"""Local Smart Terminal demo gateway (dev-only).

Default ``api.gateway.app:app`` is fail-closed (reject-all eligibility, no grants).
This module wires AllowAll eligibility, platform governors, a seeded tenant + human
user, and installed sample packages so Operator / Product / Ops can walk:

Open session -> Compose intent -> Build preview -> Commit preview

Declared Package Surfaces (PHX-G165)::

    GET /v1/packages/surfaces  (product.* / ops.*)
    POST /v1/packages/actions/resolve -> handoff to Operator

Run::

    uvicorn api.gateway.demo:app --reload --port 8001

Then open http://127.0.0.1:8001/terminal/ and paste the printed Subject / Tenant IDs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.staticfiles import StaticFiles

from api.gateway.app import create_app
from api.gateway.routers.demo_bootstrap import router as demo_bootstrap_router
from api.gateway.sample_knowledge_pack import SAMPLE_PACK_PATH
from eaos_platform.marketplace.service import MarketplaceService
from eaos_platform.package.service import PackageService
from kernel.identity.service import IdentityService
from kernel.organization.service import OrganizationService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from smart_terminal.models import ExtensionStatus, TerminalExtension
from smart_terminal.service import SmartTerminalService
from smart_terminal.signing import ExtensionSigningSettings, sign_extension_hmac_v1

# Stable bootstrap actors (not secrets).
DEMO_ADMIN = UUID("00000000-0000-4000-8000-000000000001")
DEMO_OPERATOR = UUID("00000000-0000-4000-8000-000000000002")
DEMO_TENANT = UUID("00000000-0000-4000-8000-0000000000aa")
# Dev-only HMAC material for demo extension activate (not a production secret).
DEMO_EXTENSION_HMAC = "noventi-demo-extension-hmac-v1"
DEMO_EXTENSION_KEY = "noventi.demo.panel"
DEMO_EXTENSION_VERSION = "1.0.0"

_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE_OPS = _ROOT / "packages" / "sample_ops" / "manifest.json"
_SAMPLE_PRODUCT = _ROOT / "packages" / "sample_product" / "manifest.json"

_TERMINAL_GRANTS = (
    ("terminal_session", {"open", "read", "close"}),
    ("terminal_intent", {"compose", "read"}),
    ("terminal_preview", {"build", "read"}),
    ("terminal_approval", {"present", "request"}),
    ("terminal_commit", {"execute"}),
    ("terminal_extension", {"register", "activate", "revoke", "read", "invoke"}),
)

_PACKAGE_GRANTS = (
    ("package_manifest", {"register", "publish", "read"}),
    ("package_installation", {"install", "disable", "read"}),
    ("package_surface", {"read"}),
    ("package_action", {"resolve"}),
    ("pkg.ops.brief", {"compose", "publish"}),
    ("pkg.product.offer", {"review"}),
    ("pkg.sample.flow", {"compose", "handoff"}),
    ("pkg.order.flow", {"compose", "create"}),
)

_MARKETPLACE_GRANTS = (
    (
        "marketplace_listing",
        {"create", "read", "submit", "review", "publish", "revoke"},
    ),
    ("marketplace_acquisition", {"acquire", "read"}),
)


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(*, subject_id: UUID, tenant_id: UUID | None, platform_scope: bool = False) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        platform_scope=platform_scope,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _grant_all(
    permission: PermissionService,
    *,
    admin: ExecutionContext,
    principal: UUID,
    grants: tuple[tuple[str, set[str]], ...],
) -> None:
    for resource_type, actions in grants:
        result = permission.grant(
            admin,
            principal_subject_id=principal,
            resource_type=resource_type,
            actions=actions,
        )
        if not result.ok:
            raise RuntimeError(
                f"demo grant failed for {resource_type}: "
                f"{result.error_code} {result.error_message}"
            )


def _seed_signed_extension(
    terminal: SmartTerminalService,
    *,
    ctx: ExecutionContext,
) -> UUID:
    assert ctx.tenant_id is not None
    now = datetime.now(timezone.utc)
    proto = TerminalExtension(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        extension_key=DEMO_EXTENSION_KEY,
        version=DEMO_EXTENSION_VERSION,
        signature_ref=None,
        status=ExtensionStatus.REGISTERED,
        declared_capabilities=frozenset(),
        declared_actions=frozenset({"panel.render"}),
        allowed_surfaces=frozenset({"extensions"}),
        data_scope="tenant.demo",
        created_at=now,
        updated_at=now,
    )
    signature = sign_extension_hmac_v1(secret=DEMO_EXTENSION_HMAC, extension=proto)
    registered = terminal.register_extension(
        ctx,
        extension_key=proto.extension_key,
        version=proto.version,
        signature_ref=signature,
        declared_actions=list(proto.declared_actions),
        allowed_surfaces=list(proto.allowed_surfaces),
        data_scope=proto.data_scope,
    )
    if not registered.ok or registered.data is None:
        raise RuntimeError(
            f"demo extension register failed: "
            f"{registered.error_code} {registered.error_message}"
        )
    activated = terminal.activate_extension(ctx, extension_id=registered.data)
    if not activated.ok:
        raise RuntimeError(
            f"demo extension activate failed: "
            f"{activated.error_code} {activated.error_message}"
        )
    return registered.data


def _seed_published_host_listing(
    marketplace: MarketplaceService,
    *,
    ctx: ExecutionContext,
) -> UUID:
    """Publish allowlisted first-party listing for host-acquire click-through."""

    created = marketplace.create_listing(
        ctx,
        package_key=DEMO_EXTENSION_KEY,
        package_version=DEMO_EXTENSION_VERSION,
        required_permissions=["terminal_extension:invoke"],
        declared_events=["demo.panel.rendered"],
        data_scope="tenant.demo",
    )
    if not created.ok or created.data is None:
        raise RuntimeError(
            f"demo listing create failed: {created.error_code} {created.error_message}"
        )
    listing_id = created.data
    signed = marketplace.attach_signature(
        ctx,
        listing_id=listing_id,
        signature_ref="sig:demo:host-listing",
    )
    if not signed.ok:
        raise RuntimeError(
            f"demo listing signature failed: {signed.error_code} {signed.error_message}"
        )
    submitted = marketplace.submit_for_review(ctx, listing_id=listing_id)
    if not submitted.ok:
        raise RuntimeError(
            f"demo listing submit failed: {submitted.error_code} {submitted.error_message}"
        )
    reviewed = marketplace.review_listing(
        ctx,
        listing_id=listing_id,
        approve=True,
        notes="demo host-acquire seed",
    )
    if not reviewed.ok:
        raise RuntimeError(
            f"demo listing review failed: {reviewed.error_code} {reviewed.error_message}"
        )
    published = marketplace.publish_listing(ctx, listing_id=listing_id)
    if not published.ok:
        raise RuntimeError(
            f"demo listing publish failed: {published.error_code} {published.error_message}"
        )
    return listing_id


def _install_sample_package(
    packages: PackageService,
    *,
    ctx: ExecutionContext,
    manifest_path: Path,
) -> None:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    registered = packages.register_manifest(
        ctx,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload.get("surfaces"),
        actions=payload.get("actions"),
        required_permissions=payload.get("required_permissions"),
        declared_events=payload.get("declared_events"),
    )
    if not registered.ok or registered.data is None:
        raise RuntimeError(
            f"demo package register failed ({manifest_path.name}): "
            f"{registered.error_code} {registered.error_message}"
        )
    published = packages.publish_manifest(ctx, manifest_id=registered.data)
    if not published.ok:
        raise RuntimeError(
            f"demo package publish failed ({manifest_path.name}): "
            f"{published.error_code} {published.error_message}"
        )
    installed = packages.install_package(ctx, manifest_id=registered.data)
    if not installed.ok:
        raise RuntimeError(
            f"demo package install failed ({manifest_path.name}): "
            f"{installed.error_code} {installed.error_message}"
        )


def create_demo_app():
    """Create a gateway pre-seeded with tenant user + declared sample packages."""
    permission = PermissionService(
        grant_administrators={DEMO_ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(permission, definition_administrators={DEMO_ADMIN})
    terminal = SmartTerminalService(
        permission,
        workflow,
        signing=ExtensionSigningSettings(
            mode="hmac",
            required=True,
            hmac_secret=DEMO_EXTENSION_HMAC,
        ),
    )
    organization = OrganizationService(platform_governors={DEMO_ADMIN})
    identity = IdentityService()
    packages = PackageService(permission)
    marketplace = MarketplaceService(permission)

    # Legacy fixed IDs still work for quick paste.
    legacy_admin = _ctx(subject_id=DEMO_ADMIN, tenant_id=DEMO_TENANT)
    for principal in (DEMO_ADMIN, DEMO_OPERATOR):
        _grant_all(
            permission,
            admin=legacy_admin,
            principal=principal,
            grants=_TERMINAL_GRANTS + _PACKAGE_GRANTS + _MARKETPLACE_GRANTS,
        )
    _install_sample_package(packages, ctx=legacy_admin, manifest_path=_SAMPLE_OPS)
    _install_sample_package(packages, ctx=legacy_admin, manifest_path=_SAMPLE_PRODUCT)
    _seed_signed_extension(terminal, ctx=legacy_admin)
    _seed_published_host_listing(marketplace, ctx=legacy_admin)

    # Open one real tenant + register one human user for product-page click-through.
    platform_admin = _ctx(subject_id=DEMO_ADMIN, tenant_id=None, platform_scope=True)
    tenant_result = organization.create_tenant(
        platform_admin,
        legal_name="NOVENTI Demo Tenant",
        region_policy_ref="demo-local",
    )
    if not tenant_result.ok or tenant_result.data is None:
        raise RuntimeError(
            f"demo tenant create failed: "
            f"{tenant_result.error_code} {tenant_result.error_message}"
        )
    seeded_tenant_id = tenant_result.data

    tenant_admin = _ctx(subject_id=DEMO_ADMIN, tenant_id=seeded_tenant_id)
    subject_result = identity.register_subject(
        tenant_admin,
        subject_type="human",
        display_name="Demo Tenant User",
    )
    if not subject_result.ok or subject_result.data is None:
        raise RuntimeError(
            f"demo subject register failed: "
            f"{subject_result.error_code} {subject_result.error_message}"
        )
    seeded_subject_id = subject_result.data
    for principal in (DEMO_ADMIN, seeded_subject_id):
        _grant_all(
            permission,
            admin=tenant_admin,
            principal=principal,
            grants=_TERMINAL_GRANTS + _PACKAGE_GRANTS + _MARKETPLACE_GRANTS,
        )
    _install_sample_package(packages, ctx=tenant_admin, manifest_path=_SAMPLE_OPS)
    _install_sample_package(packages, ctx=tenant_admin, manifest_path=_SAMPLE_PRODUCT)
    seeded_extension_id = _seed_signed_extension(terminal, ctx=tenant_admin)
    seeded_listing_id = _seed_published_host_listing(marketplace, ctx=tenant_admin)

    app = create_app(
        identity_service=identity,
        organization_service=organization,
        permission_service=permission,
        workflow_service=workflow,
        terminal_service=terminal,
        package_service=packages,
        marketplace_service=marketplace,
    )
    app.include_router(demo_bootstrap_router)
    sample_pack_dir = Path(__file__).resolve().parents[2] / SAMPLE_PACK_PATH
    if sample_pack_dir.is_dir():
        app.mount(
            "/v1/demo/sample-pack",
            StaticFiles(directory=str(sample_pack_dir), html=False),
            name="demo_sample_knowledge_pack",
        )
    app.state.demo_seeded_subject_id = seeded_subject_id
    app.state.demo_seeded_tenant_id = seeded_tenant_id
    app.state.demo_seeded_extension_id = seeded_extension_id
    app.state.demo_seeded_listing_id = seeded_listing_id
    # Declared Package Surface keys seeded for Product/Ops projection (G165/G167)
    # plus sample/order Terminal demo surfaces.
    app.state.demo_declared_surface_keys = (
        "product.catalog",
        "product.sample",
        "ops.workbench",
        "ops.order",
    )
    return app


app = create_demo_app()

_seeded_subject = getattr(app.state, "demo_seeded_subject_id", DEMO_OPERATOR)
_seeded_tenant = getattr(app.state, "demo_seeded_tenant_id", DEMO_TENANT)

# Banner for operators starting uvicorn.
print(
    "\n".join(
        [
            "",
            "EAOS Terminal demo gateway ready (dev-only).",
            f"  Subject (tenant user): {_seeded_subject}",
            f"  Tenant  (created):     {_seeded_tenant}",
            f"  Legacy Subject:        {DEMO_OPERATOR}",
            f"  Legacy Tenant:         {DEMO_TENANT}",
            "  Open: /terminal/  (Product #product · Ops #ops · Extensions #extensions)",
            "  Bootstrap: GET /v1/demo/bootstrap (demo-only)",
            "  Sample pack: /v1/demo/sample-pack/INDEX.md (PHX-G293; docs-only; ≠ CRUD)",
            "  Declared surfaces: product.catalog + product.sample + ops.workbench + ops.order",
            "  Demo flows: Product#product 样品 · Ops#ops 订单 → Operator handoff",
            "  Signed extension seed: noventi.demo.panel (PHX-G168/G169)",
            "  Flow: Open session -> Compose intent -> Build preview -> Commit",
            "  Keep High impact unchecked for direct commit (order.approve is high-impact).",
            "",
        ]
    )
)
