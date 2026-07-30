# Customer Deepen Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| Customer Hierarchy | [customer_hierarchy.md](customer_hierarchy.md) | Strong negative for group/store hierarchy; strong for flat master | `customers`, Customer repository, Customer360 relationships |
| Contacts & Roles | [contacts_roles.md](contacts_roles.md) | Strong for one denormalized contact; absent for roles/decision map | customer fields/templates, Object360, Business Graph vocabulary |
| Customer Status Lifecycle | [customer_status_lifecycle.md](customer_status_lifecycle.md) | Medium for editable labels; absent for freeze/blacklist enforcement | customer edit/dashboard, credit fields, risk heuristics |
| Customer AR Balance View | [ar_balance_view.md](ar_balance_view.md) | Strong for SO−Receipt view and AR-based Statement; absent for reconciliation/currency normalization | Customer360, customer repository, Finance receipts/AR, NDE |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Customer | Quotation | Quote references one flat customer ID |
| Customer | Sales | SO copies one customer ID; no group roll-up |
| Customer | Contacts | One denormalized contact set lives on customer row |
| Customer Status | Quotation/Sales | Status labels do not block new transactions |
| Customer Credit | Finance | Balance thresholds are display heuristics, not credit hold |
| Customer AR View | Receipts | Customer balance falls when Receipt rows are added |
| Customer AR View | AR Ledger | No automatic reconciliation with `ar_records` |
| Customer Statement | AR Ledger | NDE prints `ar_records.balance`, not the Customer360 operating balance |
| Customer360 | Object360 | Runtime derives views from Legacy context; Legacy remains authoritative |

## Coverage and hard-threshold check

| Body | Rules | Validations | Data semantics | Evidence rows | UNKNOWN with searched paths |
|------|------:|------------:|---------------:|--------------:|----------------------------:|
| `customer_hierarchy.md` | 19 | 13 | 20 | 16 | 9 |
| `contacts_roles.md` | 20 | 14 | 18 | 16 | 9 |
| `customer_status_lifecycle.md` | 21 | 14 | 17 | 15 | 9 |
| `ar_balance_view.md` | 23 | 15 | 17 | 17 | 9 |

## Critical honesty findings

1. Legacy has no observed customer parent/group/store model; platform organizations and distributor regions are separate domains.
2. A customer has only one overwritable contact set and no structured decision-role or consent lifecycle.
3. Customer status is free-form at service level and uses conflicting `status`/`customer_status` vocabularies.
4. Paused or invalid labels do not prevent quotation, order, delivery or receipt activity.
5. Credit fields are not connected to transaction gates; Customer360 bands are amount-based heuristics.
6. Customer blacklist/freeze was not found; `ip_blacklist` belongs to security controls.
7. Customer AR Balance is raw SO total minus Receipt total, independent of `ar_records`.
8. Customer Statement instead prints `ar_records`; one customer surface can therefore expose two unexplained totals.
9. Customer balance directly sums values across records without currency normalization and may become negative.
10. Customer detail and `/ar` lack complete route-level permission/owner gates, creating exposure risk.
11. Customer deletion cascades into quotes, sales orders and receipts rather than preserving financial history.

## Search coverage

Required areas inspected:

- `apps/customer/**`
- `core/customer/**`
- `apps/finance/**`
- `core/object360/customer/**` and finance Object360
- related `templates/**`
- `business_modules/**`
- `docs/reports/**`
- full-repo keyword families: hierarchy/parent/group/head office/branch/store, contact/role/decision maker/primary/consent, status/freeze/blacklist/credit hold, balance/receivable/receipt/reconciliation.
