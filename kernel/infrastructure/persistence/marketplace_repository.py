"""Tenant-bound SQLAlchemy adapter for Marketplace Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

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
from kernel.infrastructure.persistence.marketplace_models import (
    MarketplaceAcquisitionRecord,
    MarketplaceDisputeRecord,
    MarketplaceInvoiceRecord,
    MarketplaceListingRecord,
    MarketplacePricingRecord,
    MarketplaceRevenueShareRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyMarketplaceRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_listing(self, listing: MarketplaceListing) -> None:
        self._require_tenant(listing.tenant_id)
        self._session.add(
            MarketplaceListingRecord(
                id=listing.id,
                tenant_id=listing.tenant_id,
                package_key=listing.package_key,
                package_version=listing.package_version,
                publisher_subject_id=listing.publisher_subject_id,
                status=listing.status.value,
                signature_ref=listing.signature_ref,
                review_notes=listing.review_notes,
                required_permissions_json=sorted(listing.capability.required_permissions),
                declared_events_json=sorted(listing.capability.declared_events),
                data_scope=listing.capability.data_scope,
                created_at=listing.created_at,
                updated_at=listing.updated_at,
                version=listing.version,
            )
        )

    def get_listing(self, listing_id: UUID) -> MarketplaceListing | None:
        record = self._session.scalar(
            select(MarketplaceListingRecord).where(
                MarketplaceListingRecord.id == listing_id,
                MarketplaceListingRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_listing(record) if record is not None else None

    def save_listing(
        self,
        listing: MarketplaceListing,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(listing.tenant_id)
        result = self._session.execute(
            update(MarketplaceListingRecord)
            .where(
                MarketplaceListingRecord.id == listing.id,
                MarketplaceListingRecord.tenant_id == listing.tenant_id,
                MarketplaceListingRecord.version == expected_version,
            )
            .values(
                status=listing.status.value,
                signature_ref=listing.signature_ref,
                review_notes=listing.review_notes,
                updated_at=listing.updated_at,
                version=listing.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "marketplace listing version conflict",
            )

    def add_acquisition(self, acquisition: MarketplaceAcquisition) -> None:
        self._require_tenant(acquisition.tenant_id)
        self._session.add(
            MarketplaceAcquisitionRecord(
                id=acquisition.id,
                tenant_id=acquisition.tenant_id,
                listing_id=acquisition.listing_id,
                package_key=acquisition.package_key,
                package_version=acquisition.package_version,
                acquired_by_subject_id=acquisition.acquired_by_subject_id,
                created_at=acquisition.created_at,
                version=acquisition.version,
            )
        )

    def get_acquisition_by_listing(
        self,
        *,
        tenant_id: UUID,
        listing_id: UUID,
    ) -> MarketplaceAcquisition | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(MarketplaceAcquisitionRecord).where(
                MarketplaceAcquisitionRecord.tenant_id == tenant_id,
                MarketplaceAcquisitionRecord.listing_id == listing_id,
            )
        )
        return self._to_acquisition(record) if record is not None else None

    def upsert_pricing(self, pricing: ListingPricing) -> None:
        self._require_tenant(pricing.tenant_id)
        current = self._session.scalar(
            select(MarketplacePricingRecord).where(
                MarketplacePricingRecord.listing_id == pricing.listing_id,
                MarketplacePricingRecord.tenant_id == pricing.tenant_id,
            )
        )
        if current is None:
            self._session.add(
                MarketplacePricingRecord(
                    listing_id=pricing.listing_id,
                    tenant_id=pricing.tenant_id,
                    pricing_model=pricing.pricing_model,
                    amount=pricing.amount,
                    currency=pricing.currency,
                    updated_at=pricing.updated_at,
                    version=1,
                )
            )
            return
        result = self._session.execute(
            update(MarketplacePricingRecord)
            .where(
                MarketplacePricingRecord.listing_id == pricing.listing_id,
                MarketplacePricingRecord.tenant_id == pricing.tenant_id,
                MarketplacePricingRecord.version == current.version,
            )
            .values(
                pricing_model=pricing.pricing_model,
                amount=pricing.amount,
                currency=pricing.currency,
                updated_at=pricing.updated_at,
                version=current.version + 1,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "marketplace pricing version conflict")

    def get_pricing(self, listing_id: UUID) -> ListingPricing | None:
        record = self._session.scalar(
            select(MarketplacePricingRecord).where(
                MarketplacePricingRecord.listing_id == listing_id,
                MarketplacePricingRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return ListingPricing(
            listing_id=record.listing_id,
            tenant_id=record.tenant_id,
            pricing_model=record.pricing_model,
            amount=record.amount,
            currency=record.currency,
            updated_at=record.updated_at,
            version=record.version,
        )

    def upsert_revenue_share(self, share: ListingRevenueShare) -> None:
        self._require_tenant(share.tenant_id)
        current = self._session.scalar(
            select(MarketplaceRevenueShareRecord).where(
                MarketplaceRevenueShareRecord.listing_id == share.listing_id,
                MarketplaceRevenueShareRecord.tenant_id == share.tenant_id,
            )
        )
        if current is None:
            self._session.add(
                MarketplaceRevenueShareRecord(
                    listing_id=share.listing_id,
                    tenant_id=share.tenant_id,
                    platform_share_bps=share.platform_share_bps,
                    updated_at=share.updated_at,
                    version=1,
                )
            )
            return
        result = self._session.execute(
            update(MarketplaceRevenueShareRecord)
            .where(
                MarketplaceRevenueShareRecord.listing_id == share.listing_id,
                MarketplaceRevenueShareRecord.tenant_id == share.tenant_id,
                MarketplaceRevenueShareRecord.version == current.version,
            )
            .values(
                platform_share_bps=share.platform_share_bps,
                updated_at=share.updated_at,
                version=current.version + 1,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "marketplace revenue share version conflict",
            )

    def get_revenue_share(self, listing_id: UUID) -> ListingRevenueShare | None:
        record = self._session.scalar(
            select(MarketplaceRevenueShareRecord).where(
                MarketplaceRevenueShareRecord.listing_id == listing_id,
                MarketplaceRevenueShareRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return ListingRevenueShare(
            listing_id=record.listing_id,
            tenant_id=record.tenant_id,
            platform_share_bps=record.platform_share_bps,
            updated_at=record.updated_at,
            version=record.version,
        )

    def add_invoice(self, invoice: MarketplaceInvoice) -> None:
        self._require_tenant(invoice.tenant_id)
        self._session.add(
            MarketplaceInvoiceRecord(
                id=invoice.id,
                tenant_id=invoice.tenant_id,
                listing_id=invoice.listing_id,
                amount=invoice.amount,
                currency=invoice.currency,
                billing_cycle=invoice.billing_cycle,
                status=invoice.status.value,
                issued_by_subject_id=invoice.issued_by_subject_id,
                created_at=invoice.created_at,
                version=invoice.version,
            )
        )

    def get_invoice(self, invoice_id: UUID) -> MarketplaceInvoice | None:
        record = self._session.scalar(
            select(MarketplaceInvoiceRecord).where(
                MarketplaceInvoiceRecord.id == invoice_id,
                MarketplaceInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return MarketplaceInvoice(
            id=record.id,
            tenant_id=record.tenant_id,
            listing_id=record.listing_id,
            amount=record.amount,
            currency=record.currency,
            billing_cycle=record.billing_cycle,
            status=InvoiceStatus(record.status),
            issued_by_subject_id=record.issued_by_subject_id,
            created_at=record.created_at,
            version=record.version,
        )

    def add_dispute(self, dispute: MarketplaceDispute) -> None:
        self._require_tenant(dispute.tenant_id)
        self._session.add(
            MarketplaceDisputeRecord(
                id=dispute.id,
                tenant_id=dispute.tenant_id,
                listing_id=dispute.listing_id,
                reason=dispute.reason,
                status=dispute.status.value,
                opened_by_subject_id=dispute.opened_by_subject_id,
                resolution=dispute.resolution,
                resolved_by_subject_id=dispute.resolved_by_subject_id,
                created_at=dispute.created_at,
                resolved_at=dispute.resolved_at,
                version=dispute.version,
            )
        )

    def get_dispute(self, dispute_id: UUID) -> MarketplaceDispute | None:
        record = self._session.scalar(
            select(MarketplaceDisputeRecord).where(
                MarketplaceDisputeRecord.id == dispute_id,
                MarketplaceDisputeRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return MarketplaceDispute(
            id=record.id,
            tenant_id=record.tenant_id,
            listing_id=record.listing_id,
            reason=record.reason,
            status=DisputeStatus(record.status),
            opened_by_subject_id=record.opened_by_subject_id,
            created_at=record.created_at,
            resolution=record.resolution,
            resolved_by_subject_id=record.resolved_by_subject_id,
            resolved_at=record.resolved_at,
            version=record.version,
        )

    def save_dispute(
        self,
        dispute: MarketplaceDispute,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(dispute.tenant_id)
        result = self._session.execute(
            update(MarketplaceDisputeRecord)
            .where(
                MarketplaceDisputeRecord.id == dispute.id,
                MarketplaceDisputeRecord.tenant_id == dispute.tenant_id,
                MarketplaceDisputeRecord.version == expected_version,
            )
            .values(
                status=dispute.status.value,
                resolution=dispute.resolution,
                resolved_by_subject_id=dispute.resolved_by_subject_id,
                resolved_at=dispute.resolved_at,
                version=dispute.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "marketplace dispute version conflict")

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(ErrorCode.COMMON_INTERNAL, "tenant boundary violation")

    @staticmethod
    def _to_listing(record: MarketplaceListingRecord) -> MarketplaceListing:
        return MarketplaceListing(
            id=record.id,
            tenant_id=record.tenant_id,
            package_key=record.package_key,
            package_version=record.package_version,
            publisher_subject_id=record.publisher_subject_id,
            status=ListingStatus(record.status),
            capability=CapabilityDeclaration(
                required_permissions=frozenset(record.required_permissions_json),
                declared_events=frozenset(record.declared_events_json),
                data_scope=record.data_scope,
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
            signature_ref=record.signature_ref,
            review_notes=record.review_notes,
            version=record.version,
        )

    @staticmethod
    def _to_acquisition(record: MarketplaceAcquisitionRecord) -> MarketplaceAcquisition:
        return MarketplaceAcquisition(
            id=record.id,
            tenant_id=record.tenant_id,
            listing_id=record.listing_id,
            package_key=record.package_key,
            package_version=record.package_version,
            acquired_by_subject_id=record.acquired_by_subject_id,
            created_at=record.created_at,
            version=record.version,
        )
