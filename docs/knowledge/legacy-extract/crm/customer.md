# 客户（Customer）— Legacy Knowledge

**Evidence strength:** Strong  
**Domain identity:** slug `customer`, primary table `customers`, extraction volume `007`  
**Chain role:** Upstream master of the sales/revenue chain  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Authoritative runtime behavior lives in the extracted Customer page service/repository (moved from monolith, move-only). Scaffold API DTOs are thinner and must not be treated as the full field model.

Two parallel “status” worlds appear in Legacy:

- Form/dashboard Chinese lifecycle labels (`开发中`, `跟进中`, `已成交`, `长期客户`, plus rarer `已报价` / `暂停跟进` / `失效客户`)
- Utility / mining paths using English `Active` / `Inactive` (sometimes against a non-`customer_status` column)

EAOS rewrite must decide a single vocabulary; do not inherit the dual set blindly.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| C-R1 | Non-Admin/Manager users may list only customers they own (`owner` = session username) | Customer list query | Admin, Manager see all | Map to tenant + ownership / territory policy, not session-role string lists |
| C-R2 | New customer default status is `开发中` | Create form defaults | User may override on form | Treat as pipeline stage, not boolean active flag |
| C-R3 | Customer number style `CU` + timestamp (`YYYYMMDDHHMMSS`) exists as a utility generator | When generator is called | Page insert path uses form `customer_code` as provided | Decide: system-assigned vs user-entered code; avoid dual generators |
| C-R4 | Detail/list AR balance = sum(SO total) − sum(receipts) | Customer detail / list stats | Missing SO/receipt rows → 0 | Pure derived metric; **not** the Finance `ar_records` open-balance model |
| C-R5 | V18 health heuristic: balance > 100000 → Credit Watch (risk); > 10000 → Needs Follow-up (watch); else Healthy | Detail first viewport | Heuristic only | Replace with policy-driven credit rules + events |
| C-R6 | Credit-tab heuristics (separate): AR alert high >100k / moderate >30k; credit band from **total sales** A>100k / B>30k / C>5k / else D; collection = clear / partial / unpaid | Detail credit tab template | Different thresholds than C-R5 | Do not migrate three competing threshold sets as-is |
| C-R7 | Level presentation: A / VIP / GOLD → 5 stars; B / SILVER → 4; else 3 | Detail first viewport | Form options are A–D | Normalize customer_level enum |
| C-R8 | Win-rate display ≈ SO count / quote count | Detail “what” summary | Quote count 0 → 0% | Presentation only; not a closed-won CRM metric |
| C-R9 | Delete customer hard-cascades: followups → receipts → sales_orders → quotes → customer | Delete action | Does **not** clear delivery_orders, samples, ar_records, business_opportunities/requirements | EAOS must forbid hard cascade by default; use lifecycle + retention |
| C-R10 | Customer360 aggregates: customer + followups + quotes + sales_orders + receipts + samples | Detail / history helpers | Optional Object360 / AI attachments may fail silently | Keep 360 as a composition view over domain services |
| C-R11 | Tenant filter applied on several customer utility / history queries | When tenant scope helpers wrap SQL | Page list/detail repository path may omit tenant filter | Multi-tenant isolation is mandatory in EAOS rewrite |
| C-R12 | Add customer writes audit log category Customer / Add when logger present | Successful create | Update/delete page path may omit audit | Prefer domain event + audit ledger |
| C-R13 | Detail suggests ≤3 next actions: Approve Draft quote, AR Reminder (if balance > 0), New Quote, Statement | Detail first viewport | Draft quote optional | UI policy, not core domain invariant |
| C-R14 | Follow-up append: date + content + next_plan under customer; newest first | Follow-up POST | No permission gate observed on follow-up POST | Gate follow-up as a first-class write |
| C-R15 | Keyword search over code, company, contact, phone, WhatsApp | List | — | Keep as search projection, not domain identity |

---

## 3. 流程

### 3.1 Master data lifecycle (conceptual)

1. **Create** — capture code, company, geo, contact, type/level/status, source, owner, remark  
2. **List / search** — keyword + ownership filter; per-row AR balance  
3. **Detail 360** — financials, quotes, SOs, receipts, deliveries, followups; optional enterprise enrichers  
4. **Update** — same field set as create  
5. **Follow-up** — append dated note + next plan  
6. **Dashboard** — totals by level/status + top by sales + recent  
7. **Delete** — hard cascade (Legacy behavior; do not copy as product default)

### 3.2 Downstream / adjacent flows

- Customer → New Quote (deep link with `customer_id`)
- Customer → Approve first Draft quote (if any)
- Customer → AR reminder / statement surfaces (finance-adjacent)
- Customer → Opportunity mining page (weak / stub; see opportunity pack)
- Optional enrichment: business lifecycle, Object360, AI/automation participants

### 3.3 Permissioned page surface (Legacy HTTP concepts)

| Action | Permission concept observed |
|--------|-----------------------------|
| List / dashboard | `Customers.view` |
| Create | `Customers.add` |
| Edit | `Customers.edit` |
| Delete | `Customers.delete` |
| Detail GET | Not consistently gated |
| Follow-up add | Not consistently gated |

