# 收款 / 应收（Receipts & AR）— Legacy Knowledge

**Evidence strength:** Strong for receipt→SO payment sync; Medium for `ar_records` accrual  
**Chain role:** Cash collection on SO; parallel DO-accrual ledger  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Runtime collection uses **`receipts`** + SO payment columns. Formal accrual uses **`ar_records`** (usually from Delivery Order invoice Type A). Spec `business_modules/finance.md` mentions invoices/payments tables that **do not** match this runtime — prefer page services.

Two parallel “AR” notions are **not reconciled in code**.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| F-R1 | Create receipt for **full remaining** SO balance (no amount form) | `GET /create_receipt/{so_id}` | Balance ≤ 0 → mark Paid, no insert | Design partial-payment UX deliberately |
| F-R2 | Receipt no `RC{so_id:04d}-{n}` | Insert | Suffix derived from received total heuristic | Stable sequence generator |
| F-R3 | After receipt, re-sum → update SO `received_amount`, `balance_amount`, `payment_status` ∈ {Paid, Partial} | Finance create_receipt | **Only automated writer** of payment_status after convert | Single collection owner |
| F-R4 | Customer `/ar` outstanding = SUM(SO) − SUM(receipts) | AR customer view | **Ignores `ar_records`** | Choose one KPI source |
| F-R5 | DO invoice Type A → insert `ar_records` Unpaid (amount=DO total, source_no=do_no) | Human confirm approve | Duplicate warn does not block | Accrual ≠ cash |
| F-R6 | Receipt path does **not** settle `ar_records.balance` | Receipt create | — | Build explicit settlement if both kept |
| F-R7 | Non-Admin/Manager see receipts only for SOs they own via salesperson | Receipt list | Admin/Manager all | Align with Sales ownership model |
| F-R8 | AR remind: human confirm + balance > 0 → collection_tasks or followups | Remind POST | No auto-email | Human authorization |
| F-R9 | Convert sets payment_status localized Uncollected; DDL default Unpaid | SO create | Vocabulary split | Normalize enum |
| F-R10 | Treasury supplier payments are AP/outflow — not customer receipts | add_payment_record | Same finance app | Separate capability |

---

## 3. 流程

1. **Cash:** SO → create_receipt → update SO payment fields → `/receipts`  
2. **Accrual:** DO → invoice Type A → `ar_records` Unpaid → `/ar_dashboard`  
3. **Operational AR:** `/ar` from SO−receipts; reminders optional  
4. **Ledger list:** receivable_center from `ar_records`  

Ideal doc chain DO→invoice→receipt is **not** the implemented join.

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| F-V1 | SO exists on receipt | Hard | Else redirect |
| F-V2 | Balance ≤ 0 short-circuit | Hard | Paid, no row |
| F-V3 | AR remind human_confirm=`1` | Hard | |
| F-V4 | AR remind outstanding > 0 | Hard | |
| F-V5 | DO invoice human confirm | Hard | |
| F-V6 | Receipts.add / view RBAC | Medium | `/ar` `/receivables` often ungated |
| F-V7 | `validator.py` amount≥0 | Unused | Not wired |

---

## 5. 数据含义

| Concept | Meaning |
|---------|---------|
| `receipts` | Immutable cash collection event linked to SO |
| SO `payment_status` | Order collection: Uncollected/Unpaid → Partial → Paid |
| `ar_records` | Accrual line (often DO-sourced); Open ≠ Closed |
| Customer AR (`/ar`) | Operational SO−receipts aggregate |
| Receivable center | Formal `ar_records` listing |

**Gap vs Sales pack:** Sales never writes payment_status after convert; Finance is sole updater. SO detail may recompute balance live vs stored columns.

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/finance/services.py` / `repository.py` / `router.py` | Receipt + AR + remind |
| `business_modules/finance.md` | Spec vs runtime mismatch |
| `SALES_FINANCE_MIGRATION_S012.md` | Migration honesty |
| `apps/sales/services.py` | Convert Uncollected; detail balance |
| `apps/inventory/services.py` | DO → AR insert |
| `templates/ar.html` / `receipts.html` / `receivable_center.html` | Surfaces |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | DO invoice Type A |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\`  
**Cross-pack:** [../sales/sales_order.md](../sales/sales_order.md), [../crm/customer.md](../crm/customer.md).
