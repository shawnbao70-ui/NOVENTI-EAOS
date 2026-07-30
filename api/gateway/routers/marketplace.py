"""Marketplace HTTP surface — technical (G34) + commercial (M17) + payment clearing (G162)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import (
    MarketplaceGatewayService,
    TerminalGatewayService,
    get_marketplace_service,
    get_terminal_service,
)
from api.gateway.errors import raise_for_result
from api.gateway.host_acquire import (
    HOST_ACQUIRE_ALLOWLIST,
    acquire_listing_for_host,
)
from api.gateway.marketplace_economy import (
    billing_record_product_posture,
    dispute_arbitration_product_posture,
    metering_entitlement_product_posture,
)
from api.gateway.payment_clearing import (
    payment_clearing_enabled,
    payment_clearing_product_posture,
    record_payment_clearing,
)
from api.gateway.schemas.common import BooleanResult, UuidResult
from api.gateway.schemas.marketplace import (
    AttachSignatureRequest,
    CreateListingRequest,
    HostAcquireResult,
    MarketplaceListingResponse,
    MarketplaceStatusEnvelope,
    OpenDisputeRequest,
    PaymentClearingEnvelope,
    PaymentClearingRequest,
    ResolveDisputeRequest,
    ReviewListingRequest,
    SetPricingRequest,
    SetRevenueShareRequest,
)
from api.gateway.serializers.marketplace import (
    boolean_result,
    serialize_listing,
    uuid_result,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/marketplace", tags=["Marketplace"])


@router.get("/status", response_model=MarketplaceStatusEnvelope)
def get_marketplace_status() -> MarketplaceStatusEnvelope:
    """Marketplace posture (G101/G162/G173) + economy shells (PHX-G400–G402)."""

    clearing = payment_clearing_product_posture()
    enabled = payment_clearing_enabled()
    economy = metering_entitlement_product_posture()
    surfaces = [
        "listing_lifecycle",
        "acquire_technical",
        "host_acquire_allowlisted",
        "pricing",
        "invoice",
        "dispute",
        "revenue_share",
        "package_signature",
        "payment_clearing",
        "metering_shell",
        "entitlement_shell",
        "billing_record_shell",
        "dispute_arbitration_shell",
    ]
    return MarketplaceStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "foundation_commercial_policy": "v1",
                "economy_residual_reviewed": True,
                "external_commercial_services": "fail_closed",
                "host_acquire_not_package_install": True,
                "payment_clearing": (
                    "internal_env_gated" if enabled else "fail_closed"
                ),
                "payment_clearing_product": clearing,
                "host_acquire_product": {
                    "surface": "foundation_marketplace_host_acquire",
                    "milestone": "PHX-G173",
                    "mode": "allowlisted_first_party",
                    "arbitrary_scripts": False,
                    "package_install": False,
                    "external_psp": False,
                    "allowlist": sorted(HOST_ACQUIRE_ALLOWLIST),
                    "route": "/v1/marketplace/listings/{listing_id}/host-acquire",
                },
                "external_arbitration": "fail_closed",
                "metering": "fail_closed",
                "metering_product": economy["metering_product"],
                "entitlement_product": economy["entitlement_product"],
                "billing_record_product": billing_record_product_posture(),
                "dispute_arbitration_product": dispute_arbitration_product_posture(),
                "supported_surfaces": surfaces,
            }
        }
    )


@router.post(
    "/listings/{listing_id}/payment-clearing",
    response_model=PaymentClearingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_clearing(
    listing_id: UUID,
    response: Response,
    body: PaymentClearingRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> PaymentClearingEnvelope:
    """Env-gated internal payment clearing (PHX-G162). Default 503; no external PSP."""

    reject_context_override(body.model_dump())
    payload = record_payment_clearing(
        ctx,
        marketplace,
        listing_id=listing_id,
        invoice_id=body.invoice_id,
        note=body.note,
    )
    response.status_code = status.HTTP_201_CREATED
    return PaymentClearingEnvelope.model_validate({"data": payload})


@router.post("/listings", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_listing(
    body: CreateListingRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = marketplace.create_listing(
        ctx,
        package_key=body.package_key,
        package_version=body.package_version,
        required_permissions=list(body.required_permissions),
        declared_events=list(body.declared_events or []),
        data_scope=body.data_scope,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/listings/{listing_id}", response_model=MarketplaceListingResponse)
def get_listing(
    listing_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> MarketplaceListingResponse:
    result = marketplace.get_listing(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    return MarketplaceListingResponse.model_validate(serialize_listing(result.data))


@router.post("/listings/{listing_id}/signature", response_model=BooleanResult)
def attach_signature(
    listing_id: UUID,
    body: AttachSignatureRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    reject_context_override(body.model_dump())
    result = marketplace.attach_signature(
        ctx,
        listing_id=listing_id,
        signature_ref=body.signature_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/listings/{listing_id}/submit", response_model=BooleanResult)
def submit_listing(
    listing_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    result = marketplace.submit_for_review(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/listings/{listing_id}/review", response_model=BooleanResult)
def review_listing(
    listing_id: UUID,
    body: ReviewListingRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    reject_context_override(body.model_dump())
    result = marketplace.review_listing(
        ctx,
        listing_id=listing_id,
        approve=body.approve,
        notes=body.notes,
    )
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/listings/{listing_id}/publish", response_model=BooleanResult)
def publish_listing(
    listing_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    result = marketplace.publish_listing(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/listings/{listing_id}/revoke", response_model=BooleanResult)
def revoke_listing(
    listing_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    result = marketplace.revoke_listing(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/listings/{listing_id}/acquire",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def acquire_listing(
    listing_id: UUID,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> UuidResult:
    result = marketplace.acquire_listing(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/listings/{listing_id}/host-acquire",
    response_model=HostAcquireResult,
    status_code=status.HTTP_201_CREATED,
)
def host_acquire_listing(
    listing_id: UUID,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> HostAcquireResult:
    """Technical acquire + allowlisted first-party Extension Host projection (PHX-G172)."""

    result = acquire_listing_for_host(
        marketplace=marketplace,  # type: ignore[arg-type]
        terminal=terminal,  # type: ignore[arg-type]
        ctx=ctx,
        listing_id=listing_id,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return HostAcquireResult.model_validate(
        {
            "data": result.data,
            "audit_id": str(result.audit_id) if result.audit_id else None,
        }
    )


@router.post("/listings/{listing_id}/pricing", response_model=BooleanResult)
def set_pricing(
    listing_id: UUID,
    body: SetPricingRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    """Foundation fixed pricing (ADR-0054)."""
    reject_context_override(body.model_dump())
    result = marketplace.set_pricing(
        ctx,
        listing_id=listing_id,
        price=body.price,
        currency=body.currency,
    )
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/listings/{listing_id}/invoices",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    listing_id: UUID,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> UuidResult:
    result = marketplace.create_invoice(ctx, listing_id=listing_id)
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/listings/{listing_id}/disputes",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def open_dispute(
    listing_id: UUID,
    response: Response,
    body: OpenDisputeRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = marketplace.open_dispute(
        ctx,
        listing_id=listing_id,
        reason=body.reason,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/disputes/{dispute_id}/resolve", response_model=BooleanResult)
def resolve_dispute(
    dispute_id: UUID,
    body: ResolveDisputeRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    reject_context_override(body.model_dump())
    result = marketplace.resolve_dispute(
        ctx,
        dispute_id=dispute_id,
        resolution=body.resolution,
    )
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/listings/{listing_id}/revenue-share", response_model=BooleanResult)
def set_revenue_share(
    listing_id: UUID,
    body: SetRevenueShareRequest | None = None,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    marketplace: MarketplaceGatewayService = Depends(get_marketplace_service),
) -> BooleanResult:
    payload = body or SetRevenueShareRequest()
    reject_context_override(payload.model_dump(exclude_none=True))
    result = marketplace.set_revenue_share(
        ctx,
        listing_id=listing_id,
        platform_share_bps=payload.platform_share_bps,
        share_ratio=payload.share_ratio,
    )
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )
