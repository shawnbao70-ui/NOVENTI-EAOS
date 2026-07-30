# 报价（Quotation / Quote）— Legacy Knowledge

**Evidence strength:** Strong  
**Domain identity:** slug `quotation`, primary table `quotes` (not `quotations`), extraction volume `009`  
**Chain role:** Pricing gate between CRM / lifecycle and Sales orders  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Authoritative behavior is in `apps/quotation` page services + repository, with Sales owning `convert_so`. Boundary docs sometimes say table `quotations` / routes `/quotations`; runtime domain identity and SQL use **`quotes`** and hubs like `/quotes`. Prefer runtime evidence for rewrite.

Related supporting stores: line items, templates, terms, versions, approval rows, print history.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| Q-R1 | Non-Admin/Manager users see only quotes whose salesperson matches their username via `salespersons` | Quote list | Admin/Manager see all | Ownership via salesperson identity, not customer.owner |
| Q-R2 | Non-Admin/Manager customer pickers limited to customers they own; Admin/Manager see all customers | Quote create context | — | Align customer visibility with Customer pack rules |
| Q-R3 | New quote starts as `Draft` with total `0` | Create / copy / sample→quote / voice guide | — | Draft is the only approve-eligible status |
| Q-R4 | Quote number `QT` + timestamp | Create / copy generators | Convert SO uses different SO numbering | Keep separate document number series |
| Q-R5 | Header commercial defaults (currency, FX, validity days, payment term, delivery time, remark) resolved from master defaults / customer | Create | Copy inherits source commercial header when present | Zero-retype commercial header is a product principle |
| Q-R6 | Optional link to business requirement on create propagates `requirement_id` / `opportunity_id` | `requirement_id > 0` | Silent fail if lifecycle unavailable | Traceability event preferred over silent try/except |
| Q-R7 | Line price = cost / (1 − profit_rate/100); amount = qty × price; totals & gross profit recomputed from lines | Add/delete item; detail view | If posted cost ≤ 0, use product cost | Pricing formula is core commercial rule |
| Q-R8 | Detail shows customer historical price stats (last/low/high/average) for guidance | Detail | Empty history → zeros | Advisory only — not auto-price |
| Q-R9 | Manual status set allowed only in `{Draft, Sent, Negotiating, Won, Lost}` | Status update route | Invalid status → list redirect, no change | Canonical English pipeline — but see Q-R12 |
| Q-R10 | V18 Approve: Draft + has lines + human confirm (`human_confirm=1`) → status `Sent`; Save Draft does not advance; Cancel does not commit approve | Approve POST | Non-Draft blocked; qty≤0 / price&lt;0 blocked | Human Approved is mandatory provenance |
| Q-R11 | Convert to Sales Order is a **separate** confirm-gated action from Approve | Convert path | If SO already exists for quote → list redirect without duplicate | Do not merge Approve and Convert |
| Q-R12 | On successful convert, quote status becomes Chinese `已确认` (not `Won`) | `convert_so` success | Conflicts with English status vocabulary in Q-R9 | **Critical inconsistency** — EAOS must normalize (e.g. Won/Confirmed) deliberately |
| Q-R13 | Convert copies quote lines into SO; SO number style `SO` + zero-padded quote id (`SOxxxx`); sets pending delivery / uncollected labels | Convert | Commission recording best-effort | Sales owns order creation; Quotation initiates |
| Q-R14 | Role gates for quote UI helpers: view ∈ {Admin, Manager, Sales, Engineer}; manage ∈ {Admin, Manager, Sales}; delete = Admin only | Session role checks | Parallel RBAC module `Quotations` / slug `quotation` also exists | Unify identity roles vs module scopes |
| Q-R15 | Quote templates selectable by type/language/currency with `Active` + prefer `is_default` | AI/template helpers | — | Template is reusable header/content pattern |
| Q-R16 | Approval helper can insert `quote_approval` row as `Pending` | Approval create utility | Separate from V18 Type A Sent transition | Two approval concepts coexist — clarify in EAOS |
| Q-R17 | Print writes `quote_print_history` | Print/PDF | Tenant column fallback | Audit trail for documents |
| Q-R18 | Sample → quote creates Draft and may copy sample traceability | Sample conversion routes | — | Production/sample pack adjacency |
| Q-R19 | AI must not silently mutate prices/qty; summary must display recommendations | V18 / Business Strong honesty gates | Empty AI panels allowed | Policy for AI participant redesign |
| Q-R20 | Workspace slug intended as `quote` (boundary docs warn apps bridge wrongly used `sales`) | Workspace registry | — | Naming hygiene for EAOS package ids |
| Q-R21 | Approve surface risk heuristic: no lines → High; stock &lt; qty on any line → Medium; else Low | Approve page context | Advisory analytics only | Do not treat as credit/risk engine |
| Q-R22 | After convert, lifecycle hook may link SO ↔ quote / opportunity (best-effort try/except) | convert_so success | Silent fail if workflow unavailable | Prefer explicit domain events |

---

## 3. 流程

### 3.1 Happy path (modern V18 intent)

1. **Create Draft** (manual / voice guide / sample / copy)  
2. **Add lines** (product, qty, cost, profit rate → computed price)  
3. **Optional** edit commercial header fields  
4. **Approve surface** — review summary, margin, stock notes; optional line qty/price patches; human confirm  
5. Status → **Sent**  
6. Negotiation may move among `Sent` / `Negotiating` via status tools  
7. **Convert to SO** (separate human confirm) → SO created; quote → `已确认`  
8. Downstream delivery / AR owned by other modules

