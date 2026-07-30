# 展示编号与事务权威（Display vs Authority）— Legacy Knowledge

**Evidence strength:** Strong for route/FK/search/print consumers; strong negative for a shared authoritative numbering service  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页区分业务编号的展示/搜索作用与事务关联权威。主链详情、转换、行项和 lifecycle 多用自增 ID/FK；编号用于列表、打印和人工识别。但部分弱关联（TC `source_no`、AR `source_no`、Inventory ledger remark）只保存业务号文本，使碰撞从显示风险升级为追溯歧义。

## 2. Authority Matrix

| Entity | Display/business number | Transaction authority | Cross-module use |
|--------|-------------------------|-----------------------|------------------|
| Opportunity | opportunity_code | opportunity.id | requirement.opportunity_id |
| Requirement | requirement_code | requirement.id | Quote/Sample/SO requirement_id |
| Quote | quote_no | quotes.id | sales_orders.quote_id |
| SO | so_no | sales_orders.id | DO/Receipt use so_id |
| DO | do_no | delivery_orders.id | AR source_no uses text; inventory ledger remark uses text |
| Sample | sample_no | samples.id | Quote sample_id |
| TC | source_no=so_no | tc_ledger.id; no SO FK | weak text linkage |
| AR | source_no=do_no | ar_records.id; no DO FK | weak text linkage |
| NDE document | document_number | source entity ID/context | often display-derived only |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| DVA-R1 | Detail routes generally use numeric IDs | duplicate number does not merge rows |
| DVA-R2 | Quote→SO FK uses quote_id | quote_no not conversion key |
| DVA-R3 | SO→DO/Receipt uses so_id | so_no primarily display |
| DVA-R4 | Sample→Quote uses sample_id | sample_no not FK |
| DVA-R5 | Requirement/Opportunity links use IDs | codes label 360 views |
| DVA-R6 | Lists/search commonly match business-number text | duplicates yield ambiguous results |
| DVA-R7 | NDE Quote prints persisted quote_no | print inherits collisions |
| DVA-R8 | Other document types may derive number from source number/ID | display artifact not new master row |
| DVA-R9 | SO number enters TC `source_no` as text | collision weakens commission trace |
| DVA-R10 | DO number enters `ar_records.source_no` as text | duplicate DO number weakens AR trace |
| DVA-R11 | DO number enters inventory ledger remark `DO-{do_no}` | used by Ship duplicate guard |
| DVA-R12 | number collision can cause false-positive Ship guard across distinct DOs | text becomes behavioral weak key |
| DVA-R13 | OPP/REQ codes are DB unique but FKs still use numeric IDs | code is stable label, not relationship key |
| DVA-R14 | Quote/SO/DO/Sample codes lack DB authority | cannot safely use for external upsert |
| DVA-R15 | 每模块 prefix 只表达类型 | 不共享 counter |
| DVA-R16 | OPP/REQ、Quote、SO、DO、Sample 各自取号 | 无 global ordering |
| DVA-R17 | 同实体也可能多 generator | Quote/DO formats drift |
| DVA-R18 | i18n 不改变 persisted number | prefix 通常硬编码 |
| DVA-R19 | padding 是展示最小宽度 | ID 超四位后会扩展 |
| DVA-R20 | 状态变化不改号 | 编号不代表当前阶段 |
| DVA-R21 | technical ID 唯一不能修复业务号碰撞 | external/manual ambiguity remains |
| DVA-R22 | EAOS 必须区分 `entity_id`、`business_number`、`document_number` | 三者不得互换 |

## 4. Process

1. Create path 生成并持久化 business number。
2. 列表/search/print 展示该文本。
3. 详情 route 使用 numeric ID。
4. 转换链将 numeric FK 写入下游。
5. 个别 ledger/AR/TC 只保存 source number 文本。
6. NDE 可能读取 persisted number，或临时派生新 document number。

## 5. Shared Sequence Assessment

| Question | Finding |
|----------|---------|
| Shared sequence table? | 未观察到 |
| Shared generator service? | 有散落 helpers，无业务主链统一服务 |
| Common timezone? | 否：UTC lifecycle 与本地 datetime 并存 |
| Common format? | 否 |
| Cross-entity uniqueness? | 无 |
| Tenant-scoped sequence? | 未观察到 |
| Number reservation/status? | 未观察到 |
| External immutable ID? | BOOK/global identity 意图未接主写入 |

