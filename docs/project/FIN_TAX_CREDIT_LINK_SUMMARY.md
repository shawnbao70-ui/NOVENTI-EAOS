# PHX-G344 Summary — Tax Invoice ↔ Credit Note Link

**Status:** COMPLETE  
**Alembic tip:** `0071_finance_tax_credit_link_g344`

## Delivered

- Finance-owned, tenant-scoped explicit links between an issued tax invoice and
  a draft or issued AR credit note.
- Fail-closed validation for invoice status, shared customer, and shared
  `ar_invoice_id` lineage; idempotency, Permission, and audit are enforced.
- POST/GET HTTP surface at `/v1/finance/tax-credit-links`.

## Boundary confirmation

This slice does not alter tax NETWORK adapters or `ENABLE_TAX_NETWORK`
defaults, and does not void tax invoices or create financial postings.

## Evidence

- Coding authorization:
  `docs/project/FIN_TAX_CREDIT_LINK_CODING_AUTHORIZATION_SUMMARY.md`
- Boundary:
  `docs/decisions/ADR-0376-finance-tax-credit-link-boundary.md`
- Contract test:
  `tests/contracts/test_api_gateway_g344_finance_tax_credit_link.py`