### 3.2 Alternate / support flows

- Quote Center / templates CRUD & search  
- Print / PDF (NDE / document template deps)  
- Quotation AI engine page (assistant surface)  
- Price history advisory on detail  
- Dashboard KPIs: won / negotiating / lost / open(draft|sent) counts & won value

### 3.3 Lifecycle position

Lifecycle constants place Quotation after sample/feedback and before Sales Order. Opportunity/Requirement links are optional traceability, not mandatory for every quote.

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| Q-V1 | Approve only when status is Draft | Hard | Error key for non-draft |
| Q-V2 | Approve requires ≥1 line | Hard | |
| Q-V3 | Human confirm flag must equal `"1"` for Approve | Hard | |
| Q-V4 | Line qty must be positive on approve patches | Hard | Inline + server |
| Q-V5 | Line price must be ≥ 0 on approve patches | Hard | |
| Q-V6 | Status updates whitelist English set | Hard | Does not include `已确认` |
| Q-V7 | Convert refuses duplicate SO for same quote | Hard | |
| Q-V8 | Convert requires quote exists | Hard | Missing → quotes list |
| Q-V9 | Add line requires product exists | Soft/Hard | Missing product → redirect detail no insert |
| Q-V10 | Session role gates for view/manage/delete helpers | Medium | Not the only permission system |
| Q-V11 | Voice guide needs customer, product, qty > 0 to enable approve | Soft UI | |

**Weak / missing vs typical ERP:** no hard check that customer is Active; no expiry auto-void from validity_days; no margin floor approval matrix beyond display; V18 Approve ≠ `quote_approval` Pending workflow.

---

## 5. 数据含义

### 5.1 Entities

| Entity | Meaning | Store |
|--------|---------|-------|
| Quote header | Commercial offer to a customer | `quotes` |
| Quote item | Product line with cost/price/qty/amount | `quote_items` |
| Quote template | Reusable quote pattern | `quote_templates` |
| Quote terms | Standard terms clauses | `quote_terms` |
| Quote version | Version history rows | `quote_versions` |
| Quote approval | Approval request records (`Pending`, …) | `quote_approval` |
| Quote print history | Who printed/exported when | `quote_print_history` |

Domain metadata lists the seven tables above as owned by Quotation.

### 5.2 Header fields (semantics)

| Field | Meaning |
|-------|---------|
| `quote_no` | Document number (`QT…`) |
| `customer_id` | Sold-to customer |
| `salesperson_id` | Owning salesperson (list ACL) |
| `quote_date` | Document date |
| `total_amount` | Sum of line amounts (maintained) |
| `status` | Pipeline state — see status notes |
| `currency`, `exchange_rate` | Money context |
| `validity_days` | Offer validity window (default often 30) |
| `payment_term` | Payment terms text (default e.g. TT 100%) |
| `delivery_time` | Lead time text (default e.g. 7-15 Days) |
| `remark` | Header notes |
| `requirement_id` / `opportunity_id` / `sample_id` | Upstream traceability (when columns present) |
| Gross profit | Derived: total amount − total cost |

### 5.3 Line fields (semantics)

Product snapshot fields (code/name/category/image/material/hardness/stock), `qty`, `cost_price`, `profit` / `profit_rate`, unit `price`, line `amount`.

### 5.4 Status vocabulary (Legacy mix — preserve as knowledge)

| Status | Where used | Meaning |
|--------|------------|---------|
| `Draft` | Create, Approve eligibility | Editable working offer |
| `Sent` | After Human Approve | Issued to customer |
| `Negotiating` | Manual status / KPIs | In commercial discussion |
| `Won` | Manual status / KPIs | Won in English pipeline KPIs |
| `Lost` | Manual status / KPIs | Lost |
| `已确认` | Set by convert_so | Confirmed via order conversion (Chinese) |

Open KPI bucket treats `Draft`, `Sent`, null, empty as open-ish.

### 5.5 Role meanings (quote helpers)

| Capability | Roles |
|------------|-------|
| View | Admin, Manager, Sales, Engineer |
| Manage | Admin, Manager, Sales |
| Delete | Admin |

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `business_modules/quotation.md` | Module purpose, dependencies, workspace slug intent |
| `core/quotation/quotation.py` / `metadata.py` | Domain identity; owned tables; primary `quotes` |
| `apps/quotation/services.py` | Create/copy/pricing/status/approve/voice/sample rules |
| `apps/quotation/repository.py` | Persist, KPIs, status update, convert support queries |
| `apps/quotation/validator.py` | Role gates |
| `apps/quotation/utils.py` | QT numbering, templates/terms/versions, approval/print helpers |
| `apps/quotation/router.py` / `quote_pages.py` / `quote_api.py` | Surface inventory |
| `apps/sales/services.py` | `convert_so` business rules |
| `apps/sales/repository.py` | Quote status → `已确认`; SO insert |
| `v15/business_lifecycle/workflow.py` | Requirement/opportunity linkage |
| `v15/business_lifecycle/constants.py` | Lifecycle placement of quotation |
| `docs/design/v18/QUOTE_APPROVE_ACCEPTANCE_EXAMPLE.md` | Human Approve → Sent intent |
| `docs/reports/V18_Quote_Approve_Gate_Report.md` | Gate evidence |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Extraction scope |
| `docs/reports/Business_Strong_A013_Quote_Ops_Report.md` | Convert confirm / honesty gates |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