## 6. Validation

| ID | Validation | Strength |
|----|------------|----------|
| DVA-V1 | FK 必须使用 numeric ID | Mostly implemented |
| DVA-V2 | OPP/REQ code unique | DB Hard |
| DVA-V3 | weak text source_no 必须唯一解析 | Missing |
| DVA-V4 | business number 与 entity ID 必须同时导出 | Missing/unified contract |
| DVA-V5 | derived document number 不得冒充 persisted entity | Semantic only |
| DVA-V6 | external upsert 必须使用 authoritative key | UNKNOWN |
| DVA-V7 | prefix/parser 支持多格式 | Missing |
| DVA-V8 | cross-module source references 应保存 FK | Missing for TC/AR/ledger |
| DVA-V9 | number changes must cascade | Not modeled; numbers not normally edited |
| DVA-V10 | tenant must be part of authority | Missing/unknown |
| DVA-V11 | duplicate business number must block print/export | Missing |
| DVA-V12 | display-derived number must be marked non-persisted | Missing |

## 7. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| entity ID | DB technical authority |
| business number | human-readable identifier |
| document number | printed/display context value |
| foreign key | transaction relationship |
| source_no | weak text reference |
| quote_no | display/search/print Quote code |
| so_no | display SO code and TC weak source |
| do_no | display DO code, AR/ledger weak source |
| sample_no | display Sample code |
| opportunity_code | unique display code |
| requirement_code | unique display code |
| `sales_orders.quote_id` | authoritative Quote→SO link |
| `delivery_orders.so_id` | authoritative SO→DO link |
| `receipts.so_id` | authoritative SO→Receipt link |
| `quotes.sample_id` | Sample trace FK |
| lifecycle IDs | requirement/opportunity trace FKs |
| NDE `document_number` | rendering field |
| prefix | type hint |
| padding | formatting rule |
| shared sequence | absent |

## 8. State Vocabulary

| Term | Meaning |
|------|---------|
| authoritative | controls relationship/uniqueness |
| display | human-facing label |
| persisted number | stored on business row |
| derived number | built during rendering |
| weak source reference | text with no FK |
| shared sequence | no observed implementation |

## 9. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| external integrations use ID or number | open platform/integrations/docs |
| Number columns can be edited after create | services/routes/templates |
| TC/AR text sources ever reconciled to IDs | sales/finance/reports |
| tenant-aware business key contract | tenant schema/scoped queries |
| global identity BOOK22 runtime linkage | core/identity/business inserts |
| print-derived numbers persisted in document records | document/print center/knowledge docs |
| user search disambiguates duplicate numbers | templates/repositories |
| APIs expose both IDs and numbers consistently | app schemas/routes/open API |
| prefixes are locale/brand configurable | config/i18n/brand/templates |

## 10. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/quotation/repository.py` | quote_no search and ID access |
| `apps/quotation/services.py` | print document_number |
| `apps/sales/repository.py` | quote_id/SO id relationships |
| `apps/sales/services.py` | source-ID conversion |
| `apps/inventory/repository.py` | SO/DO IDs and ledger remark query |
| `apps/finance/repository.py` | Receipt so_id、AR source_no |
| `apps/sample/services.py` | Sample ID/number |
| `v15/business_lifecycle/repository.py` | lifecycle IDs/codes |
| `v15/business_lifecycle/workflow.py` | ID-based trace links |
| `runtime/v14/legacy_support.py` | schemas |
| `document/nde_engine.py` | document_number rendering |
| `apps/print_center/v14_residual.py` | source ID print routing |
| `templates/quotes.html` | number display/search |
| `templates/sales_orders.html` | SO number display |
| `templates/delivery_orders.html` | DO number display |
| `business_modules/quotation.md` | module authority |
| `business_modules/sales.md` | order authority |
| `docs/constitution/volume-02-eaos/BOOK22.md` | global ID intent, not runtime proof |
| `docs/knowledge/legacy-extract/document-ops/numbering.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
