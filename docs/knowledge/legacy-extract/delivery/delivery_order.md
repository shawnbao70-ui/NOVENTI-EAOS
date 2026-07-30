# 发货单（Delivery Order）— Legacy Knowledge

**Evidence strength:** Strong (Inventory ship + Sales create)  
**Chain role:** SO → DO (no stock) → Ship (stock) → Complete; optional DO → AR accrual  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Three-module handoff: **Sales** creates DO; **Inventory** ships/completes; **Finance** inserts `ar_records` from Type A “invoice” (not tax invoice). Dual create paths (`/create_do` vs `/convert_do`) differ in numbering and SO status side-effects.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| D-R1 | Create DO copies all SO lines; **no stock decrement on create** (A-003) | `/create_do` | Pre-A-003 data may already have decremented | Single create path; never stock-on-create |
| D-R2 | Canonical DO no `DO{YYYYMMDDHHMMSS}`; convert_do uses `DO{so_id:04d}` | Create paths | Dual generators | Unify numbering |
| D-R3 | Canonical create sets SO → `Delivery Created`; convert_do does not | create_do | — | One side-effect policy |
| D-R4 | Initial DO status Pending / 待出库 | Create | — | Canonical open stage |
| D-R5 | Ship only when open; ledger `DO Ship` / `DO-{do_no}` makes ship idempotent | Type A ship | Already shipped blocked | Keep ledger idempotency |
| D-R6 | Ship dual-writes inventory + products stock + ledger; insufficient stock hard-blocks | Ship | Auto-ensure inventory row from product | Single stock truth |
| D-R7 | After ship → 已出库/Shipped; Complete only from shipped → Delivered (+ SO Delivered) | Complete | — | State machine |
| D-R8 | Reopen from complete is status-only — **no stock restore** | Reopen | — | Explicit inventory adjust |
| D-R9 | Type A DO invoice → `ar_records` Unpaid; not tax invoice; ship not required (warn only) | Invoice approve | Duplicate AR warn-only | Block duplicates; link FK |
| D-R10 | Receipts remain SO-scoped — not DO | Finance parallel | — | Settle AR vs receipts deliberately |
| D-R11 | List ownership via salesperson like Sales | List | Admin/Manager all | Stable FK |
| D-R12 | `/create_do` often **lacks server permission check** (UI-only) | Create | convert_do needs Sales Orders edit | Always server-gate |
| D-R13 | No partial delivery / no one-DO-per-SO enforcement | Create | Multiple DOs structurally allowed | Product decision |

---

## 3. 流程

`SO → create_do (Open) → Type A Ship → Shipped → complete → Delivered`  
Parallel: `DO → Type A Invoice → ar_records` then later `SO → receipt`.

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| D-V1 | SO exists on create | Hard | |
| D-V2 | Ship: open stage + stock + ledger idempotency | Hard | |
| D-V3 | Complete: shipped only | Hard | |
| D-V4 | Type A human_confirm=`1` | Hard | Ship / Invoice |
| D-V5 | create_do server RBAC | Weak/Absent | UI-gated |
| D-V6 | Duplicate AR / ship-before-AR | Soft warn | |

---

## 5. 数据含义

| Entity | Meaning |
|--------|---------|
| `delivery_orders` | Outbound header linked to SO |
| `delivery_order_items` | Product/qty/price from SO |
| Ship ledger | `inventory_ledger` trans `DO Ship` |
| DO→AR | `ar_records.source_no = do_no` (string link; `ar_no` often unset) |

Status stages: open (Pending…) → shipped (已出库…) → complete (Delivered…).

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/sales/services.py` / `router.py` | create_do; A-003 |
| `apps/inventory/services.py` / `repository.py` / `router.py` | Ship/complete/invoice Type A |
| `apps/finance/services.py` | `_legacy_create_ar` |
| `templates/delivery_order_detail.html` / `do_ship.html` / `do_invoice.html` | UX |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | Create-no-decrement |
| `docs/reports/Business_Strong_A009_Delivery_Ops_Report.md` | Ops honesty |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\`  
**Cross-pack:** [../sales/sales_order.md](../sales/sales_order.md), [../finance/receipts_ar.md](../finance/receipts_ar.md).
