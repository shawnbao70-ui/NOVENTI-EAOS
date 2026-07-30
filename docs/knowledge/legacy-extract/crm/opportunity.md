# 商机（Opportunity）— Legacy Knowledge

**Evidence strength:** Medium (split brain)  
**Canonical business entity:** `business_opportunities` via Business Lifecycle  
**Secondary / stub surfaces:** Customer “opportunity mining”; Enterprise Opportunity Engine (AI demo categories)  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Legacy does **not** put Opportunity inside `apps/customer/` as a first-class CRUD package. The real operational center is:

- Routes under `/business/opportunities*`
- Table `business_opportunities`
- Constants in the requirement-driven enterprise lifecycle

Separately, “opportunity” also appears as:

1. **Customer opportunity mining** — lists recent customers with placeholder scores / `Review` actions; VIP/dormant/opportunity counts may be hard-zero stubs  
2. **Enterprise Opportunity Engine** — generates fixed-category insight cards (growth, cross-sell, inventory, price, market, supplier); not persisted CRM opportunities  

EAOS rewrite should treat (A) persisted sales opportunities and (B) AI opportunity insights as **different capability types**.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| O-R1 | Opportunity sits after Customer and before Requirement in the declared lifecycle chain | Lifecycle navigation / constants | Stages after Requirement continue to sample/quote/order; **Contract is not a stage** | Keep chain as capability graph, not hard-coded page order |
| O-R2 | Creating an opportunity requires a title at the HTTP form layer | POST create form | Repository falls back to “Untitled Opportunity” if title empty | Decide whether customer is mandatory for “sales opportunity” |
| O-R3 | Default `source_type` is `sales_opportunity` if omitted | Create | UI offers full source enum | Source taxonomy is product vocabulary — normalize in EAOS |
| O-R4 | Default status on create is `open` | Create when status omitted | Architecture docs mention `open → qualified → converted → closed`, but **no update/status API** observed | Do not ship the doc-only state machine as “Legacy implemented” |
| O-R5 | Default priority is `normal` | Create | No UI priority editor observed on center form | Model priority explicitly if needed |
| O-R6 | Opportunity code auto-built as `OPP-` + `YYYYMMDD` + sequential `-NNNN` when not supplied | Create | Custom code allowed if provided | System-assigned codes preferred |
| O-R7 | Creating a requirement from an opportunity increments `requirement_count` and links `opportunity_id` | Requirement create with opportunity | — | Maintain bidirectional consistency via events |
| O-R8 | Opportunity center / detail require `Customers.view`; create requires `Customers.add` | HTTP handlers | Requirement center uses `Quotes.view` instead | Permission model is inconsistent across lifecycle — redesign |
| O-R9 | Opportunity detail is the hub to create linked requirements (inherits customer_id) | Detail quick-create | — | Opportunity → Requirement is the primary child flow |
| O-R10 | Quotes may carry `opportunity_id` propagated from requirement or sample linkage | Quote/sample workflow hooks | Silent fail if tables/columns missing | Traceability is best-effort in Legacy |
| O-R11 | Customer mining “opportunities” are not rows in `business_opportunities` | Mining page | Stub zeros / placeholder Review; nav integrity reports map this route toward `/business/opportunities` | Do not migrate stubs as real pipeline data |
| O-R15 | Enum `ai_opportunity` exists, but AI Opportunity Engine does **not** auto-insert into `business_opportunities` | Intelligence scan / CRM create | Insight cards stay ephemeral | Keep insight → CRM conversion as an explicit EAOS product decision |
| O-R16 | Manual quote create may omit opportunity/requirement traceability that lifecycle workflow would set | Quote create outside workflow hooks | Silent / missing columns | Prefer mandatory traceability events when rewriting |
| O-R12 | AI Opportunity Engine categories are analytical recommendations, not pipeline stages | AI decision / scan APIs | Demo narrative text, not DB-backed | Separate insight package from CRM Opportunity aggregate |
| O-R13 | Salesperson on create = current session user | Create | No later reassignment UI observed | Ownership model needs explicit rewrite |
| O-R14 | If `business_opportunities` table missing, list degrades to empty | Center load | Schema ensure may run when conn present | Treat schema as capability prerequisite |

---

## 3. 流程

### 3.1 Declared enterprise lifecycle (relevant head)

`Customer → Business Opportunity → Requirement → Analysis → AI Product Matching → Recommendation → Sample → Feedback → Quotation → Sales Order → …`  
(Contract **omitted** from this chain.)

### 3.2 Operational opportunity flow (observed)

