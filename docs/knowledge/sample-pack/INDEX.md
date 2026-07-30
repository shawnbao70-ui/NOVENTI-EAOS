# Sample Knowledge Pack — Index

**Verified:** 2026-07-24 · Assembles PHX-G290…G292 only · Writable home: `docs/knowledge/sample-pack/**`

## Linked extract modules

Read in chain order for Terminal demo / Research observation.

| Stage | Module | Extract file | Milestone |
|-------|--------|--------------|-----------|
| CRM | Customer | [customer.md](../legacy-extract/crm/customer.md) | PHX-G290 |
| CRM | Opportunity | [opportunity.md](../legacy-extract/crm/opportunity.md) | PHX-G290 |
| CRM | Contract (absence) | [contract.md](../legacy-extract/crm/contract.md) | PHX-G290 |
| CRM | Quotation | [quotation.md](../legacy-extract/crm/quotation.md) | PHX-G290 |
| Sales | Sales Order | [sales_order.md](../legacy-extract/sales/sales_order.md) | PHX-G290 |
| Delivery | Delivery Order | [delivery_order.md](../legacy-extract/delivery/delivery_order.md) | PHX-G292 |
| Finance | Receipts / dual AR | [receipts_ar.md](../legacy-extract/finance/receipts_ar.md) | PHX-G291 |
| Finance | Receivables / Payables | [receivables-payables.md](../legacy-extract/finance/receivables-payables.md) | PHX-G291 |
| Finance | Invoices (fragmented) | [invoices.md](../legacy-extract/finance/invoices.md) | PHX-G291 |
| Finance | Pricing | [pricing.md](../legacy-extract/finance/pricing.md) | PHX-G291 |
| Finance | Settlement / commission | [settlement-rules.md](../legacy-extract/finance/settlement-rules.md) | PHX-G291 |

Pack indexes: [crm/INDEX](../legacy-extract/crm/INDEX.md) · [sales/INDEX](../legacy-extract/sales/INDEX.md) · [delivery/INDEX](../legacy-extract/delivery/INDEX.md) · [finance/INDEX](../legacy-extract/finance/INDEX.md) · root [legacy-extract/README](../legacy-extract/README.md)

## Assembly notes

| File | Focus |
|------|-------|
| [assembled_chain.md](assembled_chain.md) | Quote→SO→DO→Ship→AR / receipts conclusions |
| [usage.md](usage.md) | How to use this pack without inventing product surfaces |
| [fail_closed.md](fail_closed.md) | Brain / Twin / PSP holds |

## Pack rules

- Knowledge assembly only — paraphrase conclusions; cite extract paths; never copy Legacy source.
- Gaps and contradictions stay explicit (dual AR, Contract absence, DO→AR vs tax invoice).
- Deepen packs are out of scope for this acceptance.
