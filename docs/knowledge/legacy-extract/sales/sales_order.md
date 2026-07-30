# 销售订单（Sales Order）— Legacy Knowledge

**Evidence strength:** Strong (page services) / Medium (core metadata)  
**Domain identity:** Sales owns `sales_orders` / `sales_order_items`  
**Chain role:** Order authority after Quotation convert; upstream of Delivery / AR  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Authoritative convert + list/detail/approve live in `apps/sales` (S012 migrated). Duplicate convert path exists in `apps/quotation/quote_pages.py` (same commercial effect; **no** lifecycle link). `apps/sales/validator.py` is an empty placeholder.

Downstream: Delivery Orders, Finance receipts, Inventory ship — not owned here.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| SO-R1 | One SO per quote — existing `quote_id` → list redirect, no duplicate | `convert_so` | Missing quote → `/quotes` | Orchestration-level idempotency |
| SO-R2 | SO number `SO` + zero-padded quote id (`SOxxxx`) | Successful convert | — | Keep separate series from QT |
| SO-R3 | Convert copies customer / salesperson / quote_date→order_date / total; status ≈ pending delivery; payment ≈ uncollected (i18n strings) | Convert | Locale-specific stored labels | Canonical enum + display label |
| SO-R4 | Convert copies all quote lines → SO lines | After header insert | Empty lines allowed — later blocks V18 SO approve | Prefer gate on non-empty lines |
| SO-R5 | Quote status hard-set to Chinese `已确认` | Convert success | Conflicts with English Quote Won KPIs | Normalize with Quotation pack deliberately |
| SO-R6 | Lifecycle `link_sales_order_from_quote` best-effort | Sales `convert_so` only | Silent fail; **absent** on quote_pages duplicate | Single orchestrator + domain events |
| SO-R7 | Commission → `tc_ledger` Pending from salesperson level rate × amount | Convert | Silent fail; skip if no salesperson | Explicit commission event |
| SO-R8 | Non-Admin/Manager list only SOs whose salesperson **name** = session username | List | Admin/Manager see all | Stable FK, not name match |
| SO-R9 | `POST /create_sales_order` always redirects to convert; form `salesperson_id` ignored | New SO form | Quote salesperson always wins | Remove dead override or wire it |
| SO-R10 | V18 SO Approve: pending-stage + ≥1 line + `human_confirm=1` → status `Open` | Approve POST | Separate from convert; does not create DO | Keep Approve ≠ Convert ≠ Ship |
| SO-R11 | `so_status/.../Open` aliases to approve page | Status shortcut | Other statuses write DB directly | State machine with allowed transitions |
| SO-R12 | `create_do` → DO + items; SO status `Delivery Created`; stock not decremented | Create DO | Stock on ship (Inventory) | Align inventory ship gate |
| SO-R13 | Payment status owned by Finance receipts; Sales detail balances from receipts sum | Receipt post | — | Single payment-state owner |
| SO-R14 | SO hard-delete disabled in UI — cancel via status | List/detail | — | Prefer cancel + retention |
| SO-R15 | Convert has **no** server gate that quote is Sent/Won/Approved | Convert | Client confirm + Sales Orders add permission only | Decide mandatory Quote Approve before convert |

---

## 3. 流程

### 3.1 Quote → SO

1. Confirm convert (UI) → `GET /convert_so/{quote_id}`  
2. Guard: quote exists; no existing SO for quote  
3. Insert SO + copy lines + try commission + set quote `已确认` + try lifecycle link  
4. Redirect SO list  

### 3.2 Post-convert lifecycle (conceptual)

`Pending delivery` → optional V18 Approve → `Open` → optional Create DO → `Delivery Created` → ship / complete / cancel (manual mixed CN/EN) → Finance receipts update payment  

### 3.3 New SO form

Pick quote (+ decorative salesperson) → POST always converts via quote id.

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| SO-V1 | Quote exists on convert | Hard | Else `/quotes` |
| SO-V2 | No duplicate SO for quote | Hard | Else list |
| SO-V3 | V18 approve: pending stage only | Hard | |
| SO-V4 | V18 approve: ≥1 line | Hard | |
| SO-V5 | V18 approve: human_confirm=`1` | Hard | |
| SO-V6 | RBAC `Sales Orders` view/edit/add | Medium | Detail ownership not re-checked |
| SO-V7 | Domain `validator.py` | Absent | Empty placeholder |
| SO-V8 | Quote status / Sent prerequisite | Absent | Not enforced server-side |
| SO-V9 | Arbitrary `so_status/{status}` string | Weak | Direct write |

---

## 5. 数据含义

### 5.1 Entities

| Entity | Meaning | Store |
|--------|---------|-------|
| Sales Order | Commercial order authority | `sales_orders` |
| SO Item | Product line | `sales_order_items` |
| Salesperson | Owner + commission subject | `salespersons` |
| Sales level | Commission rate | `sales_levels` |
| Commission ledger | Accrual on convert | `tc_ledger` |
| Delivery Order | Fulfillment child | `delivery_orders` (+ items) |

### 5.2 Header fields

| Field | Meaning |
|-------|---------|
| `so_no` | `SOxxxx` |
| `quote_id` | Source quote |
| `customer_id` | Sold-to |
| `salesperson_id` | Owner (from quote) |
| `order_date` | From quote date |
| `total_amount` | Header total |
| `status` | Fulfillment lifecycle (mixed CN/EN/i18n) |
| `payment_status` | Collection state (Finance-driven after create) |
| `requirement_id` / `opportunity_id` | Optional traceability |

### 5.3 Status vocabulary (Legacy mix)

| Value / family | V18 stage bucket | Meaning |
|----------------|------------------|---------|
| Pending / 待发货 / empty / null | pending | Post-convert awaiting approve/fulfill |
| `Open` | open | Human-approved (V18) |
| `Delivery Created` | pending-ish | DO created |
| 已发货 / Shipped | shipped | Shipped |
| 已完成 / Completed / Delivered | complete | Done |
| 已取消 / Cancel* | cancelled | Cancelled |

Payment: Uncollected / Partial / Paid (UI).

### 5.4 Gaps vs Quotation pack

- Quote → `已确认` ≠ English `Won`  
- Convert not gated on Quote Approve  
- Dual convert implementations (Sales canonical vs quote_pages)  
- SO Approve → `Open` is a **second** human gate after convert  

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/sales/services.py` | convert_so, commission, V18 approve, list ownership |
| `apps/sales/repository.py` | Persist, dashboard counts, status updates |
| `apps/sales/router.py` | HTTP surface |
| `apps/sales/validator.py` | Empty — honesty gap |
| `apps/sales/v14_residual.py` | Parallel commission / residual UI |
| `core/sales/sales.py` / `metadata.py` | Domain identity |
| `business_modules/sales.md` | Module boundary |
| `apps/quotation/quote_pages.py` | Duplicate convert (no lifecycle link) |
| `v15/business_lifecycle/workflow.py` | `link_sales_order_from_quote` |
| `apps/finance/services.py` | Receipt → payment_status |
| `templates/so_approve.html` / `sales_order_detail.html` | Approve + status UX |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | Ops honesty |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | V18 Type A intent |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Chain extraction |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.  
**Cross-pack:** [../crm/quotation.md](../crm/quotation.md) for Quote Approve / `已确认` inconsistency.
