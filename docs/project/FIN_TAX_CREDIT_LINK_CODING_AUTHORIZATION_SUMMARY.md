# Coding Authorization Summary — Tax Invoice ↔ Credit Note Link (G344)

## Milestone

**PHX-G344** — controlled tax invoice ↔ AR credit note link shell.

## Alembic

**`0071_finance_tax_credit_link_g344`** revising
`0070_crm_cn_rma_issue_link_g343` (adjust if tip differs).

## Authorized

1. Explicit link (or create-link) between issued TaxInvoice and issued/draft
   ARCreditNote sharing invoice/customer lineage; fail-closed on mismatch.
2. Idempotent; Permission + audit; HTTP under finance.
3. Do not expand NETWORK tax adapter behavior; respect ENABLE_TAX_NETWORK.

## Out

Cap→grant, Brain silent writes, host installs, silent void of tax on restock.

## Product Owner response

**Approve — batch includes G344.** Auto-continue to G345.
