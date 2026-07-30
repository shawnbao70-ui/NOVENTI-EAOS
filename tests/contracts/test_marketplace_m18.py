"""PHX-M18 Marketplace package signature cryptography contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from eaos_platform.marketplace.service import MarketplaceService
from eaos_platform.marketplace.signing import (
    MarketplaceSigningSettings,
    sign_listing_ed25519_v1,
    sign_listing_hmac_v1,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
PUBLISHER_ID = uuid4()
HMAC_SECRET = "marketplace-signing-secret-32b"


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _granted_market(
    signing: MarketplaceSigningSettings,
) -> tuple[MarketplaceService, ExecutionContext]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    tenant_id = uuid4()
    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=PUBLISHER_ID,
        resource_type="marketplace_listing",
        actions={"create", "submit", "review", "publish", "revoke", "read"},
    ).ok
    market = MarketplaceService(permission, signing=signing)
    return market, _ctx(tenant_id, PUBLISHER_ID)


def _create_listing(market: MarketplaceService, publisher: ExecutionContext) -> UUID:
    created = market.create_listing(
        publisher,
        package_key="noventi.signed.pkg",
        package_version="1.2.0",
        required_permissions=["pkg.signed:read"],
        declared_events=["pkg.signed.ready"],
        data_scope="tenant.signed",
    )
    assert created.data is not None
    return created.data


def test_hmac_signing_accepts_valid_and_rejects_invalid() -> None:
    market, publisher = _granted_market(
        MarketplaceSigningSettings(mode="hmac", required=True, hmac_secret=HMAC_SECRET)
    )
    listing_id = _create_listing(market, publisher)
    listing = market.get_listing(publisher, listing_id=listing_id)
    assert listing.data is not None
    good = sign_listing_hmac_v1(secret=HMAC_SECRET, listing=listing.data)
    assert market.attach_signature(
        publisher,
        listing_id=listing_id,
        signature_ref=good,
    ).ok
    bad = market.attach_signature(
        publisher,
        listing_id=listing_id,
        signature_ref="v1:hmac-sha256:" + ("0" * 64),
    )
    assert bad.error_code == ErrorCode.MARKETPLACE_SIGNATURE_INVALID
    opaque = market.attach_signature(
        publisher,
        listing_id=listing_id,
        signature_ref="sig:demo",
    )
    assert opaque.error_code == ErrorCode.MARKETPLACE_SIGNATURE_INVALID


def test_required_unconfigured_fail_closed() -> None:
    market, publisher = _granted_market(
        MarketplaceSigningSettings(mode="off", required=True)
    )
    listing_id = _create_listing(market, publisher)
    denied = market.attach_signature(
        publisher,
        listing_id=listing_id,
        signature_ref="sig:opaque",
    )
    assert denied.error_code == ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED


def test_hmac_publish_lifecycle() -> None:
    market, publisher = _granted_market(
        MarketplaceSigningSettings(mode="hmac", required=True, hmac_secret=HMAC_SECRET)
    )
    listing_id = _create_listing(market, publisher)
    listing = market.get_listing(publisher, listing_id=listing_id)
    assert listing.data is not None
    sig = sign_listing_hmac_v1(secret=HMAC_SECRET, listing=listing.data)
    assert market.attach_signature(
        publisher, listing_id=listing_id, signature_ref=sig
    ).ok
    assert market.submit_for_review(publisher, listing_id=listing_id).ok
    assert market.review_listing(publisher, listing_id=listing_id, approve=True).ok
    assert market.publish_listing(publisher, listing_id=listing_id).ok


def test_ed25519_signing_round_trip() -> None:
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    private_key = ed25519.Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    market, publisher = _granted_market(
        MarketplaceSigningSettings(
            mode="ed25519",
            required=True,
            ed25519_public_key_pem=public_pem,
        )
    )
    listing_id = _create_listing(market, publisher)
    listing = market.get_listing(publisher, listing_id=listing_id)
    assert listing.data is not None
    sig = sign_listing_ed25519_v1(private_key_pem=private_pem, listing=listing.data)
    assert market.attach_signature(
        publisher, listing_id=listing_id, signature_ref=sig
    ).ok
    assert market.submit_for_review(publisher, listing_id=listing_id).ok
