# Coding Authorization Summary — Tax Void + Red-Credit (G360)

## Milestone

**PHX-G360** — ADR-0316.4 void + 红冲/贷项 shell.

## Alembic

**`0083_finance_tax_red_credit_g360`** revising `0082_…`.

## Note

Void already exists — deepen with **red-credit**: explicit command creating a
linked credit tax invoice (negative/credit) against an **issued** original;
idempotent; human_confirm; cannot red-credit voided/draft; void path remains
and stays audited. Print labels alone ≠ red-credit.

## Authorized

1. `create_tax_red_credit` / HTTP POST
   `/v1/finance/tax-invoices/{id}/red-credits`
2. Persist `original_tax_invoice_id` on credit invoice; status draft then issue
   optional separate or issue-in-command with human_confirm — prefer create
   draft credit + existing issue path, or atomic issued credit; document.
3. Contracts: void still works; red-credit links; deny on draft/voided original.
4. Do not expand ENABLE_TAX_NETWORK behavior.

## Out

Refund (G361), AP write-off, baseline.

## Product Owner response

**Approve — batch; auto-continue G361.**
