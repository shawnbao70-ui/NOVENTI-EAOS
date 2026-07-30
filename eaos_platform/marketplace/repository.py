"""In-memory Marketplace repository."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol
from uuid import UUID

from eaos_platform.marketplace.models import (
    ListingPricing,
    ListingRevenueShare,
    MarketplaceAcquisition,
    MarketplaceDispute,
    MarketplaceInvoice,
    MarketplaceListing,
)
from kernel.shared.errors import ErrorCode, KernelError


class MarketplaceRepository(Protocol):
    def add_listing(self, listing: MarketplaceListing) -> None: ...

    def get_listing(self, listing_id: UUID) -> MarketplaceListing | None: ...

    def save_listing(
        self,
        listing: MarketplaceListing,
        *,
        expected_version: int,
    ) -> None: ...

    def add_acquisition(self, acquisition: MarketplaceAcquisition) -> None: ...

    def get_acquisition_by_listing(
        self,
        *,
        tenant_id: UUID,
        listing_id: UUID,
    ) -> MarketplaceAcquisition | None: ...

    def upsert_pricing(self, pricing: ListingPricing) -> None: ...

    def get_pricing(self, listing_id: UUID) -> ListingPricing | None: ...

    def upsert_revenue_share(self, share: ListingRevenueShare) -> None: ...

    def get_revenue_share(self, listing_id: UUID) -> ListingRevenueShare | None: ...

    def add_invoice(self, invoice: MarketplaceInvoice) -> None: ...

    def get_invoice(self, invoice_id: UUID) -> MarketplaceInvoice | None: ...

    def add_dispute(self, dispute: MarketplaceDispute) -> None: ...

    def get_dispute(self, dispute_id: UUID) -> MarketplaceDispute | None: ...

    def save_dispute(
        self,
        dispute: MarketplaceDispute,
        *,
        expected_version: int,
    ) -> None: ...


class InMemoryMarketplaceRepository:
    def __init__(self) -> None:
        self._listings: dict[UUID, MarketplaceListing] = {}
        self._acquisitions: dict[UUID, MarketplaceAcquisition] = {}
        self._pricing: dict[UUID, ListingPricing] = {}
        self._revenue_share: dict[UUID, ListingRevenueShare] = {}
        self._invoices: dict[UUID, MarketplaceInvoice] = {}
        self._disputes: dict[UUID, MarketplaceDispute] = {}

    def add_listing(self, listing: MarketplaceListing) -> None:
        self._listings[listing.id] = deepcopy(listing)

    def get_listing(self, listing_id: UUID) -> MarketplaceListing | None:
        item = self._listings.get(listing_id)
        return deepcopy(item) if item is not None else None

    def save_listing(
        self,
        listing: MarketplaceListing,
        *,
        expected_version: int,
    ) -> None:
        current = self._listings.get(listing.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "marketplace listing version conflict")
        self._listings[listing.id] = deepcopy(listing)

    def add_acquisition(self, acquisition: MarketplaceAcquisition) -> None:
        self._acquisitions[acquisition.id] = deepcopy(acquisition)

    def get_acquisition_by_listing(
        self,
        *,
        tenant_id: UUID,
        listing_id: UUID,
    ) -> MarketplaceAcquisition | None:
        for item in self._acquisitions.values():
            if item.tenant_id == tenant_id and item.listing_id == listing_id:
                return deepcopy(item)
        return None

    def upsert_pricing(self, pricing: ListingPricing) -> None:
        current = self._pricing.get(pricing.listing_id)
        if current is not None:
            pricing.version = current.version + 1
        self._pricing[pricing.listing_id] = deepcopy(pricing)

    def get_pricing(self, listing_id: UUID) -> ListingPricing | None:
        item = self._pricing.get(listing_id)
        return deepcopy(item) if item is not None else None

    def upsert_revenue_share(self, share: ListingRevenueShare) -> None:
        current = self._revenue_share.get(share.listing_id)
        if current is not None:
            share.version = current.version + 1
        self._revenue_share[share.listing_id] = deepcopy(share)

    def get_revenue_share(self, listing_id: UUID) -> ListingRevenueShare | None:
        item = self._revenue_share.get(listing_id)
        return deepcopy(item) if item is not None else None

    def add_invoice(self, invoice: MarketplaceInvoice) -> None:
        self._invoices[invoice.id] = deepcopy(invoice)

    def get_invoice(self, invoice_id: UUID) -> MarketplaceInvoice | None:
        item = self._invoices.get(invoice_id)
        return deepcopy(item) if item is not None else None

    def add_dispute(self, dispute: MarketplaceDispute) -> None:
        self._disputes[dispute.id] = deepcopy(dispute)

    def get_dispute(self, dispute_id: UUID) -> MarketplaceDispute | None:
        item = self._disputes.get(dispute_id)
        return deepcopy(item) if item is not None else None

    def save_dispute(
        self,
        dispute: MarketplaceDispute,
        *,
        expected_version: int,
    ) -> None:
        current = self._disputes.get(dispute.id)
        if current is None or current.version != expected_version:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "marketplace dispute version conflict")
        self._disputes[dispute.id] = deepcopy(dispute)
