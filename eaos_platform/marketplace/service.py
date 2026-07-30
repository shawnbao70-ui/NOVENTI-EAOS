"""Marketplace service — PHX-M16 distribution + PHX-M17 Foundation commercial policy."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from eaos_platform.marketplace.models import (
    CapabilityDeclaration,
    DisputeStatus,
    InvoiceStatus,
    ListingPricing,
    ListingRevenueShare,
    ListingStatus,
    MarketplaceAcquisition,
    MarketplaceDispute,
    MarketplaceInvoice,
    MarketplaceListing,
)
from eaos_platform.marketplace.policy import (
    BILLING_CYCLE_IMMEDIATE,
    DEFAULT_PLATFORM_SHARE_BPS,
    PRICING_MODEL_FIXED,
    normalize_currency,
    normalize_fixed_price,
    normalize_platform_share_bps,
)
from eaos_platform.marketplace.repository import (
    InMemoryMarketplaceRepository,
    MarketplaceRepository,
)
from eaos_platform.marketplace.signing import (
    MarketplaceSigningSettings,
    ensure_listing_signature,
    verify_listing_signature,
)
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult


class MarketplaceService:
    """Marketplace registry with Foundation commercial policy (ADR-0054)."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: MarketplaceRepository | None = None,
        audit_log: AuditLog | None = None,
        *,
        signing: MarketplaceSigningSettings | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryMarketplaceRepository()
        self._signing = signing if signing is not None else MarketplaceSigningSettings.from_env()
        self._audit = audit_log or InMemoryAuditLog()

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def create_listing(
        self,
        ctx: ExecutionContext,
        *,
        package_key: str,
        package_version: str,
        required_permissions: list[str],
        declared_events: list[str],
        data_scope: str,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned_key = package_key.strip()
            cleaned_version = package_version.strip()
            cleaned_scope = data_scope.strip()
            perms = frozenset(item.strip() for item in required_permissions if item.strip())
            events = frozenset(item.strip() for item in declared_events if item.strip())
            if not cleaned_key or not cleaned_version:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "package_key and package_version are required",
                )
            if cleaned_key.casefold().startswith("kernel."):
                raise KernelError(
                    ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                    "marketplace listings must not claim kernel ownership",
                )
            if not perms or not cleaned_scope:
                raise KernelError(
                    ErrorCode.MARKETPLACE_CAPABILITY_REQUIRED,
                    "required_permissions and data_scope are required",
                )
            self._require_permission(
                ctx,
                action="create",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                ),
            )
            now = datetime.now(timezone.utc)
            listing = MarketplaceListing(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                package_key=cleaned_key,
                package_version=cleaned_version,
                publisher_subject_id=ctx.subject_id,
                status=ListingStatus.DRAFT,
                capability=CapabilityDeclaration(
                    required_permissions=perms,
                    declared_events=events,
                    data_scope=cleaned_scope,
                ),
                created_at=now,
                updated_at=now,
            )
            self._repo.add_listing(listing)
            audit = self._audit.record(
                ctx,
                action="Marketplace.CreateListing",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
                details={
                    "package_key": cleaned_key,
                    "package_version": cleaned_version,
                },
            )
            return KernelResult.success(listing.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def attach_signature(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        signature_ref: str,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            cleaned = signature_ref.strip()
            if not cleaned:
                raise KernelError(
                    ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED,
                    "signature_ref is required",
                )
            self._require_permission(
                ctx,
                action="create",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            if listing.status not in {ListingStatus.DRAFT, ListingStatus.REJECTED}:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "signature can only be attached in draft or rejected state",
                )
            verify_listing_signature(
                listing,
                signature_ref=cleaned,
                settings=self._signing,
            )
            expected = listing.version
            listing.signature_ref = cleaned
            listing.updated_at = datetime.now(timezone.utc)
            listing.version = expected + 1
            self._repo.save_listing(listing, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.AttachSignature",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
                details={
                    "signature_ref": cleaned,
                    "signing_mode": self._signing.mode,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def submit_for_review(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            self._require_permission(
                ctx,
                action="submit",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            if listing.status not in {ListingStatus.DRAFT, ListingStatus.REJECTED}:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "only draft or rejected listings can be submitted",
                )
            ensure_listing_signature(listing, settings=self._signing)
            expected = listing.version
            listing.status = ListingStatus.SUBMITTED
            listing.updated_at = datetime.now(timezone.utc)
            listing.version = expected + 1
            self._repo.save_listing(listing, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.SubmitForReview",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def review_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        approve: bool,
        notes: str = "",
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            self._require_permission(
                ctx,
                action="review",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            if listing.status != ListingStatus.SUBMITTED:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "only submitted listings can be reviewed",
                )
            expected = listing.version
            listing.status = (
                ListingStatus.APPROVED if approve else ListingStatus.REJECTED
            )
            listing.review_notes = notes.strip()
            listing.updated_at = datetime.now(timezone.utc)
            listing.version = expected + 1
            self._repo.save_listing(listing, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.ReviewListing",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
                details={"approve": approve},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def publish_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            self._require_permission(
                ctx,
                action="publish",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            if listing.status != ListingStatus.APPROVED:
                raise KernelError(
                    ErrorCode.MARKETPLACE_NOT_APPROVED,
                    "only approved listings can be published",
                )
            ensure_listing_signature(listing, settings=self._signing)
            expected = listing.version
            listing.status = ListingStatus.PUBLISHED
            listing.updated_at = datetime.now(timezone.utc)
            listing.version = expected + 1
            self._repo.save_listing(listing, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.PublishListing",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def revoke_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            self._require_permission(
                ctx,
                action="revoke",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            if listing.status not in {ListingStatus.PUBLISHED, ListingStatus.APPROVED}:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "only published or approved listings can be revoked",
                )
            expected = listing.version
            listing.status = ListingStatus.REVOKED
            listing.updated_at = datetime.now(timezone.utc)
            listing.version = expected + 1
            self._repo.save_listing(listing, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.RevokeListing",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[MarketplaceListing]:
        try:
            listing = self._require_listing(ctx, listing_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=listing.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            return KernelResult.success(listing)
        except KernelError as err:
            return KernelResult.from_error(err)

    def acquire_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            listing = self._require_listing(ctx, listing_id)
            if listing.status == ListingStatus.REVOKED:
                raise KernelError(
                    ErrorCode.MARKETPLACE_REVOKED,
                    "revoked listings cannot be acquired",
                )
            if listing.status != ListingStatus.PUBLISHED:
                raise KernelError(
                    ErrorCode.MARKETPLACE_NOT_PUBLISHED,
                    "only published listings can be acquired",
                )
            self._require_permission(
                ctx,
                action="acquire",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_acquisition",
                ),
            )
            existing = self._repo.get_acquisition_by_listing(
                tenant_id=ctx.tenant_id,
                listing_id=listing.id,
            )
            if existing is not None:
                raise KernelError(
                    ErrorCode.MARKETPLACE_ALREADY_ACQUIRED,
                    "listing already acquired for this tenant",
                )
            acquisition = MarketplaceAcquisition(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                listing_id=listing.id,
                package_key=listing.package_key,
                package_version=listing.package_version,
                acquired_by_subject_id=ctx.subject_id,
                created_at=datetime.now(timezone.utc),
            )
            self._repo.add_acquisition(acquisition)
            audit = self._audit.record(
                ctx,
                action="Marketplace.AcquireListing",
                resource=f"marketplace_acquisition:{acquisition.id}",
                result="ok",
                details={
                    "listing_id": str(listing.id),
                    "package_key": listing.package_key,
                },
            )
            return KernelResult.success(acquisition.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_pricing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        price: str,
        currency: str | None = None,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            assert ctx.tenant_id is not None
            amount = normalize_fixed_price(price)
            currency_code = normalize_currency(currency)
            self._require_permission(
                ctx,
                action="price",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            now = datetime.now(timezone.utc)
            self._repo.upsert_pricing(
                ListingPricing(
                    listing_id=listing.id,
                    tenant_id=ctx.tenant_id,
                    pricing_model=PRICING_MODEL_FIXED,
                    amount=amount,
                    currency=currency_code,
                    updated_at=now,
                )
            )
            audit = self._audit.record(
                ctx,
                action="Marketplace.SetPricing",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
                details={
                    "pricing_model": PRICING_MODEL_FIXED,
                    "amount": amount,
                    "currency": currency_code,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_invoice(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]:
        try:
            listing = self._require_listing(ctx, listing_id)
            assert ctx.tenant_id is not None
            self._require_permission(
                ctx,
                action="invoice",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            pricing = self._repo.get_pricing(listing.id)
            if pricing is None:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "listing pricing is required before invoicing",
                    details={"listing_id": str(listing.id)},
                )
            invoice = MarketplaceInvoice(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                listing_id=listing.id,
                amount=pricing.amount,
                currency=pricing.currency,
                billing_cycle=BILLING_CYCLE_IMMEDIATE,
                status=InvoiceStatus.ISSUED,
                issued_by_subject_id=ctx.subject_id,
                created_at=datetime.now(timezone.utc),
            )
            self._repo.add_invoice(invoice)
            audit = self._audit.record(
                ctx,
                action="Marketplace.CreateInvoice",
                resource=f"marketplace_invoice:{invoice.id}",
                result="ok",
                details={
                    "listing_id": str(listing.id),
                    "amount": invoice.amount,
                    "currency": invoice.currency,
                    "billing_cycle": invoice.billing_cycle,
                    "note": "invoice is not a purchase settlement; acquire remains technical",
                },
            )
            return KernelResult.success(invoice.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def open_dispute(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        reason: str,
    ) -> KernelResult[UUID]:
        try:
            listing = self._require_listing(ctx, listing_id)
            assert ctx.tenant_id is not None
            cleaned_reason = reason.strip()
            if not cleaned_reason:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "dispute reason is required",
                )
            self._require_permission(
                ctx,
                action="dispute",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            dispute = MarketplaceDispute(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                listing_id=listing.id,
                reason=cleaned_reason,
                status=DisputeStatus.OPEN,
                opened_by_subject_id=ctx.subject_id,
                created_at=datetime.now(timezone.utc),
            )
            self._repo.add_dispute(dispute)
            audit = self._audit.record(
                ctx,
                action="Marketplace.OpenDispute",
                resource=f"marketplace_dispute:{dispute.id}",
                result="ok",
                details={"listing_id": str(listing.id), "reason": cleaned_reason},
            )
            return KernelResult.success(dispute.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def resolve_dispute(
        self,
        ctx: ExecutionContext,
        *,
        dispute_id: UUID,
        resolution: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned = resolution.strip()
            if not cleaned:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "dispute resolution is required",
                )
            dispute = self._repo.get_dispute(dispute_id)
            if dispute is None or dispute.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.MARKETPLACE_NOT_FOUND,
                    "marketplace dispute not found",
                )
            if dispute.status != DisputeStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "dispute is not open",
                    details={"status": dispute.status.value},
                )
            self._require_permission(
                ctx,
                action="dispute",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=dispute.listing_id,
                ),
            )
            expected = dispute.version
            dispute.status = DisputeStatus.RESOLVED
            dispute.resolution = cleaned
            dispute.resolved_by_subject_id = ctx.subject_id
            dispute.resolved_at = datetime.now(timezone.utc)
            dispute.version = expected + 1
            self._repo.save_dispute(dispute, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Marketplace.ResolveDispute",
                resource=f"marketplace_dispute:{dispute.id}",
                result="ok",
                details={
                    "listing_id": str(dispute.listing_id),
                    "authority": "publisher_tenant",
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_revenue_share(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        platform_share_bps: int | None = None,
        share_ratio: float | None = None,
    ) -> KernelResult[bool]:
        try:
            listing = self._require_listing(ctx, listing_id, writable=True)
            assert ctx.tenant_id is not None
            if share_ratio is not None and platform_share_bps is None:
                platform_share_bps = int(round(float(share_ratio) * 10_000))
            bps = normalize_platform_share_bps(platform_share_bps)
            self._require_permission(
                ctx,
                action="revenue_share",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            now = datetime.now(timezone.utc)
            self._repo.upsert_revenue_share(
                ListingRevenueShare(
                    listing_id=listing.id,
                    tenant_id=ctx.tenant_id,
                    platform_share_bps=bps,
                    updated_at=now,
                )
            )
            audit = self._audit.record(
                ctx,
                action="Marketplace.SetRevenueShare",
                resource=f"marketplace_listing:{listing.id}",
                result="ok",
                details={
                    "platform_share_bps": bps,
                    "publisher_share_bps": 10_000 - bps,
                    "default_if_unset": DEFAULT_PLATFORM_SHARE_BPS,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def record_internal_payment_clearing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        invoice_id: UUID,
        note: str = "",
    ) -> KernelResult[UUID]:
        """Record an internal payment-clearing acknowledgment (PHX-G162).

        Links to an existing invoice. Does **not** call an external PSP.
        External capture / refund / arbitration remain
        ``MARKETPLACE_COMMERCIAL_POLICY_REQUIRED``.
        """

        try:
            listing = self._require_listing(ctx, listing_id)
            assert ctx.tenant_id is not None
            self._require_permission(
                ctx,
                action="payment_clearing",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="marketplace_listing",
                    resource_id=listing.id,
                ),
            )
            invoice = self._repo.get_invoice(invoice_id)
            if (
                invoice is None
                or invoice.listing_id != listing.id
                or invoice.tenant_id != ctx.tenant_id
            ):
                raise KernelError(
                    ErrorCode.MARKETPLACE_NOT_FOUND,
                    "marketplace invoice not found for listing",
                    details={
                        "listing_id": str(listing.id),
                        "invoice_id": str(invoice_id),
                    },
                )
            if invoice.status != InvoiceStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "only issued invoices can be internally cleared",
                    details={"invoice_id": str(invoice_id), "status": invoice.status.value},
                )
            clearing_id = uuid4()
            cleaned_note = note.strip()
            audit = self._audit.record(
                ctx,
                action="Marketplace.InternalPaymentClearing",
                resource=f"marketplace_payment_clearing:{clearing_id}",
                result="ok",
                details={
                    "clearing_id": str(clearing_id),
                    "listing_id": str(listing.id),
                    "invoice_id": str(invoice.id),
                    "amount": invoice.amount,
                    "currency": invoice.currency,
                    "settlement_rail": "internal_record_only",
                    "external_psp": False,
                    "note": cleaned_note,
                },
            )
            return KernelResult.success(clearing_id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def deny_unsupported_commercial(
        self,
        ctx: ExecutionContext,
        *,
        operation: str,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        """Keep deferred commercial features fail-closed (external PSP, metering, etc.)."""

        try:
            require_context(ctx, tenant_data_plane=True)
            raise KernelError(
                ErrorCode.MARKETPLACE_COMMERCIAL_POLICY_REQUIRED,
                "commercial operation is outside Foundation policy v1",
                details={"operation": operation, "listing_id": str(listing_id)},
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_listing(
        self,
        ctx: ExecutionContext,
        listing_id: UUID,
        *,
        writable: bool = False,
    ) -> MarketplaceListing:
        require_context(ctx, tenant_data_plane=True)
        listing = self._repo.get_listing(listing_id)
        if listing is None or listing.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.MARKETPLACE_NOT_FOUND,
                "marketplace listing not found",
            )
        if writable and listing.status == ListingStatus.REVOKED:
            raise KernelError(
                ErrorCode.MARKETPLACE_REVOKED,
                "revoked listing cannot be modified",
            )
        return listing

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
