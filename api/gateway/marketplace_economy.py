"""Marketplace economy gate shells (PHX-G400–G402).

Honesty postures only — no external PSP, no bank-file import, no ENABLE_*_NETWORK
invent. Network / PSP flags remain default OFF.
"""

from __future__ import annotations

from typing import Any


def metering_entitlement_product_posture() -> dict[str, Any]:
    """PHX-G400 metering + entitlement shells (fail-closed / declaration-only)."""

    return {
        "metering_product": {
            "surface": "foundation_marketplace_metering_shell",
            "milestone": "PHX-G400",
            "posture": "shell_fail_closed",
            "entitlement_linked": False,
            "external_psp": False,
            "network_default": "off",
            "commercial_auto_write": False,
            "routes": ["/marketplace/status"],
        },
        "entitlement_product": {
            "surface": "foundation_marketplace_entitlement_shell",
            "milestone": "PHX-G400",
            "posture": "shell_declaration_only",
            "auto_grant": False,
            "cap_to_grant_invent": False,
            "commercial_auto_write": False,
            "routes": ["/marketplace/status"],
        },
    }


def billing_record_product_posture() -> dict[str, Any]:
    """PHX-G401 internal billing-record shell (≠ external PSP)."""

    return {
        "surface": "foundation_marketplace_billing_record_shell",
        "milestone": "PHX-G401",
        "posture": "internal_invoice_shell",
        "external_psp": False,
        "enable_psp_network_default": "off",
        "bank_file_import": "deferred",
        "settlement_rail": "internal_record_only_when_clearing_enabled",
        "invoice_surface": "marketplace_listing_invoice",
        "finance_ar_invoice_separate": True,
        "routes": [
            "/marketplace/listings/{listing_id}/invoices",
            "/marketplace/listings/{listing_id}/payment-clearing",
        ],
    }


def dispute_arbitration_product_posture() -> dict[str, Any]:
    """PHX-G402 dispute / external-arbitration fail-closed shell."""

    return {
        "surface": "foundation_marketplace_dispute_arbitration_shell",
        "milestone": "PHX-G402",
        "dispute_surface": "publisher_tenant_resolve",
        "external_arbitration": "fail_closed",
        "external_arbitration_invent": False,
        "commercial_auto_write": False,
        "routes": [
            "/marketplace/listings/{listing_id}/disputes",
            "/marketplace/disputes/{dispute_id}/resolve",
        ],
        "fail_closed_reasons": [
            "external_arbitration_still_fail_closed",
            "no_external_arbiter_api",
            "enable_star_network_default_off",
            "external_psp_still_off",
        ],
    }