1. Open Business Opportunity Center (`/business/opportunities`)  
2. Quick-create: title (required), optional customer id, source type, description  
3. System assigns `OPP-YYYYMMDD-NNNN` style code, status `open`, salesperson = current user  
4. Open detail → review overview + linked requirements  
5. Create requirement from opportunity (title required; type + description)  
6. Downstream (outside this file’s full scope): match products → sample → quote → order, with link propagation

### 3.3 Parallel “mining / AI” flows (non-pipeline)

- Customer mining page: recent customers labeled for review  
- Opportunity engine scan: emit categorized insight cards with action URLs

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| O-V1 | Title required on opportunity create | Hard (form) | Server Form(...) required |
| O-V2 | Customer id ≥ 0 numeric; 0 means unlinked | Soft | Allowed empty customer |
| O-V3 | Source type constrained to `OPPORTUNITY_SOURCE_TYPES` in UI select | Soft | Server accepts posted string |
| O-V4 | Customers.view / Customers.add gates on opportunity pages | Hard (when permission checker active) | 403 / denied response |
| O-V5 | Detail redirects to center if opportunity missing | Hard | — |
| O-V6 | Table existence guard: if `business_opportunities` missing, list is empty | Soft degrade | Schema may be optional in some installs |

**Not observed:** amount/probability fields, close-won reason, mandatory salesperson validation, status transition API on opportunity itself.

---

## 5. 数据含义

### 5.1 Entities

| Entity | Meaning | Store |
|--------|---------|-------|
| Business Opportunity | Sales pursuit / demand umbrella under a customer | `business_opportunities` |
| Requirement | Concrete customer need under an opportunity | `business_requirements` |
| Requirement–Product Match | Matching alternatives for a requirement | `requirement_product_matches` |
| Requirement Link | Trace to quote / SO / etc. | `requirement_links` |
| EnterpriseOpportunity (AI) | Ephemeral insight card | In-memory / API response |

### 5.2 Opportunity fields (semantics)

| Field | Meaning |
|-------|---------|
| `opportunity_code` | Human-readable id (`OPP-YYYYMMDD-NNNN`) |
| `customer_id` | Optional owning customer |
| `title` | Short name of the pursuit |
| `description` | Narrative |
| `source_type` | How the opportunity originated (see enum) |
| `category` | Classification (stored; create path may leave default/empty) |
| `status` | Lifecycle state; create default `open` (doc-only further states not coded) |
| `salesperson` | Owner username at create |
| `priority` | Urgency; default `normal` |
| `requirement_count` | Cached child count |
| `created_at` / `updated_at` | Audit timestamps |

### 5.3 Opportunity source types (enum)

`customer_opportunity`, `sales_opportunity`, `ai_opportunity`, `website_inquiry`, `exhibition_lead`, `referral`, `existing_customer_expansion`

### 5.4 Adjacent requirement vocabulary (child of opportunity)

- **Source types:** customer_sample, customer_description, customer_email, whatsapp, wechat, phone_call, meeting, website_inquiry, exhibition, sales_visit, ai_recommendation, sales_recommendation, manual_entry  
- **Types:** physical_sample, photo, drawing, specification, replacement_part, equivalent_product, technical_consultation, machine_upgrade, maintenance_request, general_product_inquiry  
- **Statuses:** new → analyzing → matched → sample_pending → sample_sent → feedback_received → quoted → ordered → closed / cancelled  

### 5.5 AI opportunity categories (insight-only)

`high_growth_customer`, `cross_selling`, `inventory_optimization`, `price_adjustment`, `market_expansion`, `new_supplier`

### 5.6 Relationship to quote/order

- Requirement may hold `quote_id` / `sales_order_id` as downstream pointers  
- Quote/SO may hold `opportunity_id` / `requirement_id` for traceability  
- Status vocabulary for requirements is richer; opportunity status machine is thinner in UI

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `v15/business_lifecycle/constants.py` | Lifecycle stages, opportunity source types, requirement enums |
| `v15/business_lifecycle/repository.py` | Create/list/get opportunity & requirement rules; code format; count increment |
| `v15/business_lifecycle/routes.py` | HTTP flows & permission gates |
| `v15/business_lifecycle/workflow.py` | Quote/SO/sample link propagation including opportunity_id |
| `templates/business/opportunity_center.html` | Create UX & Open KPI |
| `templates/business/opportunity_detail.html` | Requirement-from-opportunity UX |
| `apps/customer/services.py` | Mining context builder |
| `apps/customer/repository.py` | Mining stub queries |
| `v15/enterprise_intelligence/opportunity_engine.py` | AI insight categories |
| `v15/enterprise_intelligence/platform.py` | Engine scan wiring |
| `business_modules/crm.md` | Mentions opportunity intelligence under CRM purpose |
| `core/ui/role_workspace/menu_registry.py` | Lifecycle opportunity menu key |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
