# Commission Ledger Deepen — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| Commission on Convert | [commission_on_convert.md](commission_on_convert.md) | Strong for Sales writer; mixed for atomicity/idempotency | Sales convert service/repository, TC ledger |
| Commission Rate Source | [commission_rate_source.md](commission_rate_source.md) | Strong for level lookup; absent for executable Center rules | salespersons, sales_levels, commission_rules |
| TC Ledger States | [tc_ledger_states.md](tc_ledger_states.md) | Strong for Pending/read-only; strong negative for transitions | TC writer, residual route, template |
| Commission–Finance Boundary | [commission_finance_boundary.md](commission_finance_boundary.md) | Strong for Sales ownership; absent for Finance payout | Sales, Finance/Treasury/AP/Payroll adjacent paths |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Quote→SO | TC Ledger | Best-effort Pending calculation snapshot |
| Salesperson | Sales Level | `level_id` selects canonical rate |
| Sales Level | TC Ledger | rate is copied into row at conversion |
| Commission Rules | Commission Center | Display/maintenance only; no execution link |
| Commission Calculator | salesperson_commissions | Received-amount demo, separate from TC |
| Commission Period | TC Ledger | No native link or closing effect |
| TC Ledger | Finance | No approval, payable, expense or payout bridge |
| Treasury/AP/Payroll | TC Ledger | No observed foreign key or consumer |

## Coverage and hard-threshold check

| Body | Rules | Validations | Data semantics | Evidence rows | UNKNOWN with searched paths |
|------|------:|------------:|---------------:|--------------:|----------------------------:|
| `commission_on_convert.md` | 22 | 12 | 16 | 14 | 9 |
| `commission_rate_source.md` | 24 | 12 | 19 | 15 | 10 |
| `tc_ledger_states.md` | 23 | 12 | 16 | 15 | 9 |
| `commission_finance_boundary.md` | 24 | 12 | 16 | 16 | 9 |

## Critical honesty findings

1. Canonical commission uses SO total, not receipt amount or profit.
2. `sales_levels.commission_rate` is the execution source; `commission_rules` is disconnected.
3. SO commission columns, distributor rates and collection-based helpers are parallel sources, not canonical inputs.
4. Missing salesperson skips commission; missing level/rate can create a zero-rate row.
5. Commission write failure is silent and does not roll back SO creation.
6. No unique source constraint, retry queue or cancellation reversal was observed.
7. Default A/B/C rates are seed data with uncertain business meaning.
8. New sales level form accepts data but its INSERT is commented out.
9. TC ledger has only a proven Pending writer and read-only page.
10. `/tc_ledger` has no route permission gate; `Commission` and `Commission Center` permission names are inconsistent.
11. Period, rebate, generic commission and calculator tables are parallel facts, not one state machine.
12. Finance owns no observed TC consumer, approval, payable, expense, payroll or payout path.
13. Registry dual ownership does not establish accounting authority.

## Search coverage

Required areas inspected:

- `apps/sales/**`
- `apps/finance/**`
- commission, TC ledger, sales level, salesperson, rebate, period and calculator paths
- related `templates/**`
- `business_modules/**` and `Business_Module_Registry.md`
- `docs/reports/**`
- runtime V14 schema/seed and route ownership paths

Existing `sales/sales_order.md` and `finance/settlement-rules.md` were read only for cross-reference and not modified.
