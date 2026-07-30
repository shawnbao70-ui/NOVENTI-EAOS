"""Marketplace request/status DTOs — runtime parity with docs/api/marketplace.openapi.yaml."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PaymentClearingProductPosture(_ClosedModel):
    surface: Literal["foundation_marketplace_payment_clearing"] = (
        "foundation_marketplace_payment_clearing"
    )
    milestone: Literal["PHX-G162"] = "PHX-G162"
    payment_clearing_enabled: bool
    clearing_routes: list[str] = Field(min_length=1)
    clearing_stub_observability: Literal[True] = True
    settlement_rail: Literal["disabled", "internal_record_only"]
    external_psp: Literal[False] = False
    external_arbitration: Literal["fail_closed"] = "fail_closed"
    metering: Literal["fail_closed"] = "fail_closed"
    fail_closed_reasons: list[str] = Field(min_length=1)


class HostAcquireProductPosture(_ClosedModel):
    surface: Literal["foundation_marketplace_host_acquire"] = (
        "foundation_marketplace_host_acquire"
    )
    milestone: Literal["PHX-G173"] = "PHX-G173"
    mode: Literal["allowlisted_first_party"] = "allowlisted_first_party"
    arbitrary_scripts: Literal[False] = False
    package_install: Literal[False] = False
    external_psp: Literal[False] = False
    allowlist: list[str]
    route: str = Field(min_length=1)


class MeteringProductPosture(_ClosedModel):
    """PHX-G400 metering shell — fail-closed; no external PSP/network invent."""

    surface: Literal["foundation_marketplace_metering_shell"] = (
        "foundation_marketplace_metering_shell"
    )
    milestone: Literal["PHX-G400"] = "PHX-G400"
    posture: Literal["shell_fail_closed"] = "shell_fail_closed"
    entitlement_linked: Literal[False] = False
    external_psp: Literal[False] = False
    network_default: Literal["off"] = "off"
    commercial_auto_write: Literal[False] = False
    routes: list[str] = Field(min_length=1)


class EntitlementProductPosture(_ClosedModel):
    """PHX-G400 entitlement shell — declaration-only; no auto-grant invent."""

    surface: Literal["foundation_marketplace_entitlement_shell"] = (
        "foundation_marketplace_entitlement_shell"
    )
    milestone: Literal["PHX-G400"] = "PHX-G400"
    posture: Literal["shell_declaration_only"] = "shell_declaration_only"
    auto_grant: Literal[False] = False
    cap_to_grant_invent: Literal[False] = False
    commercial_auto_write: Literal[False] = False
    routes: list[str] = Field(min_length=1)


class BillingRecordProductPosture(_ClosedModel):
    """PHX-G401 internal billing-record shell (≠ external PSP)."""

    surface: Literal["foundation_marketplace_billing_record_shell"] = (
        "foundation_marketplace_billing_record_shell"
    )
    milestone: Literal["PHX-G401"] = "PHX-G401"
    posture: Literal["internal_invoice_shell"] = "internal_invoice_shell"
    external_psp: Literal[False] = False
    enable_psp_network_default: Literal["off"] = "off"
    bank_file_import: Literal["deferred"] = "deferred"
    settlement_rail: Literal["internal_record_only_when_clearing_enabled"] = (
        "internal_record_only_when_clearing_enabled"
    )
    invoice_surface: Literal["marketplace_listing_invoice"] = (
        "marketplace_listing_invoice"
    )
    finance_ar_invoice_separate: Literal[True] = True
    routes: list[str] = Field(min_length=1)


class DisputeArbitrationProductPosture(_ClosedModel):
    """PHX-G402 dispute/arbitration fail-closed shell."""

    surface: Literal["foundation_marketplace_dispute_arbitration_shell"] = (
        "foundation_marketplace_dispute_arbitration_shell"
    )
    milestone: Literal["PHX-G402"] = "PHX-G402"
    dispute_surface: Literal["publisher_tenant_resolve"] = "publisher_tenant_resolve"
    external_arbitration: Literal["fail_closed"] = "fail_closed"
    external_arbitration_invent: Literal[False] = False
    commercial_auto_write: Literal[False] = False
    routes: list[str] = Field(min_length=1)
    fail_closed_reasons: list[str] = Field(min_length=1)


class MarketplaceStatusData(_ClosedModel):
    writable: Literal[False] = False
    foundation_commercial_policy: Literal["v1"] = "v1"
    economy_residual_reviewed: Literal[True] = True
    external_commercial_services: Literal["fail_closed"] = "fail_closed"
    host_acquire_not_package_install: Literal[True] = True
    payment_clearing: Literal["fail_closed", "internal_env_gated"]
    payment_clearing_product: PaymentClearingProductPosture
    host_acquire_product: HostAcquireProductPosture
    external_arbitration: Literal["fail_closed"] = "fail_closed"
    metering: Literal["fail_closed"] = "fail_closed"
    metering_product: MeteringProductPosture
    entitlement_product: EntitlementProductPosture
    billing_record_product: BillingRecordProductPosture
    dispute_arbitration_product: DisputeArbitrationProductPosture
    supported_surfaces: list[str] = Field(min_length=1)


class MarketplaceStatusEnvelope(_ClosedModel):
    data: MarketplaceStatusData


class PaymentClearingRequest(_ClosedModel):
    invoice_id: UUID
    note: str = ""


class CreateListingRequest(_ClosedModel):
    package_key: str = Field(min_length=1)
    package_version: str = Field(min_length=1)
    required_permissions: list[str] = Field(min_length=1)
    data_scope: str = Field(min_length=1)
    declared_events: list[str] | None = None


class AttachSignatureRequest(_ClosedModel):
    signature_ref: str = Field(min_length=1)


class ReviewListingRequest(_ClosedModel):
    approve: bool
    notes: str = ""


class SetPricingRequest(_ClosedModel):
    price: str = Field(min_length=1)
    currency: str = Field(default="CNY", min_length=3, max_length=3)


class OpenDisputeRequest(_ClosedModel):
    reason: str = Field(min_length=1)


class ResolveDisputeRequest(_ClosedModel):
    resolution: str = Field(min_length=1)


class SetRevenueShareRequest(_ClosedModel):
    platform_share_bps: int | None = Field(default=None, ge=0, le=5000)
    share_ratio: float | None = Field(default=None, ge=0, le=0.5)


class MarketplaceListingResponse(_ClosedModel):
    id: UUID
    package_key: str = Field(min_length=1)
    package_version: str = Field(min_length=1)
    status: Literal[
        "draft", "submitted", "approved", "rejected", "published", "revoked"
    ]
    signature_ref: str | None = None
    data_scope: str
    required_permissions: list[str] = Field(default_factory=list)
    declared_events: list[str] = Field(default_factory=list)
    version: int = Field(ge=0)


class PaymentClearingResult(_ClosedModel):
    clearing_step: Literal["payment_clearing"] = "payment_clearing"
    payment_cleared: Literal[True] = True
    external_psp: Literal[False] = False
    settlement_rail: Literal["internal_record_only"] = "internal_record_only"
    milestone: Literal["PHX-G162"] = "PHX-G162"
    clearing_id: UUID
    listing_id: UUID
    invoice_id: UUID
    audit_id: UUID | str | None = None


class PaymentClearingEnvelope(_ClosedModel):
    data: PaymentClearingResult


class HostAcquirePayload(_ClosedModel):
    listing_id: UUID
    package_key: str = Field(min_length=1)
    extension_id: UUID
    extension_status: str = Field(min_length=1)
    package_version: str = ""
    acquisition_id: UUID | None = None
    already_acquired: bool = False
    projected: bool = False
    host_actions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class HostAcquireResult(_ClosedModel):
    data: HostAcquirePayload
    audit_id: UUID | str | None = None
