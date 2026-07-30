# Order Chain Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| SO Convert | [so_convert.md](so_convert.md) | Strong for active conversion; mixed for hook completion and route uniqueness | Sales service/repository, Quotation, lifecycle, TC ledger |
| SO Approve → Open | [so_approve_open.md](so_approve_open.md) | Strong for V18 Type A gates; weak for global state machine | Sales approve service/router/template |
| SO → DO | [so_to_do.md](so_to_do.md) | Strong for create/ship separation; mixed for duplicate convert paths | Sales create DO, Inventory Ship |
| SO Payment View | [so_payment_view.md](so_payment_view.md) | Strong for live receipts and mirror writes; absent for AR allocation | Sales detail/list, Finance receipts/AR |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Quote | SO Convert | Header/items copied; quote status becomes `已确认` |
| SO Convert | TC Ledger | Best-effort Pending commission accrual |
| SO Convert | Lifecycle | Best-effort Quote→SO trace link |
| SO Pending | SO Open | V18 Human Approved after at least one line |
| SO | DO | Header/items copied; SO becomes `Delivery Created` |
| DO Pending | Inventory Ship | Stock check and inventory/ledger posting happen here |
| SO | Receipt | Receipt decreases live SO balance and updates mirror fields |
| Receipt | AR Ledger | No automatic allocation or close |

## Coverage and hard-threshold check

| Body | Rules | Validations | Data semantics | Evidence rows | UNKNOWN with searched paths |
|------|------:|------------:|---------------:|--------------:|----------------------------:|
| `so_convert.md` | 23 | 12 | 18 | 16 | 9 |
| `so_approve_open.md` | 23 | 14 | 16 | 17 | 9 |
| `so_to_do.md` | 25 | 14 | 17 | 17 | 9 |
| `so_payment_view.md` | 25 | 14 | 16 | 19 | 9 |

## Critical honesty findings

1. One-quote-one-SO is an application read-before-write guard; database-level uniqueness and concurrent safety remain UNKNOWN.
2. Conversion does not require Quote Sent/Won/Human Approved and can produce an empty SO.
3. Commission and lifecycle link failures are silent and do not roll back SO creation.
4. SO Approve only writes `Open`; no DO, inventory, AR or receipt is posted.
5. Unknown statuses and `Delivery Created` fall into pending stage, so an already-created DO can be followed by Approve→Open; non-Open shortcuts can also directly overwrite status.
6. Active create DO has no hard duplicate, source-state, line, stock or route-permission gate.
7. `Delivery Created` only means the action ran; it is neither reservation nor shipment proof.
8. Inventory is checked and decremented on Ship, not on DO creation.
9. SO detail reads receipts live while list/dashboard read mirrors that start at zero and may remain stale.
10. SO Paid and AR Unpaid may coexist because Receipt does not update `ar_records`.
11. Stored status values mix English, Chinese and translated labels across the chain.

## Search coverage

Required areas inspected:

- `apps/sales/**`
- `apps/inventory/**`
- `apps/finance/**`
- `apps/quotation/**`
- related `templates/**`
- `business_modules/**`
- `docs/reports/**`
- runtime/residual and V15 lifecycle paths needed to establish route and hook boundaries

Cross-references were read from existing `sales/sales_order.md` and finance knowledge without modifying or copying those packs.