Module aliases: permission module `Customers` (also `Customer`). Super Admin / Admin may bypass checker.

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| C-V1 | `validate_customer` requires a name field keyed as `customer_name` | Weak / inconsistent | Form model persists `company_name`; validator often **not wired** to page POST |
| C-V2 | Form strips whitespace on persist fields | Soft | No format checks for email/phone/WhatsApp observed in page service |
| C-V3 | RBAC module names `Customers` / `Customer`; app slug `customer` | Medium | Workspace bridge historically mismatched `crm` vs `customer` |
| C-V4 | Detail returns not-found when customer missing | Hard | Redirect/message via service |
| C-V5 | Delete has no open-AR / linked-document guard | Absent | Cascades regardless of outstanding balance |

**Not observed as hard server rules on create/update:** unique company name, unique `customer_code`, mandatory owner, mandatory country, email format, duplicate detection.

---

## 5. 数据含义

### 5.1 Entities

| Entity | Meaning | Primary store (Legacy) |
|--------|---------|------------------------|
| Customer | Commercial account / company master | `customers` |
| Follow-up | Interaction / next-plan note | `followups` |
| Customer360 | Read model composing customer + commercial history | Assembled, not a table |
| Balance | Outstanding AR proxy (SO − receipts) | Derived — distinct from Finance `ar_records` |

### 5.2 Key fields (semantics)

| Field | Meaning |
|-------|---------|
| `customer_code` | Business code (often user-entered; CU-timestamp generator exists separately) |
| `company_name` | Display / legal trade name (primary human identifier in UI) |
| `country`, `city` | Geography |
| `contact_person`, `phone`, `whatsapp`, `email` | Primary contact channels |
| `customer_type` | Segmentation; form options include 经销商 / 工厂 / 贸易商 / OEM / 终端客户 / 代理商 |
| `customer_level` | Value tier; form A–D; heuristics also recognize VIP/GOLD/SILVER |
| `customer_status` | Pipeline / relationship stage (Chinese primary vocabulary) |
| `source` | Lead / acquisition source |
| `owner` | Sales owner used for list visibility |
| `remark` | Free-text notes |

Schema-evolution columns may exist in DB (`credit_level`, `credit_limit`, `payment_days`, `tenant_id`, legacy `customer_name`) without full page-CRUD coverage.

### 5.3 Follow-up fields

| Field | Meaning |
|-------|---------|
| `followup_date` | When the follow-up occurred / was recorded |
| `content` | What was discussed |
| `next_plan` | Next action plan |

### 5.4 Dashboard status buckets (observed)

| Bucket | Status values counted |
|--------|------------------------|
| Following | `跟进中`, `开发中` |
| Active (dashboard) | `已成交`, `长期客户` |
| Level A | `customer_level = 'A'` |
| Form / locale extras | `已报价`, `暂停跟进`, `失效客户` |
| Stats / mining English | `Active` / `Inactive` (utility or mining paths; may diverge from `customer_status`) |

### 5.5 Object360 mapping notes

Legacy row → enterprise object conceptually maps: `id` → customer reference; `customer_code` → object code; `company_name` → object name; type/level/status → metadata. This is adapter intent, not a second database. Enterprise Customer360 integration may be deferred to Legacy renderer.

### 5.6 Known Legacy honesty gaps (for rewrite)

- Template positional row indices vs ALTER-added columns can drift.  
- Page repository vs tenant-aware utils/history diverge on isolation.  
- Opportunity mining VIP/dormant/opportunity counts may be hard-zero stubs.

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `business_modules/crm.md` | Module purpose, owned routes/tables, dependencies, workspace slug risk |
| `CRM_MODULE_STATUS.md` | Migration/readiness context |
| `apps/customer/services.py` | Ownership rule, form defaults, 360 KPIs, health heuristic, actions, audit |
| `apps/customer/repository.py` | Persist fields, cascade delete, dashboard/opportunity SQL |
| `apps/customer/validator.py` | Name-required validation helper (wiring gap) |
| `apps/customer/utils.py` | CU number generator, related-entity loaders, Active/Inactive stats |
| `apps/customer/history.py` | Customer360 assembly |
| `apps/customer/router.py` / `routes.py` | Page/API surface & permission gaps |
| `apps/customer/workspace.py` | Workspace slug bridge (`crm` vs `customer`) |
| `core/customer/customer.py` / `metadata.py` | Domain identity & owned tables |
| `core/permission/checker.py` | `Customers`/`Customer` aliases; Admin bypass |
| `core/object360/customer/runtime.py` | Runtime 360 enrich / AI advice heuristics |
| `templates/customer_detail.html` | Credit-tab thresholds; field presentation |
| `templates/edit_customer.html` | Type/level/status option vocabulary |
| `templates/includes/v18/customer360_first.html` | First-viewport actions surface |
| `docs/customer/Customer360_Object_Model.md` | Field → 360 semantics |
| `docs/reports/V151E_Volume007_Customer_Business_Chain_Extraction_Report.md` | Extraction scope & permissions table |
| `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` | Honesty gates for list/detail ops |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.  
**Also referenced as:** `EZAM_CRM-9.0` (same asset family; verified live root uses space + hyphen form).
