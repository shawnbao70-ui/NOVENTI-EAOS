# Changelog — Project Phoenix

**Repository:** `NOVENTI-EAOS`  
**Product:** NOVENTI Enterprise AI Operating System (EAOS)

---

## Title

Phoenix Changelog

## Purpose

Record significant Phoenix milestones and documentation/platform changes inside `NOVENTI-EAOS` only.

## Scope

Changes in the EAOS repository. Legacy repository mutations are out of scope and forbidden.

## Current Status

Active.

## 条目

### 2026-07-29 — PHX-G525 CRM Return Authorization Read-only UI

- Added Delivery-Order-scoped Return Authorization create and detail read
  Smart Terminal UI (Create gated on shipped DO; Restock/Credit Note excluded).
- No tenant RA list; no Inventory ship UI in this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G525 verification: **69 passed**.
- **FINAL STOP TRACK-G525**; G526–G527 remain closed.

### 2026-07-29 — PHX-G524 CRM AR Invoice Read / Issue UI

- Added Delivery-Order-scoped AR Invoice create, detail read, and Issue
  Smart Terminal UI over existing APIs (no tenant Invoice list).
- Explicit confirmation for create and Issue; Void/RA/Receipt remain outside.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G524 verification: **65 passed**.
- **FINAL STOP TRACK-G524**; G525–G527 remain closed.

### 2026-07-29 — PHX-G523 CRM Delivery Order Read / Release UI

- Added Sales-Order-scoped Delivery Order create, detail read, and Release
  Smart Terminal UI over existing APIs (no tenant DO list).
- Explicit confirmation for create and Release; Invoice/RA remain outside.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G523 verification: **61 passed**.
- **FINAL STOP TRACK-G523**; G524–G527 remain closed.

### 2026-07-29 — PHX-G522 CRM Quote Issue UI

- Added Smart Terminal Issue for `draft` Quotes with explicit confirmation,
  `human_confirm: true`, idempotency, and optional approval_ref.
- Post-issue Quote detail refresh; Convert/Confirm/Delivery/Invoice/RA remain
  outside.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G522 verification: **57 passed**; browser verified Issue
  affordance and fail-closed control projection.
- **FINAL STOP TRACK-G522**; G523–G527 remain closed.

### 2026-07-29 — PHX-G521 CRM Customer 360 read-only UI

- Added Smart Terminal Customer 360 read-only composition over existing `/360`.
- Shows commercial_hold, open-order counts, and non-navigating traces.
- Commercial Hold write, Quote Issue, Delivery, Invoice, and RA remain outside.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G521 verification: **53 passed**; browser verified 360 surface.
- **FINAL STOP TRACK-G521**; G522–G527 remain closed.

### 2026-07-29 — PHX-G520 CRM Sales Order Confirm UI

- Added Smart Terminal Confirm for `created` Sales Orders with explicit
  confirmation, `human_confirm: true`, idempotency, and optional approval_ref.
- Post-confirm detail/line refresh; lines materialize on Confirm.
- Delivery, Invoice, Return Authorization, and Quote Issue remain outside.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G520 verification: **49 passed**; browser verified Confirm
  affordance and fail-closed control projection.
- **FINAL STOP TRACK-G520**; G521–G527 remain closed.

### 2026-07-29 — PHX-G519 CRM Sales Order read-only UI

- Added tenant-scoped Sales Order collection queries with bounded
  `created_at + id` cursor pagination and closed minimal DTOs.
- Added Smart Terminal Sales Order list/detail and line read surfaces.
- Kept Confirm, Delivery, Invoice, and Return Authorization outside the
  milestone; created orders correctly show empty lines until Confirm.
- No Database, Alembic, Kernel, or Runtime Manifest change.
- Focused G512–G519 verification: **45 passed**; browser verified fail-closed
  read-only Sales Order behavior.
- **FINAL STOP TRACK-G519**; G520–G525 remain closed.

### 2026-07-29 — Standing Coding Authorization Approved

- Product Owner issued **Coding Authorization Approved** (effective
  immediately) for all Business Packages with Architecture Gate Accepted.
- Permits CRUD, migrations, API, runtime, front-end, integration, tests, and
  implementation docs inside accepted boundaries.
- Does not waive Gate process for future architecture changes; hard holds and
  one-contiguous-milestone sequencing remain.
- Record: [PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md](PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md).
- Queue advanced to **FINAL STOP TRACK-G519** after PHX-G519 closeout.

### 2026-07-29 — Phoenix Gate Framework Redesign review Approve

- Product Owner completed Framework review: **Approve** (governance process
  only). Confirms Decision Summary as sole PO surface; Approve/Amend/Reject;
  auto-generated Gate artifacts; Gate Accept independent of Coding Auth; one
  workflow for all Business Packages (ADR-0321).
- Recorded in Approval Record / Architecture Gate / Acceptance / Decision
  Summary. **Coding Authorization: None.** No CRUD, migration, API, runtime,
  or frontend authority from this Approve alone.

### 2026-07-29 — PHX-G518 CRM Quote Convert UI

- Added Smart Terminal Convert confirmation for issued Quotes, Conversion
  detail refresh, and Sales Order shell creation from a ready Conversion.
- Reused existing Convert / Conversion / create-SO APIs without backend,
  Repository, Database, Alembic, Kernel, or Runtime Manifest change.
- Preserved idempotent Convert, Permission default-deny, and explicit
  high-impact confirmation.
- Kept Quote Issue, Sales Order Confirm, Delivery, Invoice, and Return
  Authorization outside the milestone.
- Focused G512–G518 verification: **40 passed**; browser verified
  fail-closed Convert controls.
- **FINAL STOP TRACK-G518**; G519–G525 remain closed.

### 2026-07-29 — PHX-G517 CRM Quote Lines managed UI

- Added Quote Line list/detail/create/edit/archive Smart Terminal workflows
  under the selected governed Quote Header.
- Reused existing API contracts without backend, Repository, Database,
  Alembic, Kernel, or Runtime Manifest change.
- UI projects active lines while archived history remains available from the
  existing API for audit.
- Kept Amount server-calculated/read-only and preserved Permission default-deny,
  optimistic concurrency, and explicit archive confirmation.
- Kept Issue, Convert, approvals, and automatic pricing outside the milestone.
- Focused G512–G517 verification: **35 passed**; browser verified fail-closed
  Quote Line behavior.
- **FINAL STOP TRACK-G517**; G518–G521 remain closed.

### 2026-07-29 — PHX-G516 CRM Quote Header managed UI

- Added tenant-scoped, Permission-default-deny Quote Header collection queries
  with bounded opaque-cursor pagination and closed minimal DTOs.
- Added Quote Header list/detail/create/edit/archive workflows with governed
  Requirement association.
- Kept Quote Lines, Issue, Convert, approvals, Database, Alembic, and Runtime
  Manifest outside this milestone.
- Version conflicts never retry or overwrite automatically; archive requires
  reason and confirmation.
- Focused G512–G516 verification: **30 passed**; browser verified fail-closed
  Quote Header behavior.
- **FINAL STOP TRACK-G516**; G517–G521 remain closed.

### 2026-07-29 — PHX-G515 CRM Requirement managed UI

- Added tenant-scoped, Permission-default-deny Requirement collection queries
  with bounded opaque-cursor pagination and closed minimal DTOs.
- Added Requirement list/detail/create/edit/archive workflows with governed
  Opportunity association.
- Version conflicts never retry or overwrite automatically; archive requires
  reason and confirmation.
- In-memory and SQLAlchemy paths require no Database or Alembic change.
- Focused G512–G515 verification: **24 passed**; browser verified fail-closed
  Requirement behavior.
- **FINAL STOP TRACK-G515**; G516–G521 remain closed.

### 2026-07-28 — PHX-G514 CRM Opportunity managed UI

- Added tenant-scoped, Permission-default-deny Opportunity collection queries
  with bounded opaque-cursor pagination and closed minimal DTOs.
- Added Smart Terminal Opportunity list/detail/create/edit/archive workflows
  with governed Customer association.
- Effective grants project write controls; server Permission remains
  authoritative and unavailable projection hides writes.
- Updates and archive use optimistic versions; conflict handling never retries
  or overwrites automatically.
- In-memory and SQLAlchemy paths require no Database or Alembic change.
- Focused G512–G514 verification: **18 passed**; browser verified Opportunity
  fail-closed behavior with CRM runtime unavailable.
- **FINAL STOP TRACK-G514**; G515–G521 remain closed.

### 2026-07-28 — PHX-G513 CRM Customer + Contact managed UI

- Added effective-permission-projected Customer and Contact create, edit, and
  archive controls to Smart Terminal.
- Missing or unavailable grant projection hides every write affordance; server
  Permission remains authoritative.
- Managed updates and archive use optimistic versions; conflict handling stops,
  refreshes, and never retries or overwrites automatically.
- Archive requires a reason and explicit confirmation; Contact PII stays
  optional and collection-minimized.
- No API, Service, Repository, Database, Alembic, or Runtime Manifest change.
- Focused G512/G513 verification: **12 passed**; browser verified fail-closed
  behavior with CRM runtime unavailable.
- **FINAL STOP TRACK-G513**; production remains **NO-GO** pending G469 evidence.

### 2026-07-28 — PHX-G512 CRM Customer + Contact read-only UI

- Added tenant-scoped, Permission-default-deny Customer and Contact collection
  queries with bounded opaque-cursor pagination.
- Contact list DTO excludes email, phone, and tenant identifiers; governed
  detail remains separately permissioned.
- Added Smart Terminal CRM list/detail surface with loading, empty, denied,
  and error states and no write controls.
- In-memory and SQLAlchemy repositories support stable active-only listing
  without Database or Alembic changes.
- Focused CRM/API/UI/persistence verification: **16 passed**; browser verified
  denied and authorized-empty states.
- **FINAL STOP TRACK-G512**; production remains **NO-GO** pending G469 evidence.

### 2026-07-28 — ADR-0321 Phoenix Gate Framework formal standard

- Product Owner approved ADR-0321 as the sole Gate Framework.
- Exact nine-field Decision Summary is the only Gate approval entry;
  Product Owner actions are limited to Approve / Amend / Reject.
- Manual PO maintenance of OD, RC, Approval Table, Signature, Evidence, and
  long-form Gate documents is retired.
- Generator rules and generated Architecture Gate / Acceptance templates now
  require ADR, approved Summary, Evidence, Approval Record, Signature, and
  `Coding Authorization: None`.
- CRM, Inventory, Purchase, Finance, Workflow, Marketplace, and Enterprise
  Brain are registered under the same framework without rewriting historical
  evidence.
- Governance-only change; no CRUD, Database, API, Runtime, Frontend, Business
  Logic, Alembic, or Runtime Manifest authorization.

### 2026-07-28 — PHX-G464…G511 Batches M→T（Foundation 0.2.5）

- **M** production evidence decision closed **NO-GO** without fabricating
  branch-protection, CI Docker history, or PostgreSQL evidence.
- **N** Identity/Auth residual: secrets hidden, PKCE S256, WebAuthn attestation
  crypto false, Role→grant default OFF.
- **O/P** commercial and supply-chain status residuals.
- **Q** Marketplace economy residual with external services fail closed.
- **R** Event/Outbox/Audit residual; on-demand delivery and no multi-region claim.
- **S** Terminal/Plugin residual; no signature bypass or sandbox escape.
- **T** V2.0 readiness refresh; Foundation **0.2.5**;
  **FINAL STOP TRACK-G511**.
- Alembic remains `0092`; all HARD HOLDs remain closed.

### 2026-07-28 — PHX-G464…G469 Batch M production evidence decision

- Branch-protection evidence remains a human repo-admin action; no settings
  mutation or fabricated proof.
- CI defines `docker-smoke`, but run history could not be verified because
  GitHub CLI is unavailable and local Docker was not installed.
- Fresh PostgreSQL `integration_critical` attempt blocked during setup and was
  terminated after no progress.
- `PRODUCTION_GO_DECISION_G469.md` therefore records unconditional production
  **NO-GO**; feature work may continue under the separate M→T serial authority.
- `pr_required`: **96 passed / 1 skipped · 63.3 s**（≤600 s）.

### 2026-07-27 — PHX-G416…G463 Batches E→L（Foundation 0.2.4）

- **E** RC HOLD closeout：PG `integration_critical` green；Docker CI-path；REPAIR FREEZE lifted（G416–G421）
- **F** Integration tip/reset truth + duration publish（G422–G427）
- **G** Finance status deepen；`bank_file_import=deferred`；PSP default off（G428–G433）
- **H** Workflow escalation fail-closed；compensation/SLA invent=false（G434–G439）
- **I** OpenAPI `semantic_remainder_honest`；`full_openapi_http_complete` remains false（G440–G445）
- **J** Knowledge/Twin/Brain advisory；execute/authorize commercial auto-write closed（G446–G451）
- **K** Ops/Tenant/Observability + deploy security regression（G452–G457）
- **L** V2.0 readiness refresh；Foundation **0.2.4**；**FINAL STOP TRACK-G463**
- Alembic tip 仍 `0092`；无 host Docker/PG 安装；无银行文件导入 / 外部 PSP invent

### 2026-07-27 — PHX-G409…G415 Remediation wave close（CONDITIONAL GO）

- **G409** Helm Chart/appVersion/image.tag → `0.2.3`；`test_ops_g409_version_parity.py`
- **G410** `.github/workflows/ci.yml` + `constraints/production.txt` + `CI_AND_LOCK.md`
- **G411** PROJECT_STATUS / ENG tip / DAL current truth → `0.2.3`/`0092`；`RUNTIME_PACKAGE_LAYOUT.md`；manifest inventory honesty
- **G412** `api/gateway/production_auth.py`（`EAOS_ENV=production` fail-closed）；WebAuthn/network truth tests
- **G413** Helm non-root / drop ALL / seccomp；Dockerfile `USER 10001`
- **G414** `integration_critical` shard；PG suite gated on `EAOS_TEST_DATABASE_URL`
- **G415** `RC_EVIDENCE_G415.md` → **CONDITIONAL GO**；`FINAL STOP TRACK-G415`
- Alembic tip 仍 `0092`；无功能里程碑重开；宿主 Docker/PG 安装未做

### 2026-07-27 — PHX-G408 Remediation P0-2 contract shards

- 接受 ADR-0422；`tests/contracts/shards.yaml` + `scripts/run_contract_shard.py`
- Required PR set `pr_required` 墙钟预算 ≤600s；参考机实测 **53.5s / 47 passed**
- `docs/release/CONTRACT_SHARDS.md` 公布分片 ownership；全量 suite 走 nightly/parallel，不得隐藏耗时
- 契约 `test_ops_g408_contract_shards.py`；无 Alembic；包仍 `0.2.3`；下一步 G409 版本表面对齐

### 2026-07-27 — PHX-G407 Remediation P0-3 Docker noventi packaging

- 接受 ADR-0421；`Dockerfile` `COPY noventi ./noventi`；`/smoke_imports.py` 导入
  `api.gateway.app` / `noventi.crm` / `noventi.finance`（+ purchase/inventory）
- COMPOSE.md 标明 packaging ≠ host OS install ≠ Industry/Marketplace host-install invent
- 契约 `test_ops_g407_docker_noventi_packaging.py`；本机无 Docker CLI 时 layout smoke 绿、镜像构建证据暂缓
- Alembic tip 仍 `0092`；包仍 `0.2.3`；下一步 G408 PR shards（另批）

### 2026-07-27 — PHX-G406 Remediation P0-1 tip helper

- 接受 ADR-0420；`tests/contracts/_baseline.py` 为唯一现行 tip/package 真源（Alembic + Manifest）
- 消除 contracts 中 `0049_…` 作为 `get_current_head()` 的断言；历史 revision 改 existence/ancestor
- REPAIR FREEZE 写入 roadmap；G0 PARTIAL；无 Alembic；包仍 `0.2.3`
- 契约 `test_api_gateway_g406_remediation_tip_helper.py`；下一步 G407 Docker noventi（另批）

### 2026-07-27 — PHX-G405 Baseline + V2.0 readiness checklist

- 发布 `docs/release/V2_0_READINESS_CHECKLIST.md`（readiness board only；≠ V2.0 cut）
- Roadmap G400–G405 COMPLETE；`FINAL STOP TRACK-G405`；queue empty await PO for G406+
- Tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；package `0.2.3`；契约 `test_baseline_hygiene_g405.py`
- 外部 PSP / ENABLE_*_NETWORK 默认 OFF；银行文件导入仍暂缓

### 2026-07-27 — PHX-G404 Foundation 0.2.3 Release Cut

- 接受 ADR-0419；包基线 `0.2.2` → **`0.2.3`**（pyproject / SDK / Manifest / ops docs / `GET /v1/release`）
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；本切片无新 migration
- Align OPERATIONS_RUNBOOK / COMPATIBILITY / RELEASE_CHECKLIST / PRODUCTION_TOPOLOGY package version to `0.2.3`
- MASTER_PLAN / POST_CRM_VERTICAL_ROADMAP 现行基线指针 → `0.2.3`；G404 COMPLETE；G405 IN QUEUE
- 无业务 CRUD

### 2026-07-27 — PHX-G403 Workflow multi-step executable deepen

- `WorkflowStatusData.multi_step_executable=true`（窄域 `kernel_task_approve_reject_escalate`）；`legacy_multi_step_implemented=false`
- `workflow.openapi.yaml` → **1.0.11**；契约 `test_api_gateway_g403_workflow_multi_step_executable.py`
- Alembic tip 仍为 `0092`；不发明全量 multi-step runtime

### 2026-07-27 — PHX-G402 Marketplace dispute/arbitration fail-closed shell

- `GET /v1/marketplace/status` 加深 `dispute_arbitration_product`：external arbitration fail-closed；无外部 arbiter invent
- `marketplace.openapi.yaml` → **1.2.17**；契约 `test_api_gateway_g402_marketplace_dispute_arbitration.py`
- ENABLE_*_NETWORK / 外部 PSP 仍默认 OFF

### 2026-07-27 — PHX-G401 Marketplace billing record internal shell

- Marketplace billing-record shell（internal invoice / clearing record only；≠ external PSP）
- `bank_file_import=deferred`；契约 `test_api_gateway_g401_marketplace_billing_record_shell.py`
- Alembic tip 仍为 `0092`

### 2026-07-27 — PHX-G400 Marketplace metering/entitlement shell

- Marketplace metering fail-closed + entitlement declaration-only shells on `/v1/marketplace/status`
- 契约 `test_api_gateway_g400_marketplace_metering_entitlement.py`；无 commercial auto-write / Cap→grant invent
- Alembic tip 仍为 `0092`

### 2026-07-26 — PHX-G380 Commercial domain-event honesty

- 接受 ADR-0406；`SO.confirm` → `crm.sales_order.confirmed`；`DO.ship` → `inventory.delivery_order.shipped`
- TransactionalCRMService / TransactionalInventoryService 同 UoW 注入 DomainEventEmitter；in-memory 可选/no-op
- 目录 `COMMERCIAL_EVENTS.md`；契约 `test_api_gateway_g380_commercial_domain_events.py`
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；无新 migration
- POST_CRM_VERTICAL_ROADMAP：G380 COMPLETE；G381 IN QUEUE

### 2026-07-26 — PHX-G379 AI Workforce thin boundary

- 接受 ADR-0405；`GET /v1/platform/ai-workforce/status` 诚实边界字段：`task_engine=false`、`labor_write=false`、`commercial_auto_write=false`、`execution_authority=none`、`digital_employee_identity_separate=true`
- 与 G374 `digital-employee/status` 身份面分离；无 task CRUD
- `platform.openapi.yaml` → **1.0.13**；契约 `test_api_gateway_g379_ai_workforce_thin.py`
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；不发明域事件面或 Marketplace PSP
- POST_CRM_VERTICAL_ROADMAP：G379 COMPLETE；G380 IN QUEUE

### 2026-07-26 — PHX-G378 Industry Package boundary

- 接受 ADR-0404；`GET /v1/platform/industry-package/status` 诚实边界字段：`industry_package_runtime=false`、`host_install=false`、`declaration_only=true`、`package_type_industry_supported_in_manifest=true`、`execution_authority=none`
- `platform.openapi.yaml` → **1.0.12**；契约 `test_api_gateway_g378_industry_package_boundary.py`
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；不发明 host 安装运行时
- POST_CRM_VERTICAL_ROADMAP：G378 COMPLETE；G379 IN QUEUE

### 2026-07-26 — PHX-G377 Knowledge governance thin

- 接受 ADR-0403；`GET /v1/knowledge/status` 加深治理诚实字段：`graph_write_engine=false`、`constitution_rewrite=never`、`sample_pack_is_not_runtime_graph=true`、`execution_authority=none`
- `knowledge.openapi.yaml` → **1.0.11**；契约 `test_api_gateway_g377_knowledge_governance_thin.py`
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；不发明图谱写引擎
- POST_CRM_VERTICAL_ROADMAP：G377 COMPLETE；G378 IN QUEUE

### 2026-07-26 — PHX-G376 Foundation 0.2.2 Release Cut

- 接受 ADR-0402；包基线 `0.2.1` → **`0.2.2`**（pyproject / SDK / Manifest / ops docs / `GET /v1/release`）
- Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`；本切片无新 migration
- Align OPERATIONS_RUNBOOK / COMPATIBILITY / RELEASE_CHECKLIST / PRODUCTION_TOPOLOGY package version to `0.2.2`
- MASTER_PLAN / POST_CRM_VERTICAL_ROADMAP 现行基线指针 → `0.2.2`；G376 COMPLETE；G377 IN QUEUE
- 无业务 CRUD

### 2026-07-26 — PHX-G373 Release train readiness (residual closeout G370–G372)

- Residual closeout at tip `0092_finance_realized_fx_gl_bridge_g372`：G370 Controlled Reship · G371 Treasury transfer + FX · G372 Realized FX → GL bridge
- Align `RELEASE_MANIFEST.yaml` `alembic_head` + OPERATIONS_RUNBOOK / COMPATIBILITY / RELEASE_CHECKLIST / PRODUCTION_TOPOLOGY tip refs；train candidate at tip 0092
- 包仍 `0.2.1`；无 Alembic；无业务 CRUD

### 2026-07-24 — Foundation deepen (DAL-U235) Knowledge status sample-pack nest

- `GET /v1/knowledge/status` → `KnowledgeStatusEnvelope` + `sample_knowledge_pack_product`；Terminal domain strip；DAL-**U235**

### 2026-07-24 — Foundation deepen (DAL-U231…U234) Sample pack UI + Ops closed + demo serve

- Terminal G293 strip；Ops health/release/adapters/context `response_model` + `gateway_store`；bootstrap pack 指针；demo 只读挂载 `/v1/demo/sample-pack`；DAL-**U231**…**U234**

### 2026-07-24 — Foundation deepen (DAL-U230) Sample pack discoverability

- `/v1/adapters` meta 暴露 `sample_knowledge_pack_product`（G293；≠ CRUD）；ops OpenAPI；T2/T3 intake 标明 pack ≠ Complete；DAL-**U230**

### 2026-07-24 — PHX-G293 Sample Knowledge Pack

- 接受 ADR-0319；`docs/knowledge/sample-pack` 组装 G290–G292 CRM→Delivery 结论（Terminal demo / Research observation）；DAL-**U229**
- 契约：`test_docs_g293_sample_knowledge_pack.py`
- 非目标：不实现业务 CRUD；不打开 Brain/Twin；包仍 `0.2.1`；Alembic 仍 `0029`

### 2026-07-24 — Foundation harden (DAL-U226 / U228) named lists + Brain/Twin fail-closed fence

- Org/Workflow/Permission list 成功响应命名 array schema；Brain execute / Twin authorize 无成功 DTO + 运行时 403 契约；DAL-**U226** / **U228**

### 2026-07-24 — Foundation harden (DAL-U223…U225 / U227) 422 + fail-closed + Org UuidResult + forbid

- 全量 requestBody 补 `422`→`HTTPValidationError`（纠正错误 GatewayDetailError）；Brain/Twin fail-closed 补 401；Org `IdResponse`→`UuidResult`；closed_dto_extra 扩面；DAL-**U223**…**U225** / **U227**

### 2026-07-24 — Foundation harden (DAL-U217…U222) OpenAPI 401 honesty sweep

- Platform IdP / Marketplace / Terminal / Organization / Identity / Permission·Event·Workflow·AI·Knowledge·Package 共约 100 个鉴权 2xx 路径补 `401`+`GatewayDetailError`；公开 OIDC providers 不加 401；契约元测试扫全量；DAL-**U217**…**U222**

### 2026-07-24 — Foundation harden (DAL-U216) Marketplace payment/host-acquire closed + 401

- PaymentClearing/HostAcquire 闭环；OpenAPI 401；external PSP 仍 false；DAL-**U216**

### 2026-07-24 — Foundation harden (DAL-U215) Permission effective-permissions closed + 401

- `EffectivePermission` list；enterprises list + effective-permissions OpenAPI 401；DAL-**U215**

### 2026-07-24 — Foundation harden (DAL-U214) Brain/Twin GET closed + fail-closed preserved

- Insight/snapshot GET 闭环；OpenAPI 401；execute/authorize 仍 fail-closed；DAL-**U214**

### 2026-07-24 — Foundation harden (DAL-U213) Workflow task list closed + 401

- `WorkflowTaskResponse` list；tasks GET OpenAPI 401；DAL-**U213**

### 2026-07-24 — Foundation harden (DAL-U212) Organization GET closed DTOs + 401

- Tenant/Enterprise/Unit/Membership GET 闭环；tenant GET OpenAPI 401；DAL-**U212**

### 2026-07-24 — Foundation harden (DAL-U211) AI run/memory/invoke closed DTOs + 401

- AgentRun/Memory/ToolInvocation 闭环；run GET OpenAPI 401；DAL-**U211**

### 2026-07-24 — Foundation harden (DAL-U210) Knowledge query/get closed envelopes + 401

- entity/list/search/provenance 闭环；entity GET OpenAPI 401；DAL-**U210**

### 2026-07-24 — Foundation harden (DAL-U209) Workflow instance closed DTOs + 401

- start/get/signal/cancel/compensate/approve/reject/escalate 闭环；instances OpenAPI 401
- DAL-**U209**

### 2026-07-24 — Foundation harden (DAL-U208) Identity GET/session closed DTOs + 401

- Subject/credential/session/AI profile 闭环；subject GET OpenAPI 401；DAL-**U208**

### 2026-07-24 — Foundation harden (DAL-U207) Marketplace listing GET closed

- `MarketplaceListingResponse`；listing GET OpenAPI 401；DAL-**U207**

### 2026-07-24 — Foundation harden (DAL-U206) Package manifest GET closed

- `PackageManifestResponse`；manifest GET OpenAPI 401；DAL-**U206**

### 2026-07-24 — Foundation harden (DAL-U205) Terminal GET/commit closed DTOs

- Session/intent/preview/approval GET + commit `*Response`；session GET OpenAPI 401
- DAL-**U205**

### 2026-07-24 — Foundation harden (DAL-U204) Event closed report envelopes + 401

- publish/dispatch/stats/DLQ/get/replay 闭环；publish+dispatch OpenAPI 401
- DAL-**U204**

### 2026-07-23 — Foundation harden (DAL-U203) Permission evaluate/explanation closed DTOs

- `EvaluateResult` / `DecisionExplanation` 闭环；OpenAPI `policy_version` 对齐 runtime string；evaluations 401
- DAL-**U203**

### 2026-07-23 — Foundation harden (DAL-U202) AI/Brain/Twin closed UuidResult + 401

- AI runs/tools/memory/approvals + Brain insights + Twin snapshots `UuidResult`；commits `OkResponse`
- Brain execute / Twin authorize 仍 fail-closed；OpenAPI 401；DAL-**U202**

### 2026-07-23 — Foundation harden (DAL-U201) Organization dual-key + closed mutation wire

- Organization `IdResponse` 对齐双 key；enterprise/unit/membership + platform tenants 闭环
- DAL-**U201**；契约：`g21` / `foundation_harden_marketplace_uuid_closed` / `openapi_401_honesty`

### 2026-07-23 — Foundation harden (DAL-U200) Identity closed UuidResult wire + 401

- Identity subjects/credentials/governors/AI `UuidResult`；subjects OpenAPI 401
- DAL-**U200**；契约：`foundation_harden_marketplace_uuid_closed` / `openapi_401_honesty`

### 2026-07-23 — Foundation harden (DAL-U199) Knowledge closed mutation wire + 401

- Knowledge entities/links `UuidResult`；archive/share `OkResponse`；entities OpenAPI 401
- DAL-**U199**；契约：`foundation_harden_marketplace_uuid_closed` / `openapi_401_honesty`

### 2026-07-23 — Foundation harden (DAL-U198) Event/Workflow closed mutation wire + 401

- Event outbox/subscriptions + Workflow definitions `UuidResult`/`OkResponse`；OpenAPI 401
- DAL-**U198**；契约：`foundation_harden_marketplace_uuid_closed` / `openapi_401_honesty`

### 2026-07-23 — Foundation harden (DAL-U197) Marketplace closed mutation wire + 401

- Marketplace listing lifecycle `UuidResult`/`BooleanResult`；listings/intents/policies OpenAPI 401
- DAL-**U197**；契约：`foundation_harden_marketplace_uuid_closed`

### 2026-07-23 — Foundation harden (DAL-U196) Terminal/Permission mutation closed wire

- Terminal preview/approval/extension + Permission policy/grant 闭环；共享 `OkResponse`
- DAL-**U196**；契约：`foundation_harden_uuid_result_closed`

### 2026-07-23 — Foundation harden (DAL-U195) Domain status auth fail-closed copy

- G194 jwt/oidc/idp 探针失败文案改为 `fail_closed`；DAL-**U195**

### 2026-07-23 — Foundation harden (DAL-U194) UuidResult + OpenAPI 401 honesty

- 共享 `UuidResult` 接到 Package/Terminal 注册响应
- Platform/Terminal/Permission/Package OpenAPI 补齐 401；DAL-**U194**

### 2026-07-23 — Foundation harden (DAL-U193) Package surfaces/resolve + roles UI headers

- Package surfaces/resolve closed response DTO；roles/status 探针改走 `api(auth:true)`
- DAL-**U193**；契约：`g201` / `foundation_harden_package_surfaces_closed`

### 2026-07-23 — Foundation harden (DAL-U192) Terminal extension closed envelopes

- Extension list/invoke closed response DTO；DAL-**U192**
- 契约：`foundation_harden_terminal_extension_closed`

### 2026-07-23 — Foundation harden (DAL-U191) Role→grant mint closed DTO

- `POST /permission/role-grants` closed mint response；OpenAPI 422 honesty
- DAL-**U191**；契约：`foundation_harden_role_grant_mint_closed` / `g161`

### 2026-07-23 — Foundation harden (DAL-U190) Platform IdP federation closed envelopes

- Federation matrix + tenant bindings list/create/unbind/priority closed response DTO
- DAL-**U190**；契约：`foundation_harden_platform_roles_closed`

### 2026-07-23 — Foundation harden (DAL-U189) Platform IdP issuer closed envelopes

- `/platform/idp/issuers` list/create/disable + discovery sync closed response DTO
- DAL-**U189**；契约：`foundation_harden_platform_roles_closed`

### 2026-07-23 — Foundation harden (DAL-U188) Platform roles envelopes + intents/previews 422

- Platform `/platform/roles` list/upsert/disable closed response DTO
- Terminal intents/previews OpenAPI 422 honesty；DAL-**U188**

### 2026-07-23 — Foundation harden (DAL-U187) Permission roles catalog + sessions 422

- `GET /permission/roles` closed flat response DTO；Terminal sessions OpenAPI 422
- DAL-**U187**；契约：`g180` / `foundation_harden_auth_response_closed`

### 2026-07-23 — Foundation harden (DAL-U186) RoleCatalog/WebAuthn response DTOs

- `/permission/roles/status` + WebAuthn options/verify closed response DTO；callback 返回类型收口
- Auth WebAuthn options + Terminal extension register OpenAPI 422 honesty；DAL-**U186**

### 2026-07-23 — Foundation harden (DAL-U185) G194 auth probes + Marketplace status DTO

- Domain Foundation Status 探针补齐 jwt/oidc/idp；Marketplace `/status` closed envelope
- DAL-**U185**；契约：`g194` / `foundation_harden_status_response_closed`

### 2026-07-23 — Foundation harden (DAL-U184) Domain status closed envelopes + resolve 422

- 11 域 `/status` 接入 closed response DTO（含 Brain/Twin fail-closed 字段）
- Package resolve OpenAPI 补齐运行时已有的 422；DAL-**U184**
- 契约：`foundation_harden_status_response_closed` / `g180`

### 2026-07-23 — Foundation harden (DAL-U183) Denial audit parity

- Terminal `ListExtensions` + Package register/publish/install/disable 拒绝路径写入 denial audit
- DAL-**U183**；契约：`g39` / `b14`

### 2026-07-23 — Foundation harden (DAL-U182) OIDC/IdP status closed envelopes

- `GET /auth/oidc/status` + `/auth/idp/status` closed response DTO（对齐 G189/G190 OpenAPI）
- DAL-**U182**；契约：`foundation_harden_auth_response_closed`

### 2026-07-23 — Foundation harden (DAL-U181) Terminal domain status strip expand

- Admin Domain Foundation Status 探针补齐 knowledge/identity/organization/marketplace/permission
- DAL-**U181**；契约：`g194`

### 2026-07-23 — Foundation harden (DAL-U180) Auth envelopes + closed-DTO suite expand

- JWT status / OIDC providers closed response DTO；callback JSON 走 `OidcTokenEnvelope`
- closed-DTO `extra_field→422` 覆盖 Identity/Permission/Workflow/Org/Event/Knowledge/AI/Marketplace/Twin
- DAL-**U180**

### 2026-07-23 — Foundation harden (DAL-U179) Permission status surface honesty

- `/v1/permission/status` 列出 `role_grant_auto_write`；DAL-**U179**

### 2026-07-23 — Foundation harden (DAL-U178) Status/OpenAPI honesty

- Terminal `/status` 列出 `extension_register` / `extension_revoke`
- Package resolve OpenAPI 补齐运行时已有的 403/409；DAL-**U178**
- 契约：`g194`/`g180`

### 2026-07-23 — Foundation harden (DAL-U177) Extension audit + UuidResult + OIDC DTO

- Terminal Extension register/activate/revoke/invoke 拒绝路径写入 denial audit
- Identity create 响应双键 `id`+`data`（UuidResult）；OIDC refresh/logout closed response DTO
- DAL-**U177**；契约：`g39`/`g20`/`g61`

### 2026-07-23 — Foundation harden (DAL-U176) Declared-surface + closed-DTO + auth posture

- Declared product/ops surface + ops brief handoff resolve fail-closed
- Closed-DTO `extra_field→422` 参数化套件；`allow_dev_headers=false` → 401
- Role-grant 缺 body → 422；priority bool `mode=before` 拒绝；DAL-**U176**
- 契约：`g35`/`g37`/`g78`/`g161` + `foundation_harden_closed_dto_extra`

### 2026-07-23 — Foundation harden (DAL-U175) Demo bootstrap closed envelope

- Dev-only `GET /v1/demo/bootstrap` closed response DTO（`extra=forbid` + exclude_none）；生产网关仍 404
- DAL-**U175**；契约：`g167`/`g168`

### 2026-07-23 — Foundation harden (DAL-U174) Resolve fail-closed + extension invoke

- Product/Ops fixture handoff 一律 Package resolve；拒绝后阻断 Operator
- HTTP：disable 后 resolve → `PACKAGE_ACTION_UNDECLARED`；歧义 → `PACKAGE_ACTION_AMBIGUOUS` 409
- Extension invoke closed serializer + `action`/`surface` 必填；DAL-**U174**
- 契约：`g27`/`g35`/`g168`

### 2026-07-23 — Foundation harden (DAL-U173) Terminal Operator honesty

- Operator `buildPreview` 以 GET preview.`high_impact` 路由 approval/commit（不信任 checkbox）
- Ops brief handoff 先 Package resolve，拒绝后不再进入 Operator
- Terminal intent/preview elevation → 422；DAL-**U173**；契约：`g30`/`g35` + foundation_harden

### 2026-07-23 — Foundation harden (DAL-U172) Context echo + typed helpers

- `POST /v1/context/echo` 运行时 `ContextEchoRequest`（`extra=allow`；elevation 仍 400）
- Payment clearing / Role-grant mint 内部 helper 改为 typed；closed-DTO elevation 契约对齐 422
- DAL-**U172**；契约：`g18`/`g27`/`g83`/`g140`/`g34`/`g161` + terminal `g62`/`g69`

### 2026-07-23 — Foundation harden (DAL-U171) Platform/Auth DTOs + SQL smoke

- Platform IdP/Roles · WebAuthn options · Role-grant 请求体 closed DTO；WebAuthn verify 保持 `extra=allow`（浏览器残差）
- `EAOS_GATEWAY_STORE=sql` 正向 smoke：`/v1/health.gateway_store=sql` + composition 12 槽位
- 修复 `GET /permission/roles` 扁平信封 + 可信上下文；DAL-**U171**
- 契约：`g56`/`g66`/`g78`/`g88`/`g93`/`g151`/`g156`/`g160`/`g161` + foundation_harden

### 2026-07-23 — Foundation harden (DAL-U170) Twin/Brain/AI/Marketplace closed DTOs

- Twin · Brain · AI · Marketplace 请求体 closed Pydantic DTO（`extra=forbid`）；DAL-**U170**
- Brain `execute` / Twin `authorize` 保持 fail-closed；契约：`g28`/`g29`/`g34`/`g114`/`g116`

### 2026-07-23 — Foundation harden (DAL-U169) Workflow/Org/Event/Knowledge closed DTOs

- Workflow · Organization · Platform tenants · Event · Knowledge 请求体 closed Pydantic DTO；DAL-**U169**
- 契约：`g21`/`g23`–`g26`/`g32`/`g105`/`g107`

### 2026-07-23 — Foundation harden (DAL-U168) Identity/Permission closed DTOs

- Identity + Permission 请求体 closed Pydantic DTO（`extra=forbid`）；DAL-**U168**
- 契约：`test_api_gateway_g20_identity` / `g22` / `g128` / `g129`

### 2026-07-23 — Foundation harden (DAL-U167) Package/Terminal authz + closed DTOs

- Resolve 歧义 fail-closed（`PACKAGE_ACTION_AMBIGUOUS`）；Terminal preview `high_impact` 以 Package resolve 为准
- Package/Terminal 请求体 closed Pydantic DTO（`extra=forbid`）；演示移交 resolve 拒绝后不再进入 Operator
- 可选 `EAOS_GATEWAY_STORE=sql` 组合根；`/v1/health` 暴露 `gateway_store`；DAL-**U167**
- 契约：`test_api_gateway_foundation_harden_preview_authz.py` + b14/g30/demo
- 非目标：不实现 CRM CRUD；不自开 PHX-G

### 2026-07-23 — PHX-G292 Legacy Knowledge Extract Delivery

- 接受 ADR-0311；发货单知识包（create/ship/complete/DO→AR）；DAL-**U165**
- 契约：`test_docs_g292_legacy_knowledge_extract_delivery.py`

### 2026-07-23 — PHX-G291 Legacy Knowledge Extract Finance

- 接受 ADR-0310；收款 / 双轨应收知识包；DAL-**U164**
- 契约：`test_docs_g291_legacy_knowledge_extract_finance.py`

### 2026-07-23 — PHX-G290 Legacy Knowledge Extract CRM + Sales

- 接受 ADR-0309；正式 CRM 知识包 + 新增 Sales Order 知识包；根索引 `docs/knowledge/legacy-extract/README.md`；DAL-**U163**
- 契约：`test_docs_g290_legacy_knowledge_extract.py`
- 非目标：不实现业务 CRUD；不打开 Brain/Twin；不继续空 OpenAPI hygiene 循环

### 2026-07-23 — PHX-G289 Terminal OpenAPI Outer-Close Guard Status Deepen

- 接受 ADR-0308；Admin CTA + strip；DAL-**U162**
- 契约：`test_api_gateway_g289_terminal_openapi_outer_close_guard_status.py`

### 2026-07-23 — PHX-G288 OpenAPI Outer-Close Regression Guard

- 接受 ADR-0307；standing allowlist guard；`ContextEchoRequest` 命名；ops **1.0.69**；inventory G288；DAL-**U161**
- 契约：`test_api_gateway_g288_openapi_outer_close_regression_guard.py`

### 2026-07-23 — PHX-G287 Terminal OpenAPI ErrorBody Outer Status Deepen

- 接受 ADR-0306；Admin CTA + strip；DAL-**U160**
- 契约：`test_api_gateway_g287_terminal_openapi_errorbody_outer_status.py`

### 2026-07-23 — PHX-G286 OpenAPI ErrorBody Outer Closed

- 接受 ADR-0305；7 域 ErrorBody 外层 `additionalProperties: false`；Admin bind 去重；ops **1.0.68**；inventory G286；DAL-**U159**
- 契约：`test_api_gateway_g286_openapi_errorbody_outer_closed.py`

### 2026-07-23 — PHX-G285 Terminal OpenAPI Inventory Softener Wave6 Status Deepen

- 接受 ADR-0304；Admin CTA + strip；DAL-**U158**
- 契约：`test_api_gateway_g285_terminal_openapi_softener_wave6_status.py`

### 2026-07-23 — PHX-G284 Foundation Contract Softener Wave6

- 接受 ADR-0303；Terminal UI G/PHX-G pin soft + version soft；ops **1.0.67**；inventory G284；DAL-**U157**
- 契约：`test_api_gateway_g284_openapi_contract_softener_wave6.py`

### 2026-07-23 — PHX-G283 Terminal OpenAPI Inventory Softener Wave5 Status Deepen

- 接受 ADR-0302；Admin CTA + strip；DAL-**U156**
- 契约：`test_api_gateway_g283_terminal_openapi_softener_wave5_status.py`

### 2026-07-23 — PHX-G282 Foundation Contract Softener Wave5

- 接受 ADR-0301；g192/g194/g201/g204/g208 soft；ops **1.0.66**；inventory G282；DAL-**U155**
- 契约：`test_api_gateway_g282_openapi_contract_softener_wave5.py`

### 2026-07-23 — PHX-G281 Terminal OpenAPI Inventory Softener Wave4 Status Deepen

- 接受 ADR-0300；Admin CTA + strip；DAL-**U154**
- 契约：`test_api_gateway_g281_terminal_openapi_softener_wave4_status.py`

### 2026-07-23 — PHX-G280 Foundation Contract Softener Wave4

- 接受 ADR-0299；bulk tip/version soft g176–g189+；ops **1.0.65**；inventory G280；DAL-**U153**
- 契约：`test_api_gateway_g280_openapi_contract_softener_wave4.py`

### 2026-07-23 — PHX-G279 Terminal OpenAPI Inventory Softener Wave3 Status Deepen

- 接受 ADR-0298；Admin CTA + strip；DAL-**U152**
- 契约：`test_api_gateway_g279_terminal_openapi_softener_wave3_status.py`

### 2026-07-23 — PHX-G278 Contract Softener Wave3 + Tip-Parity Guard

- 接受 ADR-0297；g174/g180/g181 soft；ops↔live tip 常驻守卫；ops **1.0.64**；inventory G278；DAL-**U151**
- 契约：`test_api_gateway_g278_openapi_contract_softener_wave3_tip_parity_guard.py`

### 2026-07-22 — PHX-G277 Terminal OpenAPI Inventory Contract Softener Wave2 Status Deepen

- 接受 ADR-0296；Admin CTA + strip；DAL-**U150**
- 契约：`test_api_gateway_g277_terminal_openapi_contract_softener_wave2_status.py`

### 2026-07-22 — PHX-G276 Foundation Contract Softener Wave2

- 接受 ADR-0295；g164/g193/g202/g206/g216/g220/g224 tip/version soft；ops **1.0.63**；inventory G276；DAL-**U149**
- 契约：`test_api_gateway_g276_openapi_contract_softener_wave2.py`

### 2026-07-22 — PHX-G275 Terminal OpenAPI Inventory Ops Milestone Parity Status Deepen

- 接受 ADR-0294；Admin CTA + strip；DAL-**U148**
- 契约：`test_api_gateway_g275_terminal_openapi_ops_milestone_parity_status.py`

### 2026-07-22 — PHX-G274 Ops Milestone Const Parity + Foundation Contract Softener

- 接受 ADR-0293；ops milestone const↔live tip；softener ops/g148/g166；ops **1.0.62**；inventory G274；DAL-**U147**
- 契约：`test_api_gateway_g274_ops_milestone_const_parity_contract_softener.py`

### 2026-07-22 — PHX-G273 Terminal OpenAPI Inventory Brain/Twin Status Deepen

- 接受 ADR-0292；Admin CTA + strip；DAL-**U146**
- 契约：`test_api_gateway_g273_terminal_openapi_brain_twin_status.py`

### 2026-07-22 — PHX-G272 OpenAPI Brain/Twin Outer Schemas Closed

- 接受 ADR-0291；UpsertTwin/PublishInsight + TwinSnapshot/BrainInsight closed；ops **1.0.61**；inventory G272；≠ Twin authorize；DAL-**U145**
- 契约：`test_api_gateway_g272_openapi_brain_twin_schemas_closed.py`

### 2026-07-22 — PHX-G271 Terminal OpenAPI Inventory Knowledge Entity Status Deepen

- 接受 ADR-0290；Admin CTA + strip；DAL-**U144**
- 契约：`test_api_gateway_g271_terminal_openapi_knowledge_entity_status.py`

### 2026-07-22 — PHX-G270 OpenAPI Knowledge Entity/Provenance Schemas Closed

- 接受 ADR-0289；KnowledgeEntity/ProvenanceRecord closed；ops **1.0.60**；inventory G270；DAL-**U143**
- 契约：`test_api_gateway_g270_openapi_knowledge_entity_provenance_schemas_closed.py`

### 2026-07-22 — PHX-G269 Terminal OpenAPI Inventory Event Envelope Status Deepen

- 接受 ADR-0288；Admin CTA + strip；DAL-**U142**
- 契约：`test_api_gateway_g269_terminal_openapi_event_envelope_status.py`

### 2026-07-22 — PHX-G268 OpenAPI Event Envelope/DeadLetter Schemas Closed

- 接受 ADR-0287；EventEnvelope/DeadLetterEntry closed；ops **1.0.59**；inventory G268；DAL-**U141**
- 契约：`test_api_gateway_g268_openapi_event_envelope_dead_letter_schemas_closed.py`

### 2026-07-22 — PHX-G267 Terminal OpenAPI Inventory AI Agent/Memory Status Deepen

- 接受 ADR-0286；Admin CTA + strip；DAL-**U140**
- 契约：`test_api_gateway_g267_terminal_openapi_ai_agent_memory_status.py`

### 2026-07-22 — PHX-G266 OpenAPI AI AgentRun/MemoryEntry Schemas Closed

- 接受 ADR-0285；AgentRun/MemoryEntry closed；ops **1.0.58**；inventory G266；DAL-**U139**
- 契约：`test_api_gateway_g266_openapi_ai_agent_memory_schemas_closed.py`

### 2026-07-22 — PHX-G265 Terminal OpenAPI Inventory Terminal Session Status Deepen

- 接受 ADR-0284；Admin CTA + strip；DAL-**U138**
- 契约：`test_api_gateway_g265_terminal_openapi_terminal_session_status.py`

### 2026-07-22 — PHX-G264 OpenAPI Terminal Session Schemas Closed

- 接受 ADR-0283；OpenSession…InvokeExtension + Session/Intent/Preview/Approval/Commit closed；ops **1.0.57**；inventory G264；DAL-**U137**
- 契约：`test_api_gateway_g264_openapi_terminal_session_schemas_closed.py`

### 2026-07-22 — PHX-G263 Terminal OpenAPI Inventory Package Manifest Status Deepen

- 接受 ADR-0282；Admin CTA + strip；DAL-**U136**
- 契约：`test_api_gateway_g263_terminal_openapi_package_manifest_status.py`

### 2026-07-22 — PHX-G262 OpenAPI Package Manifest Schemas Closed

- 接受 ADR-0281；Register/Install/Resolve + Surface/Action/DeclaredPermission/Manifest/ResolvedAction closed；ops **1.0.56**；inventory G262；DAL-**U135**
- 契约：`test_api_gateway_g262_openapi_package_manifest_schemas_closed.py`

### 2026-07-22 — PHX-G261 Terminal OpenAPI Inventory Organization Entity Status Deepen

- 接受 ADR-0280；Admin CTA + strip；DAL-**U134**
- 契约：`test_api_gateway_g261_terminal_openapi_organization_entity_status.py`

### 2026-07-22 — PHX-G260 OpenAPI Organization Entity Schemas Closed

- 接受 ADR-0279；Tenant/Enterprise/Unit/Membership/IdResponse closed；ops **1.0.55**；inventory G260；DAL-**U133**
- 契约：`test_api_gateway_g260_openapi_organization_entity_schemas_closed.py`

### 2026-07-22 — PHX-G259 Terminal OpenAPI Inventory Marketplace Write/Listing Status Deepen

- 接受 ADR-0278；Admin CTA + strip；DAL-**U132**
- 契约：`test_api_gateway_g259_terminal_openapi_marketplace_write_listing_status.py`

### 2026-07-22 — PHX-G258 OpenAPI Marketplace Write/Listing Schemas Closed

- 接受 ADR-0277；write request + MarketplaceListing closed；ops **1.0.54**；inventory G258；DAL-**U131**
- 契约：`test_api_gateway_g258_openapi_marketplace_write_listing_schemas_closed.py`

### 2026-07-22 — PHX-G257 Terminal OpenAPI Inventory UuidResult Closed Status Deepen

- 接受 ADR-0276；Admin CTA + strip；DAL-**U130**
- 契约：`test_api_gateway_g257_terminal_openapi_uuid_result_closed_status.py`

### 2026-07-22 — PHX-G256 OpenAPI UuidResult/BooleanResult/OkResponse Closed

- 接受 ADR-0275；跨域 success dialect additionalProperties false；ops **1.0.53**；inventory G256；DAL-**U129**
- 契约：`test_api_gateway_g256_openapi_uuid_boolean_ok_result_schemas_closed.py`

### 2026-07-22 — PHX-G255 Terminal OpenAPI Inventory PaymentClearing Success Status Deepen

- 接受 ADR-0274；Admin CTA + strip；DAL-**U128**
- 契约：`test_api_gateway_g255_terminal_openapi_payment_clearing_success_status.py`

### 2026-07-22 — PHX-G254 OpenAPI PaymentClearing Success Schemas Closed

- 接受 ADR-0273；Request/Envelope/Result closed；marketplace **1.2.13**；ops **1.0.52**；inventory G254；DAL-**U127**
- 契约：`test_api_gateway_g254_openapi_payment_clearing_success_schemas_closed.py`

### 2026-07-22 — PHX-G253 Terminal OpenAPI Inventory PaymentClearing StubError Status Deepen

- 接受 ADR-0272；Admin CTA + strip；DAL-**U126**
- 契约：`test_api_gateway_g253_terminal_openapi_payment_clearing_stub_error_status.py`

### 2026-07-22 — PHX-G252 OpenAPI PaymentClearingStubError Envelope Honesty

- 接受 ADR-0271；PaymentClearingStubError；marketplace **1.2.12**；ops **1.0.51**；inventory G252；DAL-**U125**
- 契约：`test_api_gateway_g252_openapi_payment_clearing_stub_error_envelope.py`

### 2026-07-22 — PHX-G251 Terminal OpenAPI Inventory RoleGrant No-Match Status Deepen

- 接受 ADR-0270；Admin CTA + strip；DAL-**U124**
- 契约：`test_api_gateway_g251_terminal_openapi_role_grant_no_match_status.py`

### 2026-07-22 — PHX-G250 OpenAPI RoleGrant No-Match Denial Honesty

- 接受 ADR-0269；RoleGrantNoMatchDenialDetail/Error；permission **1.1.15**；ops **1.0.50**；inventory G250；DAL-**U123**
- 契约：`test_api_gateway_g250_openapi_role_grant_no_match_denial.py`

### 2026-07-22 — PHX-G249 Terminal OpenAPI Inventory WebAuthn Verify Denial Status Deepen

- 接受 ADR-0268；Admin CTA + strip；DAL-**U122**
- 契约：`test_api_gateway_g249_terminal_openapi_webauthn_verify_denial_status.py`

### 2026-07-22 — PHX-G248 OpenAPI WebAuthn Verify Denial Honesty

- 接受 ADR-0267；WebauthnVerifyDenialDetail/Error；auth **1.3.27**；DAL-**U121**；attestation-crypto HARD HOLD 仍关
- 契约：`test_api_gateway_g248_openapi_webauthn_verify_denial.py`

### 2026-07-22 — PHX-G247 Terminal OpenAPI Inventory IdP JWKS Document Status Deepen

- 接受 ADR-0266；Admin CTA + strip IdP JWKS document 标记；inventory 不 bump；DAL-**U120**
- 契约：`test_api_gateway_g247_terminal_openapi_idp_jwks_document_status.py`

### 2026-07-22 — PHX-G246 OpenAPI IdP JWKS Document Named Honesty

- 接受 ADR-0265；IdpJwksDocument/Key；platform **1.0.10**；ops **1.0.49**；RFC residual 仍 open
- Inventory PHX-G246；DAL-**U119**
- 契约：`test_api_gateway_g246_openapi_idp_jwks_document_named.py`

### 2026-07-22 — PHX-G245 Terminal OpenAPI Inventory OIDC Amr/Acr Closed Status Deepen

- 接受 ADR-0264；Admin CTA + strip Amr/Acr closed 标记；inventory 不 bump；DAL-**U118**
- 契约：`test_api_gateway_g245_terminal_openapi_oidc_amr_acr_closed_status.py`

### 2026-07-22 — PHX-G244 OpenAPI OIDC Amr/Acr Details Closed

- 接受 ADR-0263；OidcAmr/AcrRequiredDetails additionalProperties false；auth **1.3.26**；ops **1.0.48**
- Inventory PHX-G244；DAL-**U117**
- 契约：`test_api_gateway_g244_openapi_oidc_amr_acr_details_closed.py`

### 2026-07-22 — PHX-G243 Terminal OpenAPI Inventory WebAuthn Verify Response Status Deepen

- 接受 ADR-0262；Admin CTA + strip RegisterVerifyResponse closed 标记；inventory 不 bump；DAL-**U116**
- 契约：`test_api_gateway_g243_terminal_openapi_webauthn_verify_response_status.py`

### 2026-07-22 — PHX-G242 OpenAPI WebAuthn RegisterVerifyResponse Closed

- 接受 ADR-0261；RegisterVerifyResponse additionalProperties false；auth **1.3.25**；ops **1.0.47**
- Inventory PHX-G242；DAL-**U115**；attestation-crypto HARD HOLD 仍关
- 契约：`test_api_gateway_g242_openapi_webauthn_register_verify_response_closed.py`

### 2026-07-22 — PHX-G241 Terminal OpenAPI Inventory WebAuthn PK Options Status Deepen

- 接受 ADR-0260；Admin CTA + strip PublicKeyCredentialCreationOptions 标记；inventory 不 bump；DAL-**U114**
- 契约：`test_api_gateway_g241_terminal_openapi_webauthn_pk_options_status.py`

### 2026-07-22 — PHX-G240 OpenAPI WebAuthn PublicKeyCredentialCreationOptions Named Honesty

- 接受 ADR-0259；PublicKeyCredentialCreationOptions + nested；auth **1.3.24**；ops **1.0.46**
- Inventory PHX-G240；DAL-**U113**；attestation-crypto HARD HOLD 仍关
- 契约：`test_api_gateway_g240_openapi_webauthn_public_key_creation_options.py`

### 2026-07-22 — PHX-G239 Terminal OpenAPI Inventory DiscoveryRegistryWrite Status Deepen

- 接受 ADR-0258；Admin CTA + strip DiscoveryRegistryWrite 标记；inventory 不 bump；DAL-**U112**
- 契约：`test_api_gateway_g239_terminal_openapi_discovery_registry_write_status.py`

### 2026-07-22 — PHX-G238 OpenAPI DiscoveryRegistryWritePosture Named Honesty

- 接受 ADR-0257；DiscoveryRegistryWritePosture；auth **1.3.23**；platform **1.0.9**；ops **1.0.45**
- Inventory PHX-G238；DAL-**U111**
- 契约：`test_api_gateway_g238_openapi_discovery_registry_write_posture.py`

### 2026-07-22 — PHX-G237 Terminal OpenAPI Inventory Opaque Auth Array-Item Status Deepen

- 接受 ADR-0256；Admin CTA + strip opaque-auth-array-item 标记；inventory 不 bump；DAL-**U110**
- 契约：`test_api_gateway_g237_terminal_openapi_opaque_auth_array_items_status.py`

### 2026-07-22 — PHX-G236 OpenAPI Opaque Auth Array-Item Named Honesty

- 接受 ADR-0255；OidcLoginProviderPublicItem + IdpRegistryIssuerStatusItem；retire AuthStatusEnvelope
- auth **1.3.22**；ops **1.0.44**；inventory PHX-G236；DAL-**U109**
- 契约：`test_api_gateway_g236_openapi_opaque_auth_array_items.py`

### 2026-07-22 — PHX-G235 Terminal OpenAPI Inventory CountMeta Status Deepen

- 接受 ADR-0254；Admin CTA + strip CountMeta 标记；inventory 不 bump；DAL-**U108**
- 契约：`test_api_gateway_g235_terminal_openapi_count_meta_status.py`

### 2026-07-22 — PHX-G234 OpenAPI CountMeta + OidcProvidersPayload Named Honesty

- 接受 ADR-0253；CountMeta + OidcProvidersPayload；platform **1.0.8**；auth **1.3.21**；ops **1.0.43**
- Inventory PHX-G234；DAL-**U107**
- 契约：`test_api_gateway_g234_openapi_count_meta_oidc_providers_payload.py`

### 2026-07-22 — PHX-G233 Terminal OpenAPI Inventory Nested-Anon ≥2 Status Deepen

- 接受 ADR-0252；Admin CTA + strip nested-anon≥2 标记；inventory 不 bump；DAL-**U106**
- 契约：`test_api_gateway_g233_terminal_openapi_nested_anon_ge2_status.py`

### 2026-07-22 — PHX-G232 OpenAPI Nested-Anon ≥2 Payload Named Honesty

- 接受 ADR-0251；ToolInvocation/Health/AdaptersMeta/ContextEcho payloads；ai **1.0.7**；ops **1.0.42**
- Inventory PHX-G232；DAL-**U105**
- 契约：`test_api_gateway_g232_openapi_nested_anon_ge2_payload.py`

### 2026-07-22 — PHX-G231 Terminal OpenAPI Inventory Federation Matrix Status Deepen

- 接受 ADR-0250；Admin CTA + strip federation-matrix 标记；inventory 不 bump；DAL-**U104**
- 契约：`test_api_gateway_g231_terminal_openapi_federation_matrix_status.py`

### 2026-07-22 — PHX-G230 OpenAPI Federation Matrix Payload Named Honesty

- 接受 ADR-0249；FederationMatrix Cell/Payload/Meta；IdpFederationMatrixSummary
- platform **1.0.7**；auth **1.3.20**；ops **1.0.41**；inventory PHX-G230；DAL-**U103**
- 契约：`test_api_gateway_g230_openapi_federation_matrix_payload.py`

### 2026-07-22 — PHX-G229 Terminal OpenAPI Inventory Nested Data Payload Status Deepen

- 接受 ADR-0248；Admin CTA + strip nested-data-payload 标记；inventory 不 bump；DAL-**U102**
- 契约：`test_api_gateway_g229_terminal_openapi_nested_data_payload_status.py`

### 2026-07-22 — PHX-G228 OpenAPI Nested Data Payload Named Honesty

- 接受 ADR-0247；Delivery*/Dispatch*/ReleasePosture named；event **1.0.8**；ops **1.0.40**
- Inventory `milestone=PHX-G228`；`t0188_status=mount_parity_complete_nested_data_payload_named_honest`；DAL-**U101**
- 契约：`test_api_gateway_g228_openapi_nested_data_payload.py`

### 2026-07-22 — PHX-G227 Terminal OpenAPI Inventory HostAcquirePayload Status Deepen

- 接受 ADR-0246；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`HostAcquirePayload named honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U100**
- 契约：`test_api_gateway_g227_terminal_openapi_host_acquire_payload_status.py`

### 2026-07-22 — PHX-G226 OpenAPI HostAcquirePayload Named Honesty

- 接受 ADR-0245；Gate/Acceptance Fully Accepted（Foundation）
- HostAcquireResult.data → named `HostAcquirePayload` `$ref`；marketplace **1.2.11**
- Inventory / ops **1.0.39**：`milestone=PHX-G226`；`t0188_status=mount_parity_complete_host_acquire_payload_named_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U099**
- 契约：`test_api_gateway_g226_openapi_host_acquire_payload.py`

### 2026-07-22 — PHX-G225 Terminal OpenAPI Inventory Named Success Envelopes Status Deepen

- 接受 ADR-0244；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`named success envelopes honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U098**
- 契约：`test_api_gateway_g225_terminal_openapi_named_success_envelopes_status.py`

### 2026-07-22 — PHX-G224 OpenAPI Named Success Envelopes Honesty

- 接受 ADR-0243；Gate/Acceptance Fully Accepted（Foundation）
- 五处 list 成功体提升为 named `$ref` envelopes（knowledge/event/package）
- knowledge **1.0.7**；event **1.0.7**；package **1.0.8**
- Inventory / ops **1.0.38**：`milestone=PHX-G224`；`t0188_status=mount_parity_complete_named_success_envelopes_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U097**
- 契约：`test_api_gateway_g224_openapi_named_success_envelopes.py`

### 2026-07-22 — PHX-G223 Terminal OpenAPI Inventory Stub Detail Const Status Deepen

- 接受 ADR-0242；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`stub detail const honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U096**
- 契约：`test_api_gateway_g223_terminal_openapi_stub_detail_const_status.py`

### 2026-07-22 — PHX-G222 OpenAPI Stub Detail Const Honesty

- 接受 ADR-0241；Gate/Acceptance Fully Accepted（Foundation）
- PaymentClearingStubDetail：`settlement_rail`/`next_action` const `none`
- WebauthnCeremonyStubDetail：`next_action` enum；`milestone` const PHX-G160
- Inventory / ops **1.0.37**：`milestone=PHX-G222`；`t0188_status=mount_parity_complete_stub_detail_const_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U095**
- 契约：`test_api_gateway_g222_openapi_stub_detail_const.py`

### 2026-07-22 — PHX-G221 Terminal OpenAPI Inventory Cross-Domain Elevation $ref Status Deepen

- 接受 ADR-0240；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`cross-domain elevation details $ref honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U094**
- 契约：`test_api_gateway_g221_terminal_openapi_cross_domain_elevation_ref_status.py`

### 2026-07-22 — PHX-G220 OpenAPI Cross-Domain Elevation Details $ref Honesty

- 接受 ADR-0239；Gate/Acceptance Fully Accepted（Foundation）
- 十域 Error*.details：anyOf `$ref` → ContextElevationDenialDetails
- Inventory / ops **1.0.36**：`milestone=PHX-G220`；`t0188_status=mount_parity_complete_cross_domain_elevation_details_ref_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U093**
- 契约：`test_api_gateway_g220_openapi_cross_domain_elevation_details_ref.py`

### 2026-07-22 — PHX-G219 Terminal OpenAPI Inventory Named Details $ref Status Deepen

- 接受 ADR-0238；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`named Details $ref composition honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U092**
- 契约：`test_api_gateway_g219_terminal_openapi_named_details_ref_status.py`

### 2026-07-22 — PHX-G218 OpenAPI Named Details $ref Composition Honesty

- 接受 ADR-0237；Gate/Acceptance Fully Accepted（Foundation）
- auth/marketplace/ops/terminal：`Error*.details` anyOf `$ref` 到命名 *Details
- Inventory / ops **1.0.35**：`milestone=PHX-G218`；`t0188_status=mount_parity_complete_named_details_ref_composition_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U091**
- 契约：`test_api_gateway_g218_openapi_named_details_ref_composition.py`

### 2026-07-22 — PHX-G217 Terminal OpenAPI Inventory Error Details Description-Key Status Deepen

- 接受 ADR-0236；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`ErrorResponse.details description-key honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U090**
- 契约：`test_api_gateway_g217_terminal_openapi_error_details_description_key_status.py`

### 2026-07-22 — PHX-G216 OpenAPI ErrorResponse.details Description-Key Honesty

- 接受 ADR-0235；Gate/Acceptance Fully Accepted（Foundation）
- org/permission/platform/workflow：合并重复 `details.description`，保留 known-shape
- Inventory / ops **1.0.34**：`milestone=PHX-G216`；`t0188_status=mount_parity_complete_error_details_description_key_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U089**
- 契约：`test_api_gateway_g216_openapi_error_details_description_key.py`

### 2026-07-22 — PHX-G215 Terminal OpenAPI Inventory OIDC MFA Enrollment Status Deepen

- 接受 ADR-0234；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`OIDC MFA enrollment details honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U088**
- 契约：`test_api_gateway_g215_terminal_openapi_oidc_mfa_enrollment_status.py`

### 2026-07-22 — PHX-G214 OpenAPI OIDC MFA Enrollment Details Honesty

- 接受 ADR-0233；Gate/Acceptance Fully Accepted（Foundation）
- auth：Amr/Acr Details + ErrorResponse.details 声明 `mfa_enrollment_url`
- Inventory / ops **1.0.33**：`milestone=PHX-G214`；`t0188_status=mount_parity_complete_oidc_mfa_enrollment_details_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U087**
- 契约：`test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py`

### 2026-07-22 — PHX-G213 Terminal OpenAPI Inventory Host-Acquire Details Status Deepen

- 接受 ADR-0232；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`host-acquire details per-code honest` 标记；bootstrap quiet refresh
- Inventory 不 bump；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U086**
- 契约：`test_api_gateway_g213_terminal_openapi_host_acquire_status.py`

### 2026-07-22 — PHX-G212 OpenAPI Host-Acquire Details Per-Code Shape Honesty

- 接受 ADR-0231；Gate/Acceptance Fully Accepted（Foundation）
- marketplace：`HostAcquireAllowlistDenialDetails`（`package_key`）；allowlist fence intact
- Inventory / ops **1.0.32**：`milestone=PHX-G212`；`t0188_status=mount_parity_complete_host_acquire_details_code_shape_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U085**
- 契约：`test_api_gateway_g212_openapi_host_acquire_details_code_shape.py`

### 2026-07-22 — PHX-G211 Terminal OpenAPI Inventory OIDC Details Status Deepen

- 接受 ADR-0230；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`OIDC details per-code honest` 标记；bootstrap quiet refresh
- Inventory 不 bump（对标 G203/G205/G207/G209）；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U084**
- 契约：`test_api_gateway_g211_terminal_openapi_oidc_details_status.py`

### 2026-07-22 — PHX-G210 OpenAPI OIDC Details Per-Code Shapes Honesty

- 接受 ADR-0229；Gate/Acceptance Fully Accepted（Foundation）
- auth：OidcRequiredClaimMissing / RoleRequired / AmrRequired / AcrRequired Details
- Inventory / ops **1.0.31**：`milestone=PHX-G210`；`t0188_status=mount_parity_complete_oidc_details_code_shapes_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U083**
- 契约：`test_api_gateway_g210_openapi_oidc_details_code_shapes.py`

### 2026-07-22 — PHX-G209 Terminal OpenAPI Inventory Elevation Per-Code Status Deepen

- 接受 ADR-0228；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`elevation details per-code honest` 标记；bootstrap quiet refresh
- Inventory 不 bump（对标 G203/G205/G207）；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U082**
- 契约：`test_api_gateway_g209_terminal_openapi_elevation_status.py`

### 2026-07-22 — PHX-G208 OpenAPI Elevation Details Per-Code Shape Honesty

- 接受 ADR-0227；Gate/Acceptance Fully Accepted（Foundation）
- terminal/ops：`ContextElevationDenialDetails`（TERMINAL_CONTEXT_ELEVATION_DENIED）
- Inventory / ops **1.0.30**：`milestone=PHX-G208`；`t0188_status=mount_parity_complete_elevation_details_code_shape_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U081**
- 契约：`test_api_gateway_g208_openapi_elevation_details_code_shape.py`

### 2026-07-22 — PHX-G207 Terminal OpenAPI Inventory Enum-Const Status Deepen

- 接受 ADR-0226；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`single-enum const honest` 标记；bootstrap quiet refresh
- Inventory 不 bump（对标 G203/G205）；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U080**
- 契约：`test_api_gateway_g207_terminal_openapi_enum_const_status.py`

### 2026-07-22 — PHX-G206 OpenAPI Single-Value Enum Const Honesty

- 接受 ADR-0225；Gate/Acceptance Fully Accepted（Foundation）
- package/permission/terminal：5 处单值 enum 并列 const
- Inventory / ops **1.0.29**：`milestone=PHX-G206`；`t0188_status=mount_parity_complete_single_enum_const_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U079**
- 契约：`test_api_gateway_g206_openapi_single_enum_const.py`

### 2026-07-22 — PHX-G205 Terminal OpenAPI Inventory Fields-Shape Status Deepen

- 接受 ADR-0224；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；`details.fields[] known-shape honest` 标记；bootstrap quiet refresh
- Inventory 不 bump（对标 G194/G201/G203）；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U078**
- 契约：`test_api_gateway_g205_terminal_openapi_fields_shape_status.py`

### 2026-07-22 — PHX-G204 OpenAPI Error Details fields[] Known-Shape Honesty

- 接受 ADR-0223；Gate/Acceptance Fully Accepted（Foundation）
- 14 份 catalog OpenAPI：`details.fields[]` 已知形状（仍 additionalProperties: true）
- Inventory / ops **1.0.28**：`milestone=PHX-G204`；`t0188_status=mount_parity_complete_error_details_fields_shape_honest`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U077**
- 契约：`test_api_gateway_g204_openapi_error_details_fields_shape.py`

### 2026-07-22 — PHX-G203 Terminal OpenAPI Inventory Status Surface Deepen

- 接受 ADR-0222；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + strip；ErrorBody.details closed 标记；bootstrap quiet refresh
- Inventory 不 bump（对标 G194/G201）；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U076**
- 契约：`test_api_gateway_g203_terminal_openapi_inventory_status.py`

### 2026-07-22 — PHX-G202 OpenAPI ErrorBody/ErrorResponse Details Inventory

- 接受 ADR-0221；Gate/Acceptance Fully Accepted（Foundation）
- auth **1.3.14** / permission **1.1.10** / org **1.0.4** / workflow **1.0.6** / platform **1.0.3**：`ErrorResponse.details`
- Inventory / ops **1.0.27**：`milestone=PHX-G202`；`t0188_status=mount_parity_complete_errorbody_details_inventory_closed`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U075**
- 契约：`test_api_gateway_g202_openapi_errorbody_details_inventory.py`

### 2026-07-22 — PHX-G201 Terminal Role Catalog Status Surface

- 接受 ADR-0220；Gate/Acceptance Fully Accepted（Foundation）
- Operator strip + Admin CTA；`loadRoleCatalogStatus` 摘要 source_counts / Cap≠grant
- Bootstrap quiet refresh；Inventory 不 bump（对标 G194）
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U074**
- 契约：`test_api_gateway_g201_terminal_role_catalog_status.py`

### 2026-07-22 — PHX-G200 OpenAPI Success-Response Catalog Closure Honesty

- 接受 ADR-0219；Gate/Acceptance Fully Accepted（Foundation）
- Catalog 扫描：全部 mounted `200`/`201` 具备 `content` schema；不宣称 semantic complete
- Inventory / ops **1.0.26**：`milestone=PHX-G200`；`t0188_status=mount_parity_complete_success_response_catalog_closed_semantic_partial`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U073**
- 契约：`test_api_gateway_g200_openapi_success_response_catalog_closure.py`

### 2026-07-22 — PHX-G199 OpenAPI Terminal Extension Invoke Response Parity

- 接受 ADR-0218；Gate/Acceptance Fully Accepted（Foundation）
- Terminal **1.1.6**：`TerminalExtensionInvokeEnvelope` / `InvokeData`（executed=false）
- Inventory / ops **1.0.25**：`milestone=PHX-G199`；`t0188_status=mount_parity_complete_terminal_extension_invoke_response_parity`
- 无任意扩展执行；`full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U072**
- 契约：`test_api_gateway_g199_openapi_terminal_extension_invoke_response.py`

### 2026-07-22 — PHX-G198 OpenAPI Terminal Extension List Response Parity

- 接受 ADR-0217；Gate/Acceptance Fully Accepted（Foundation）
- Terminal **1.1.5**：`TerminalExtensionListEnvelope` / `TerminalExtensionEntry` field parity
- Inventory / ops **1.0.24**：`milestone=PHX-G198`；`t0188_status=mount_parity_complete_terminal_extension_list_response_parity`
- Extension Host sandbox 不变；`full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U071**
- 契约：`test_api_gateway_g198_openapi_terminal_extension_list_response.py`

### 2026-07-22 — PHX-G197 OpenAPI Ops GatewayDetailError KernelError Parity

- 接受 ADR-0216；Gate/Acceptance Fully Accepted（Foundation）
- Ops **1.0.23**：`KernelError` → `GatewayDetailError`；`ErrorResponse.details` 可选
- Inventory：`milestone=PHX-G197`；`t0188_status=mount_parity_complete_ops_gateway_detail_error_parity`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U070**
- 契约：`test_api_gateway_g197_openapi_ops_gateway_detail_error.py`

### 2026-07-22 — PHX-G196 OpenAPI RoleGrant Auto-Write Response/Detail Parity

- 接受 ADR-0215；Gate/Acceptance Fully Accepted（Foundation）
- Permission **1.1.9**：`RoleGrantAutoWriteMintResponse` / `RoleGrantMintedGrant` / `RoleGrantAutoWriteStubDetail` field parity
- Inventory / ops **1.0.22**：`milestone=PHX-G196`；`t0188_status=mount_parity_complete_role_grant_auto_write_response_detail_parity`
- Auto-write 默认仍 fail-closed；`full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U069**
- 契约：`test_api_gateway_g196_openapi_role_grant_auto_write_response_detail.py`

### 2026-07-22 — PHX-G195 OpenAPI RoleCatalogStatus source_counts Field Parity

- 接受 ADR-0214；Gate/Acceptance Fully Accepted（Foundation）
- Permission **1.1.8**：`RoleCatalogSourceCounts`（catalog/oidc_map/grant_map）；`catalog_store` enum
- Inventory / ops **1.0.21**：`milestone=PHX-G195`；`t0188_status=mount_parity_complete_role_catalog_status_source_counts_field_parity`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U068**
- 契约：`test_api_gateway_g195_openapi_role_catalog_status_source_counts.py`

### 2026-07-22 — PHX-G194 Terminal Domain Foundation Status Surface

- 接受 ADR-0213；Gate/Acceptance Fully Accepted（Foundation）
- Admin CTA + `domainFoundationStatus`；探测 twin/brain/ai/workflow/package/terminal/event
- Bootstrap quiet refresh；Brain execute / Twin authorize 仍 fail-closed
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U067**
- 契约：`test_api_gateway_g194_terminal_domain_foundation_status.py`

### 2026-07-22 — PHX-G193 OpenAPI Package/Terminal/Event Status Mount Parity

- 接受 ADR-0212；Gate/Acceptance Fully Accepted（Foundation）
- Package **1.0.4** status parity；Terminal **1.1.4** `/terminal/status`；Event **1.0.4** `/events/status`
- Inventory / ops **1.0.20**：`milestone=PHX-G193`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U066**
- 契约：`test_api_gateway_g193_*`；g130 catalog 扩展

### 2026-07-22 — PHX-G192 OpenAPI Identity/Org/Knowledge Status Body Field Parity

- 接受 ADR-0211；Gate/Acceptance Fully Accepted（Foundation）
- Identity **1.0.4** / Organization **1.0.3** / Knowledge **1.0.4** status field parity
- Inventory / ops **1.0.19**：`milestone=PHX-G192`
- `full_openapi_http_complete` 仍为 false；包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U065**
- 契约：`test_api_gateway_g192_openapi_identity_org_knowledge_status_parity.py`

### 2026-07-22 — PHX-G191 OpenAPI Brain/Twin/AI/Workflow Status Body Field Parity

- 接受 ADR-0210；Gate/Acceptance Fully Accepted（Foundation）
- Brain/Twin OpenAPI **1.0.4**；AI **1.0.4**；Workflow **1.0.5** status field parity
- Inventory / ops **1.0.18**：`milestone=PHX-G191`
- Brain execute / Twin authorize **仍 fail-closed**；`full_openapi_http_complete=false`
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U064**
- 契约：`test_api_gateway_g191_openapi_brain_twin_ai_workflow_status_parity.py`

### 2026-07-22 — PHX-G190 OpenAPI OIDC Status Body Field Parity

- 接受 ADR-0209；Gate/Acceptance Fully Accepted（Foundation）
- Auth OpenAPI **1.3.13**：`OidcStatusEnvelope` / `OidcStatusData`；IdP.oidc `$ref`
- Inventory / ops **1.0.17**：`milestone=PHX-G190`；`t0188_status=mount_parity_complete_oidc_status_body_field_parity`
- `full_openapi_http_complete` 仍为 false；关闭 G189 nested oidc defer
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U063**
- 契约：`test_api_gateway_g190_openapi_oidc_status_body_parity.py`

### 2026-07-22 — PHX-G189 OpenAPI IdP Status Body Field Parity

- 接受 ADR-0208；Gate/Acceptance Fully Accepted（Foundation）
- Auth OpenAPI **1.3.12**：`IdpStatusEnvelope` / aggregates；nested `oidc` 仍 open
- Inventory / ops **1.0.16**：`milestone=PHX-G189`；`t0188_status=mount_parity_complete_idp_status_body_field_parity`
- `full_openapi_http_complete` 仍为 false
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U062**
- 契约：`test_api_gateway_g189_openapi_idp_status_body_parity.py`

### 2026-07-22 — PHX-G188 OpenAPI JWT Status Body Field Parity

- 接受 ADR-0207；Gate/Acceptance Fully Accepted（Foundation）
- Auth OpenAPI **1.3.11**：`JwtStatusEnvelope` / `JwtStatusData` / `JwtDenylistPosture`
- Inventory / ops **1.0.15**：`milestone=PHX-G188`；`t0188_status=mount_parity_complete_jwt_status_body_field_parity`
- `full_openapi_http_complete` 仍为 false；IdP nested schema deferred；no jti dump
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U061**
- 契约：`test_api_gateway_g188_openapi_jwt_status_body_parity.py`

### 2026-07-22 — PHX-G187 OpenAPI OIDC Login Product-Posture Schema Parity

- 接受 ADR-0206；Gate/Acceptance Fully Accepted（Foundation）
- Auth OpenAPI **1.3.10**：`OidcLoginProductPosture` emitted field parity
- Inventory / ops **1.0.14**：`milestone=PHX-G187`；`t0188_status=mount_parity_complete_oidc_login_product_posture_schema_honest`
- `full_openapi_http_complete` 仍为 false；attestation crypto / Brain / Twin / Cap→grant 仍关闭
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U060**
- 契约：`test_api_gateway_g187_openapi_oidc_login_product_posture_schema.py`

### 2026-07-22 — PHX-G186 OpenAPI Marketplace Status Body Field Parity

- 接受 ADR-0205；Gate/Acceptance Fully Accepted（Foundation）
- Marketplace OpenAPI **1.2.6**：`PaymentClearingProduct` + `FoundationStatusData` emitted field parity
- Inventory / ops **1.0.13**：`milestone=PHX-G186`；`t0188_status=mount_parity_complete_marketplace_status_body_field_parity`
- `full_openapi_http_complete` 仍为 false；external PSP / Brain / Twin / Cap→grant 仍关闭
- 包仍 `0.2.1`；Alembic 仍 `0029`；DAL-**U059**
- 契约：`test_api_gateway_g186_openapi_marketplace_status_body_parity.py`

### 2026-07-22 — PHX-G160 WebAuthn Env-Gated Live Mint

- 接受 ADR-0183；Gate/Acceptance Fully Accepted（Foundation）
- **DAL-G008** explicit PO「继续WebAuthn live mint」+ DAL-**U037**
- Env `EAOS_WEBAUTHN_REGISTRATION_ENABLED`（default OFF → 503）；需 `EAOS_WEBAUTHN_RP_ID` + `EAOS_WEBAUTHN_ORIGIN`
- `POST /v1/auth/webauthn/register/options|verify`：challenge-bound mint → Identity.BindCredential；`attestation_crypto_verified=false`
- auth OpenAPI **1.3.6**；inventory fence → `webauthn_attestation_crypto_verify`；Terminal 薄行；Manifest G160
- 包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：packed/TPM attestation crypto；`/auth/webauthn/register`；Brain execute；Twin authorize；Cap→grant
- 不回归 G161 Role→grant / G163 T2/T3 intake
- 契约：`test_api_gateway_g160_webauthn_live_mint.py`

### 2026-07-22 — PHX-G164 OpenAPI Semantic Deepen (T-0188)

- 接受 ADR-0182；Gate/Acceptance Fully Accepted（Foundation）
- PO cue「继续全量 OpenAPI 语义深挖」+ DAL-**U036**
- Inventory：`route_mount_parity_complete=true`；`full_openapi_http_complete=false`；fence → `full_openapi_semantic_parity_t0188`
- Knowledge UuidResult `{id}` + GatewayDetailError；AI/Event error 信封；Brain/Twin 403 文档化；Workflow/AI/Brain status fences
- ops OpenAPI **1.0.2**；Terminal 薄行；Manifest G164
- 包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：`full_openapi_http_complete=true`；Brain execute；Twin authorize；Const/BP
- 契约：`test_api_gateway_g164_openapi_semantic_deepen.py`

### 2026-07-22 — PHX-G163 T2 / T3 Evidence Intake & Live Capture

- 接受 ADR-0180；Gate/Acceptance Fully Accepted（Research；docs-only）
- 新增 [T2_T3_EVIDENCE_INTAKE.md](../research/T2_T3_EVIDENCE_INTAKE.md)（**NRI-T2-T3-INTAKE**）：T2 vs T3 bars；intake + verification；Registry **0 Complete**
- 新增 [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](../research/templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md)
- Readiness board deepen（floors 仍 **T1**；0/10 live Complete）；DAL-**U034**；Manifest G163
- Explicit Out：fake Complete；Board re-Promote；Eng invent from Research；Brain/Twin
- 契约：`test_docs_g163_t2_t3_evidence_intake.py`

### 2026-07-22 — PHX-G162 Marketplace Payment Clearing (Eng Explicit Defer `4`)

- 接受 ADR-0181；Gate/Acceptance Fully Accepted（Foundation）
- **DAL-G007** explicit PO「继续Eng 4 支付清算」+ DAL-**U035**
- Env `EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED`（default OFF → 503）；ON = internal audit record（≠ external PSP）
- `POST /v1/marketplace/listings/{id}/payment-clearing`；status `payment_clearing_product`；marketplace OpenAPI **1.2.0**
- Terminal 薄探针；inventory fence → external PSP/arbitration；Manifest G162
- 包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：external PSP；metering；arbitration；Brain execute；Twin authorize
- 契约：`test_api_gateway_g162_payment_clearing.py`

### 2026-07-22 — PHX-G161 Role→grant Env-Gated Live Mint

- 接受 ADR-0179；Gate/Acceptance Fully Accepted（Foundation）
- **DAL-G006** explicit PO「继续Role→grant live mint」+ DAL-**U032**
- Env `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`（default OFF → 503）；需非空 `EAOS_PERMISSION_ROLE_GRANT_MAP`
- `POST /v1/permission/role-grants`：就绪时按 roles 展开 map → `Permission.grant`（Cap≠grant；≠ Cap→grant）
- permission OpenAPI **1.1.3**；Terminal 薄行；Runbook/Checklist/Compat；Manifest G161
- 包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：payment；Brain execute；Twin authorize；全量 OpenAPI；Const/BP
- 契约：`test_api_gateway_g161_role_grant_live_mint.py`

### 2026-07-22 — PHX-G159 Generation-1 Architecture Review Board Hold

- 接受 ADR-0178；Gate/Acceptance Fully Accepted（Research；docs-only）
- **DAL-G005** CA-authorized Board session；NRI-ARC-RP-001…010 → **Hold×10**
- [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md) 记录 session；**Hold ≠ Promote ≠ Eng ingest**
- Manifest G159；DAL-**U031**；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_docs_g159_architecture_review_board_hold.py`

### 2026-07-21 — PHX-G158 Autonomous Soft-Queue Natural Pause

- 接受 ADR-0177；Gate/Acceptance Fully Accepted（docs-only）
- [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md) 记录 **Natural Pause**；「继续」不 invent 空循环
- Resume = Board / live T2–T3 / mint-with-PO / Eng `4` PO / 审慎 OpenAPI 大切片
- Manifest G158；DAL-**U030**；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_docs_g158_autonomous_soft_queue_pause.py`

### 2026-07-21 — PHX-G157 Foundation Ops / Checklist Hygiene After G156

- 接受 ADR-0176；Gate/Acceptance Fully Accepted（docs-only）
- [OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)：Smoke 含 G154 `ceremony_step` + G156 Role→grant stub 503
- [RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)：Manifest G145…G157
- Manifest G157；DAL-**U029**；包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：live mint；支付；Brain；Twin；全量 OpenAPI HTTP
- 契约：`test_docs_g157_foundation_ops_hygiene.py`

### 2026-07-21 — PHX-G156 Role→grant Auto-Write Stub Deepen

- 接受 ADR-0175；Gate/Acceptance Fully Accepted
- 新增 `role_grant_auto_write.py` + `routers/role_grants.py`：`POST /v1/permission/role-grants` → 503 `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`
- `role_grant_product` milestone **PHX-G156**；`auto_write_routes` 列 stub；permission OpenAPI → **1.1.2**；Terminal 薄行；DAL-**U028**
- Explicit Out：live mint（仍需 **explicit PO**）；支付清算；Brain execute；Twin authorize；WebAuthn live mint；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g156_role_grant_auto_write_stub.py`

### 2026-07-21 — PHX-G155 T2 / T3 Evidence Readiness Board

- 接受 ADR-0174；Gate/Acceptance Fully Accepted（docs-only）
- 新增 [T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md)（**NRI-T2-T3-EVID**）：RP-001…010 全部 **T1**；**0 / 10** live T2/T3 Complete；criteria only
- Index/Library/G2 tip/PROJECT_STATUS/DAL-**U027**；Manifest G155
- Explicit Out：fake tier upgrade；AR self-certify；Eng invent；mint；支付；Brain；Twin；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_docs_g155_t2_t3_evidence_readiness.py`

### 2026-07-21 — PHX-G154 WebAuthn Ceremony Stub Observability

- 接受 ADR-0173；Gate/Acceptance Fully Accepted
- 503 detail 增加 `ceremony_step` / `registration_minted=false` / `attestation_verified=false` / `next_action=none`
- `webauthn_product` milestone **PHX-G154**；inventory fence → `webauthn_live_credential_mint`
- OpenAPI `auth.openapi.yaml` → **1.3.4**；Terminal 薄行；DAL-**U026**
- Explicit Out：live create/get mint；Role→grant mint；支付清算；Brain execute；Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g154_webauthn_ceremony_observability.py`

### 2026-07-21 — PHX-G153 Foundation Ops / Compatibility / Checklist Hygiene

- 接受 ADR-0172；Gate/Acceptance Fully Accepted（docs-only）
- [OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)：milestones G144–G153；Smoke 含 G151 stub 503 + Held fences
- [COMPATIBILITY.md](../release/COMPATIBILITY.md)：G145–G153 additive on `0.2.1` / `0029`
- [RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)：Manifest G145–G153 + mint/payment holds
- Manifest G153；DAL-**U025**；包仍 `0.2.1`；Alembic 仍 `0029`
- Explicit Out：live WebAuthn mint；Role→grant mint；支付清算；Brain execute；Twin authorize
- 契约：`test_docs_g153_foundation_ops_hygiene.py`

### 2026-07-21 — PHX-G152 AR Board Queue + Foundation Release Hygiene

- 接受 ADR-0171；Gate/Acceptance Fully Accepted（docs-only）
- 新增 [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)（**NRI-AR-BOARD-QUEUE**）：汇总 NRI-ARC-RP-001…010 Awaiting Board；不自证；不代填 decision
- `RELEASE_MANIFEST.yaml` milestones 补齐 PHX-G145…G152；包仍 `0.2.1`；Alembic 仍 `0029`
- Index/Library/G2 tip/ENG tip/PROJECT_STATUS/DAL-**U024**
- Explicit Out：Board self-certify；live WebAuthn mint；Role→grant mint；支付清算；Brain execute；Twin authorize
- 契约：`test_docs_g152_ar_board_queue_and_release_hygiene.py`

### 2026-07-21 — PHX-G151 WebAuthn Ceremony Stub Deepen

- 接受 ADR-0170；Gate/Acceptance Fully Accepted
- 新增 `webauthn_ceremony.py` + `routers/webauthn.py`：`POST /v1/auth/webauthn/register/options|verify` → 503 `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`
- `webauthn_product` G151：`webauthn_registration_enabled=false`；`registration_routes` 列出两条 stub；`/auth/webauthn/register` 仍 ABSENT
- Env `EAOS_WEBAUTHN_REGISTRATION_ENABLED` 文档化为 future-only（G151 不 mint）
- OpenAPI `auth.openapi.yaml` → **1.3.3**；Terminal 薄行 stub 文案；DAL-**U023**
- Explicit Out：live create/get mint；Role→grant mint；支付清算；Brain execute；Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g151_webauthn_ceremony_stub.py`

### 2026-07-21 — Wave 3 Architecture Review Candidates RP-006/008/010 (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md](../research/programs/RP-006-ai-infrastructure-platform/ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md)（NRI-ARC-RP-006；Awaiting Board；不自证；`kernel_bypass: never`）
- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md](../research/programs/RP-008-smart-factory/ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)（NRI-ARC-RP-008；Awaiting Board；不自证；`mes_kernelization: never`；`machine_control_from_brain: never`）
- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md](../research/programs/RP-010-future-enterprise-operating-model/ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md)（NRI-ARC-RP-010；Awaiting Board；不自证；`constitution_rewrite: never`；`execution_authority: none`；synthesis not rewrite）
- Wave 3 AR set complete：NRI-ARC-RP-006 / 008 / 010（peer 臻宇；WP Accepted；AIRM/SFSM/FEOM；GP/PW/SA；Draft NRI opinion Hold for T2/T3 or Remain Research Asset；Board blank）
- **Wave 1+2+3 AR Candidates complete for RP-001…010**（全部 Awaiting Board；不自证）
- DAL：**DAL-U020** / **DAL-U021** / **DAL-U022**；G2 tip / Index / Library / Status 同步
- 契约：`test_research_rp006_architecture_review_candidate.py` · `test_research_rp008_architecture_review_candidate.py` · `test_research_rp010_architecture_review_candidate.py`

### 2026-07-21 — RP-003 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md](../research/programs/RP-003-capability-first/ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md)（NRI-ARC-RP-003；Awaiting Board；不自证；Cap≠Org；Capability ≠ Permission；`auto_grant_minted: never`）
- Wave 2 AR deepen：NRI-ARC-RP-003（peer 臻宇；WP Accepted；CFM；CG-01…02；IND/RISK/PEER）；Draft NRI opinion Hold for T2/T3 or Remain Research Asset；Board blank
- DAL：**DAL-U018**（RP-003 AR Candidate；preserves **DAL-U016** / **DAL-U017** / **DAL-U019** if present）；G2 tip / Index / Library / Status 同步
- 契约：`test_research_rp003_architecture_review_candidate.py`

### 2026-07-21 — RP-004 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md](../research/programs/RP-004-organization-neutrality/ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md)（NRI-ARC-RP-004；Awaiting Board；不自证；Structure ≠ Permission；`org_shape_grant: never`；Cap≠Org；Twin authorize / Brain execute fail-closed）
- Wave 2 AR deepen：NRI-ARC-RP-004（peer 臻宇；WP Accepted；ONM；NA-01…02；IND/RISK/PEER）；Draft NRI opinion Hold for T2/T3 or Remain Research Asset；Board blank
- DAL：**DAL-U019**（RP-004 AR Candidate；preserves **DAL-U016**–**U018** if present）；G2 tip / Index / Library / Status 同步
- 契约：`test_research_rp004_architecture_review_candidate.py`

### 2026-07-21 — RP-009 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md](../research/programs/RP-009-enterprise-brain-evolution/ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md)（NRI-ARC-RP-009；Awaiting Board；不自证；`execution_authority: none`；IC-06 Act forbidden；never Act；ADR-0030；Twin authorize / Brain execute fail-closed）
- Wave 2 AR deepen：NRI-ARC-RP-009（peer 臻宇；WP Accepted；BEM；AE-01…03；IND/RISK/PEER）；Draft NRI opinion Hold for T2/T3 or Remain Research Asset；Board blank
- DAL：**DAL-U017**（RP-009 AR Candidate；preserves **DAL-U016**）；G2 tip / Index / Library / Status 同步
- 契约：`test_research_rp009_architecture_review_candidate.py`

### 2026-07-21 — RP-002 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md](../research/programs/RP-002-enterprise-dna/ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md)（NRI-ARC-RP-002；Awaiting Board；不自证；DNA≠grant；constraint vector never authorization；Twin authorize fail-closed）
- Wave 2 AR set start：NRI-ARC-RP-002（peer 臻宇；WP Accepted；EDNA；SC-01…03；IND/RISK/PEER）
- DAL：**DAL-U016**（RP-002 AR Candidate）；G2 tip / Index / Library / Status 同步
- 契约：`test_research_rp002_architecture_review_candidate.py`

### 2026-07-21 — RP-005 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md](../research/programs/RP-005-ai-workforce-transformation/ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)（NRI-ARC-RP-005；Awaiting Board；不自证；Title≠Permission；Cap≠grant；AI not legal person；Digital Human ≠ duty bearer；`auto_grant_minted: never`；Role→grant mint NOT opened）
- Wave 1 AR set complete：NRI-ARC-RP-001 / **NRI-ARC-RP-005** / NRI-ARC-RP-007
- DAL：**DAL-U015**（RP-005 AR Candidate）；G2 tip / Index / Library / Status / ROADMAP 同步
- 契约：`test_research_rp005_architecture_review_candidate.py`

### 2026-07-21 — RP-007 Architecture Review Candidate (docs-only)

- Research：开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md](../research/programs/RP-007-enterprise-evolution-engine/ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md)（NRI-ARC-RP-007；Awaiting Board；不自证；`execution_authority=none`；ADR-0030）
- DAL：**DAL-U014**（RP-007 AR Candidate）；G2 tip / Index / Library / ROADMAP Research tip 同步
- 契约：`test_research_rp007_architecture_review_candidate.py`

### 2026-07-21 — PHX-G150 Autonomous Execution Directive + RP-001 AR Candidate (docs-only)

- 接受 ADR-0169；新增 [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md) v1.1（HARD HOLDS；Explicit Defer；价值平局；Research 默认 AR Candidate + T2/T3；加深优先序；强制 milestone report + DAL）
- DAL v1.2：**DAL-G004** Active（与 G003 共存）；**DAL-U012**（G150/AED）；**DAL-U013**（RP-001 AR Candidate）
- Research：首开 [ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md](../research/programs/RP-001-enterprise-discovery/ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)（NRI-ARC-RP-001；Awaiting Board；不自证）
- Dual-Track 「继续」→ AED；Eng/G2 tip 指向 AED；包仍 `0.2.1`；Alembic 仍 `0029`；无代码
- 契约：`test_docs_g150_autonomous_execution_directive.py` · `test_research_rp001_architecture_review_candidate.py`

### 2026-07-21 — NRI Generation-2 Research Tip Board (docs-only)

- 新增 [GENERATION2_TIP_BOARD.md](../research/GENERATION2_TIP_BOARD.md)（NRI-G2-TIP）：G1（RP-001…010 WP Accepted）完成；Next = optional deepenings only
- Explicit Out：不 invent RP-011…；不 Const/BP rewrite；不从 Research invent Eng；不 Brain execute；Architecture Review 不自证
- Index/Library/Status 同步；DAL-U011；契约：`test_research_generation2_tip_board.py`

### 2026-07-21 — PHX-G149 Eng Soft-Queue Tip Hygiene (docs-only)

- 接受 ADR-0168；新增 [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)（Done G144–G148；Held 支付/`4`/Brain/Twin/ceremony/mint；Next = optional deepenings only）
- TASKS：T-0199 → 完成（G138）；T-0204 → 完成（G25/G127）；与 Fully Accepted 对齐
- Explicit Out：支付清算、WebAuthn ceremony、Role→grant mint、Brain execute、Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`；无代码
- DAL-U010；契约：`test_docs_g149_eng_tip.py`

### 2026-07-21 — PHX-G148 OpenAPI Inventory Product Posture (thin)

- 接受 ADR-0167；T-0188 标为 **部分完成（inventory posture G148；全量路由仍延后）**（DAL-U009）
- `openapi_inventory_product` 挂入 `GET /v1/adapters` meta；合同计数来自 `list_openapi_contracts()`；adapter registry 对齐；thin-probe vs deferred 域；`full_openapi_http_complete=false`
- Terminal 薄行展示库存姿态；ops OpenAPI → **1.0.1**
- Explicit Out：全量 FastAPI 路由 parity、WebAuthn ceremony、Role→grant mint、支付清算、Brain execute、Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g148_openapi_inventory_product.py`

### 2026-07-21 — PHX-G147 OIDC Login Product Surface (thin)

- 接受 ADR-0166；关闭 T-0189「OIDC 登录页延后」（DAL-U008）
- `oidc_login_product` 挂入 `oidc_status()`；`authorization_code_enabled` 来自配置；`live_routes` 组合 Auth Code 路径；未配置 fail-closed
- Terminal 命名「OIDC Login Product」面板复用 Login/Refresh/Logout/providers CTA；无新认证协议
- auth OpenAPI → **1.3.2**
- Explicit Out：WebAuthn ceremony、Role→grant mint、支付清算、Brain execute、Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g147_oidc_login_product.py`

### 2026-07-21 — PHX-G146 Role→grant Product Posture (thin)

- 接受 ADR-0165；Eng Explicit Defer `3` 以只读产品姿态面打开（DAL-U007）
- `role_grant_product` 挂入 `build_role_catalog_status()`；`auto_grant_from_role_enabled=false`；`auto_write_routes=[]`
- 手工 G128/G129 与 evaluate-only G83 仍为非 auto-write 相对面；`/permission/role-grants` 仍 ABSENT
- Cap≠grant / title≠permission 记入 `fail_closed_reasons`；Terminal 薄行；permission OpenAPI → **1.1.1**
- Explicit Out：Role→grant auto-write、WebAuthn ceremony、支付清算、Brain execute、Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g146_role_grant_product_posture.py`

### 2026-07-21 — PHX-G145 WebAuthn / MFA Product Posture (thin)

- 接受 ADR-0164；Eng Explicit Defer `2` 以只读产品姿态面打开（DAL-U006）
- `webauthn_product` 挂入 `oidc_status()`；`webauthn_registration_enabled=false`；`registration_routes=[]`
- IdP MFA enrollment redirect（G89/G134）仍为唯一 live enroll；`/auth/webauthn/register` 仍 ABSENT
- Terminal 薄行展示姿态 + 既有 MFA enrollment 链接；auth OpenAPI → **1.3.1**
- Explicit Out：live WebAuthn ceremony、Role→grant、支付清算、Brain execute、Twin authorize；包仍 `0.2.1`；Alembic 仍 `0029`
- 契约：`test_api_gateway_g145_webauthn_product_posture.py`

### 2026-07-21 — PHX-G144 Foundation 0.2.1 Release Train

- 接受 ADR-0163；包基线 `0.2.0` → **`0.2.1`**（pyproject / SDK / Manifest / Helm / `GET /v1/release`）
- 纳入已接受 G18–G143；Alembic head 仍 `0029_eaos_declared_roles_g90`（无新 schema）
- Explicit Out：支付清算、Role→grant、WebAuthn 产品页、Brain execute、Twin authorize
- DAL-U005：Eng Explicit Defer `1` 开口记录
- 契约：`test_release_g144.py`；R17/G76/G51 跟进 `0.2.1`
- 最终验证：见本切片合约回归；七步复核 Fully Accepted

### 2026-07-21 — DAL-G003 Continuous Autonomy + Wave 3 Complete (Governance / Research)

- 激活 [DELEGATED_AUTHORITY_LEDGER](DELEGATED_AUTHORITY_LEDGER.md) **DAL-G003**（至 2026-07-27）：全权审批 + 合宪自主开发
- Usage：DAL-U002（激活）；DAL-U003（RP-010 Pass+WP）；DAL-U004（RP-008 Pass+WP）
- RP-008 / RP-010 peer **臻宇** Pass → `WHITE_PAPER-RP-008` / `WHITE_PAPER-RP-010` Accepted
- Generation-1（RP-001…010）peer + WP content 闸门关闭；Eng `4` 支付清算仍暂缓；Brain/Twin fail-closed；包版本仍 `0.2.0`

### 2026-07-21 — NRI Generation-1 Peer Gate Board (Research Track)

- 新增 `GENERATION1_PEER_GATE.md`：RP-001…010 闸门矩阵；不代填 Pass/Acceptance
- Research invent 以 peer/WP cues 为 tip；无 Eng / Brain-execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-010 SA-01…02 + IND/RISK + PEER Ready (Research Track)

- 新增 `audits/SA-01…02`（Synthetic Complete；`constitution_rewrite: never`；`execution_authority: none`）
- 新增 `INDUSTRY_ANALYSIS.md`（P-EOM-01…10）、`RISK_ANALYSIS.md`（R-EOM-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-EOM-01…12）
- Reviewer Pending；无 Const/BP/Brain-execute / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-010 Future Enterprise Operating Model Research Draft (Research Track)

- 新增 `FUTURE_ENTERPRISE_OPERATING_MODEL.md`（ES-01…07；E0–E4；一致性矩阵；`constitution_rewrite: never`）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-010.md`；程序升为 Research v1.0
- Wave 3 early；下一步 SA-01…02；无 Const/BP/Brain-execute / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-008 PW-01…02 + IND/RISK + PEER Ready (Research Track)

- 新增 `walkthroughs/PW-01…02`（Synthetic Complete；`mes_kernelization: never`；`machine_control_from_brain: never`）
- 新增 `INDUSTRY_ANALYSIS.md`（P-SF-01…10）、`RISK_ANALYSIS.md`（R-SF-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-SF-01…12）
- Reviewer Pending；无 MES Kernel / machine-control / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-008 Smart Factory Specialization Model Research Draft (Research Track)

- 新增 `SMART_FACTORY_SPECIALIZATION_MODEL.md`（SF-01…08；PR0–PR4；`mes_kernelization: never`；Brain≠machine control）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-008.md`；程序升为 Research v1.0
- Wave 3 early；下一步 PW-01…02；无 MES Kernel / machine-control / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — PHX Delegated Authority Ledger (Governance)

- 新增 [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md)（PHX-DAL）：Active Grants + Usage Log
- 回填 DAL-G001（Research 审批窗口 2026-07-21…22）与 DAL-U001（8 份 WP content Accepted）
- 持续自主开发模式 **未开启**（待显式 cue）；包版本仍 `0.2.0`

### 2026-07-21 — NRI WP Content Acceptance Batch (CA Delegated) (Research Track)

- Chief Architect 授权窗口 **2026-07-21…2026-07-22**：Research Track 审批由 Cursor 代记
- WP-RP-001 / 002 / 003 / 004 / 005 / 006 / 007 / 009 → **Accepted White Paper**（content Accepted）
- 不含：虚构 RP-008/010 peer 姓名；Eng Explicit Defer `1`–`4`；Architecture Review；Const/BP/Kernel/Runtime 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-006 Peer Pass + WP Draft (Research Track)

- Peer **臻宇** Pass：PR-INF-01…12 → WP Draft Allowed
- 新增 `WHITE_PAPER-RP-006.md`（Draft；content Approval Pending）
- Pass ≠ WP Acceptance ≠ Architecture Review ≠ Runtime/Kernel openings ≠ Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Wave 3 Peer Assigned: 臻宇 (RP-006) (Research Track)

- `RP-006 peer = 臻宇`；Assigned — decision Pending
- 指派 ≠ Pass；未开 WP；无 Runtime/Kernel/Brain-execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-009 Peer Pass + WP Draft (Research Track)

- Peer **臻宇** Pass：PR-BE-01…12 → WP Draft Allowed
- 新增 `WHITE_PAPER-RP-009.md`（Draft；content Approval Pending）
- Pass ≠ WP Acceptance ≠ Architecture Review ≠ Brain execute ≠ Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-006 GP-01…02 + IND/RISK + PEER Ready (Research Track)

- 新增 `gap-profiles/GP-01…02`（Synthetic Complete；`kernel_bypass: never`）
- 新增 `INDUSTRY_ANALYSIS.md`（P-INF-01…10）、`RISK_ANALYSIS.md`（R-INF-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-INF-01…12）
- [WAVE3_PEER_ASSIGNMENT](../research/WAVE3_PEER_ASSIGNMENT.md)；Reviewer Pending；无 Runtime/Kernel/Brain-execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-006 AI Infrastructure Reference Model Research Draft (Research Track)

- 新增 `AI_INFRASTRUCTURE_REFERENCE_MODEL.md`（ID-01…08；I0–I4；`kernel_bypass: never`）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-006.md`；程序升为 Research v1.0
- Wave 3 early start；下一步 GP-01…02；无 Runtime/Kernel/Brain-execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-009 AE-01…03 + IND/RISK + Peer Assigned (Research Track)

- 新增 `red-team/AE-01…03`（Synthetic Complete；`execution_authority: none`；fail-closed）
- 新增 `INDUSTRY_ANALYSIS.md`（P-BE-01…10）、`RISK_ANALYSIS.md`（R-BE-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-BE-01…12）
- Peer **臻宇** Assigned（decision Pending）；不开 WP；无 Brain execute / Twin authorize / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI RP-003 / RP-004 Peer Pass + WP Drafts (Research Track)

- Peer **臻宇** Pass：PR-CAP-01…12 / PR-ON-01…12 → WP Draft Allowed
- 新增 `WHITE_PAPER-RP-003.md`、`WHITE_PAPER-RP-004.md`（Draft；content Approval Pending）
- Pass ≠ WP Acceptance ≠ Architecture Review ≠ Cap/Org→grant ≠ Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Wave 2 Peers Assigned: 臻宇 (RP-003 / RP-004 / RP-009) (Research Track)

- `RP-003 peer = 臻宇`；`RP-004 peer = 臻宇`；`RP-009 peer = 臻宇`（designated；PEER 未开）
- 指派 ≠ Pass；未开 RP-003/004 WP；无 Cap/Org/Brain execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-009 Brain Evolution Model Research Draft (Research Track)

- 新增 `BRAIN_EVOLUTION_MODEL.md`（IC-01…05；never Act；`execution_authority: none`）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-009.md`；程序升为 Research v1.0
- 下一步 anti-execution AE-01…03；Brain execute / Twin authorize 仍 fail-closed；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-004 Industry/Risk Draft + Peer Package (Research Track)

- 新增 `INDUSTRY_ANALYSIS.md`（P-ON-01…10）、`RISK_ANALYSIS.md`（R-ON-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-ON-01…12）
- Reviewer 仍 Pending；不代填 Pass；不开 WP；无 Org-shape→grant / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-004 Neutrality Audits NA-01…02 (Research Track)

- 新增 `audits/NA-01-wt01-mfg.md`、`NA-02-wt02-svc.md`（N-01…08；`org_shape_grant: never`；Cap ID stable）
- 下一步 Industry/Risk Draft + peer；RP-003 peer 仍待指派；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-004 Organization Neutrality Model Research Draft (Research Track)

- 新增 `ORGANIZATION_NEUTRALITY_MODEL.md`（OF-01…07；N-01…08；V-ON-01…05）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-004.md`；程序升为 Research v1.0
- 下一步 synthetic neutrality audits NA-01…02；RP-003 peer 仍待指派；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-003 Industry/Risk Draft + Peer Package (Research Track)

- 新增 `INDUSTRY_ANALYSIS.md`（P-CAP-01…10）、`RISK_ANALYSIS.md`（R-CAP-01…14）、`PEER_REVIEW_PACKAGE.md`（PR-CAP-01…12）
- Reviewer 仍 Pending；不代填 Pass；不开 WP；无 Cap→grant / Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-003 Synthetic Capability Graphs CG-01…02 (Research Track)

- 新增 `graphs/CG-01-wt01-mfg.md`、`CG-02-wt02-svc.md`（Cap≠Org；`auto_grant_minted: never`；critical-path gaps）
- 下一步 Industry/Risk Draft + peer package；不开 WP / Eng；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-002 Peer Pass + White Paper Draft (Research Track)

- PR-DNA-01…12 均为 Yes/Pass；Selected outcome = Pass → WP Draft Allowed（臻宇）
- 新增 `WHITE_PAPER-RP-002.md`（Draft；内容 Approval 仍 Pending）
- Peer Pass ≠ WP Acceptance ≠ Architecture Review；DNA≠grant；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-002 Peer Assigned: 臻宇 (Research Track)

- `RP-002 peer = 臻宇`；PEER Status = Assigned — Awaiting Reviewer Decision
- 指派 ≠ Pass；未开 RP-002 White Paper；无 Eng / DNA→grant 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Wave 1 Peer Pass + White Paper Drafts (Research Track)

- 臻宇 / 包锦昱 / 牟蓉：清单均为 Yes/Pass；Selected outcome = Pass → WP Draft Allowed
- 新增 `WHITE_PAPER-RP-001/005/007.md`（Status: Draft；内容 Approval 仍 Pending）
- Peer Pass ≠ WP Acceptance ≠ Architecture Review；无 Eng / Brain execute / Twin authorize / Role→grant 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-003 Capability First Model Research Draft (Research Track)

- 新增 `CAPABILITY_FIRST_MODEL.md`（Cap≠Org / L0–L4 / A0–A4）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-003.md`；程序升为 Research v1.0
- 下一步 synthetic capability graphs CG-01…02；不代填 peer Pass；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-002 Peer Review Package + Wave 2 Assignment Cue (Research Track)

- 新增 `PEER_REVIEW_PACKAGE.md`（PR-DNA-01…12）与 `WAVE2_PEER_ASSIGNMENT.md`
- Reviewer 仍 Pending；不代填 Pass；不开 White Paper；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-002 Industry + Risk Analysis Draft (Research Track)

- 新增 `INDUSTRY_ANALYSIS.md`（P-DNA-01…10）与 `RISK_ANALYSIS.md`（R-DNA-01…14）
- 不代填 Wave 1 peer Pass；不开 White Paper；无 Eng 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Wave 1 Peers Complete: 臻宇 / 包锦昱 / 牟蓉 (Research Track)

- `RP-001 peer = 臻宇`；`RP-007 peer = 牟蓉`（RP-005 仍为 包锦昱）
- 三份 PEER package 均为 Assigned — Awaiting Reviewer Decision；Approval/WP 仍 Pending
- 指派 ≠ Pass；无 Eng / Constitution / Blueprint / Runtime 开口

### 2026-07-21 — NRI-RP-005 Peer Assigned: 包锦昱 (Research Track)

- `RP-005 peer = 包锦昱`（legal 优先）；PEER package → Assigned — Awaiting Reviewer Decision
- Approval / WP 仍 Pending；指派 ≠ Pass；无 Eng / Role→grant 开口
- RP-001 / RP-007 peer 仍待真实姓名

### 2026-07-21 — NRI-RP-002 DNA Scorecards + Peer Assignment Guard (Research Track)

- 新增 SC-01…03 synthetic DNA scorecards（WT-01/02/03）；`authorization_input: never`
- 新增 `WAVE1_PEER_ASSIGNMENT.md`：**拒绝**字面 `<name>` 占位指派；不自审通过 WP
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-002 Enterprise DNA Model Research Draft (Research Track)

- 新增 `ENTERPRISE_DNA_MODEL.md`（DX-01…08）、`EVIDENCE_PACK.md`、`DELIVERABLES-RP-002.md`；程序升为 Research v1.0
- Wave 2 结构性研究提前启动；下一步 synthetic DNA scorecards；仍不自审 Wave 1 WP
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Wave 1 Peer Packages + RP-005 IND/RISK (Research Track)

- 新增 RP-005/RP-007 `PEER_REVIEW_PACKAGE.md`；RP-005 `INDUSTRY_ANALYSIS.md` + `RISK_ANALYSIS.md`（Draft）
- 三框架均具备可执行 peer 指派口令；**不自审通过** White Paper
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-007 Evidence Pack + Input Freeze + Trigger Tests (Research Track)

- 新增 `EVIDENCE_PACK.md`、`INPUT_FREEZE.md`、`DELIVERABLES-RP-007.md`
- 新增 synthetic trigger tests TT-01 (HOLD) / TT-02 (Assist≠Agentize) / TT-03 (Robot safety HOLD)；皆 `execution_authority: none`
- Wave 1 三框架证据门禁齐；共同阻塞为人工 peer；无 Eng / Brain execute 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-005 Synthetic Role Inventories RI-01…02 (Research Track)

- 新增 `inventories/RI-01-office-synthetic.md`（14 role classes；RC3 Holds）与 `RI-02-ops-synthetic.md`（Robot/Device；RC5；Cap≠title）
- Evidence Pack：≥2 inventories → **Yes**；legal peer 仍 Pending；`auto_grant_minted: never`
- 无 Constitution / Blueprint / Kernel / Runtime / Eng Role→grant 开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI Peer Package (RP-001) + RP-005 Evidence Pack (Research Track)

- 新增 RP-001 `PEER_REVIEW_PACKAGE.md`（人工 reviewer 未分配；禁止自审通过）
- 新增 RP-005 `EVIDENCE_PACK.md` + `DELIVERABLES-RP-005.md`（复用 RP-001 pack 模式）
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-001 Industry + Risk Analysis Draft (Research Track)

- 新增 `INDUSTRY_ANALYSIS.md`（P1–P10）与 `RISK_ANALYSIS.md`（R-ED-01…14）
- Deliverables #2/#15 → Draft；WP gate Near；阻塞项仅剩人工 peer review
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`

### 2026-07-21 — NRI-RP-001 Synthetic Walkthroughs WT-01…03 (Research Track)

- 新增 `walkthroughs/WT-01|02|03-*-synthetic.md`（制造 Cap≠Org、服务业 license theater、阶段对比）
- 更新 Evidence Pack WP gate：≥3 walkthrough **Yes**（T1 synthetic）；peer review 仍 Pending
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`
- 契约：`test_research_rp001_evidence_pack.py`（含 walkthrough 门禁）

### 2026-07-21 — NRI-RP-001 Evidence Pack + Deliverables (Research Track)

- 新增 `EVIDENCE_PACK.md`（NRI-RP-001-EVID）与 `DELIVERABLES-RP-001.md`；定义 White Paper freeze 证据门禁
- 更新 EDF Promotion Stance、Research Index / Library、PROJECT_STATUS Research Track
- 无 Constitution / Blueprint / Kernel / Runtime / Eng 产品开口；包版本仍 `0.2.0`
- 契约：`test_research_rp001_evidence_pack.py`；全量 contracts `790 passed`

### 2026-07-21 — PHX-G143 Dual-Track Governance Formalization

- 接受 ADR-0162；正式采用 Engineering + Research (NRI) Dual-Track
- 新增 `DUAL_TRACK_GOVERNANCE.md` 操作手册；同步 MASTER_PLAN / ROADMAP / PROJECT_STATUS / NRI 交叉引用
- 无 Kernel/Runtime/Constitution/Blueprint/Alembic 变更；包版本仍 `0.2.0`
- 契约：`test_dual_track_g143_governance.py`
- 最终验证：`786 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G142 Organization Get Enterprise Thin Probe

- 接受 ADR-0161；Terminal 接线 `GET /v1/enterprises/{id}`；同步 `api/README.md` Terminal 目录
- 无新 Alembic；包版本仍 `0.2.0`
- 最终验证：`781 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G141 Marketplace Foundation Commercial Terminal Probe

- 接受 ADR-0160；Terminal 接线 pricing/invoice/dispute/revenue-share（≠ 支付清算）
- 修正 `docs/api/README.md` 商业面表述；无新 Alembic；包版本仍 `0.2.0`
- 最终验证：`779 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G140 Terminal Ops Echo + Workflow Deprecation

- 接受 ADR-0159；Terminal 接线 context echo（elevation→400）与 workflow definition deprecation
- 无新 Alembic；包版本仍 `0.2.0`；同步 PROJECT_STATUS 契约计数漂移
- 最终验证：`777 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G139 Gateway Ops OpenAPI Catalog

- 接受 ADR-0158；新增 `ops.openapi.yaml`（health/release/adapters/context）；Manifest 13→14
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`775 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G138 Identity AI Employee / Governor Thin Probe

- 接受 ADR-0157；Gateway + Terminal 接线 platform governor 与 AI employee（profile/assign/reassign）
- Identity OpenAPI 与 Gateway 对齐；无新 Alembic；包版本仍 `0.2.0`
- 最终验证：`770 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G137 Identity Credential/Session Revoke Thin Probe

- 接受 ADR-0156；Gateway + Terminal 接线 credential validate/revoke 与 session revoke
- 无新 Alembic；包版本仍 `0.2.0`；≠ AI employee / platform governor
- 最终验证：`768 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G136 Permission Roles List OpenAPI

- 接受 ADR-0155；`permission.openapi.yaml` 增补 GET /roles（v1.1.0；≠ Role→grant）
- 无运行时变更；Manifest 仍 13；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`766 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G135 Platform OpenAPI Catalog

- 接受 ADR-0154；新增 `platform.openapi.yaml`（roles + IdP/federation）；Manifest 12→13
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`；≠ Role→grant
- 最终验证：`764 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G134 OIDC MFA Enrollment OpenAPI

- 接受 ADR-0153；`auth.openapi.yaml` 增补 MFA enrollment redirect（v1.3.0；≠ WebAuthn 产品页）
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`759 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G133 OIDC Refresh / Logout OpenAPI

- 接受 ADR-0152；`auth.openapi.yaml` 增补 Bearer-gated refresh/logout（v1.2.0）；MFA enrollment 另批
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`757 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G132 OIDC Login / Callback OpenAPI

- 接受 ADR-0151；`auth.openapi.yaml` 增补 login/callback/providers（v1.1.0）；refresh/logout/MFA 另批
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`755 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G131 Auth OpenAPI Status Catalog

- 接受 ADR-0150；新增 `auth.openapi.yaml`（OIDC/IdP/JWT status）；Release Manifest OpenAPI 11→12
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`753 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G130 OpenAPI Foundation Status Catalog

- 接受 ADR-0149；9 份域 OpenAPI 补齐 11 条 Foundation `GET */status`（含 roles/twin/brain）；auth status 另批
- 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`748 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G129 Permission Deprecate / Delegate Thin Probe

- 接受 ADR-0148；Smart Terminal Admin Deprecate policy / Delegate grant；create grant 可选 delegable
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`；≠ Role→grant
- 最终验证：`746 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G128 Permission Policy / Grant Manual Write Thin Probe

- 接受 ADR-0147；Smart Terminal Admin Create·Activate policy；Create·Revoke grant（手工写入；≠ Role→grant）
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`744 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G127 Platform Tenant Lifecycle Thin Probe

- 接受 ADR-0146；Smart Terminal Admin Create / Suspend / Reactivate platform tenant（platform 上下文）
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`742 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G126 Organization Enterprise Lifecycle Thin Probe

- 接受 ADR-0145；Smart Terminal Admin Suspend / Reactivate / Close enterprise
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`740 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G125 Organization Membership Transfer / End Thin Probe

- 接受 ADR-0144；Smart Terminal Admin Transfer membership unit / End membership
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`738 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G124 Organization Lifecycle Thin Probe

- 接受 ADR-0143；Smart Terminal Admin Set unit status / Suspend·Reactivate membership
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`736 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G123 Organization Unit / Membership Thin Probe

- 接受 ADR-0142；Smart Terminal Admin Upsert unit / Get tree / Add·List memberships；Organization Terminal 运维面齐
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`734 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-21 — PHX-G122 Organization Status / Tenant / Enterprise Thin Probe

- 接受 ADR-0141；`GET /v1/organization/status`；Smart Terminal Admin Get tenant / Create·List enterprises；unit/membership 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`732 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G121 Identity Credential / Session Thin Probe

- 接受 ADR-0140；Smart Terminal Admin Bind credential / Create·Validate session；Identity Terminal 运维面齐
- session 以目标 subject 作 trusted header；secret 仅 vault ref；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`730 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G120 Identity Status / Subject Thin Probe

- 接受 ADR-0139；`GET /v1/identity/status`；Smart Terminal Admin Register/Resolve subject；credential/session 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`728 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G119 AI Approval / Commit Thin Probe

- 接受 ADR-0138；Smart Terminal Admin Request approval / Commit（approval-gated）；AI Runtime Terminal 运维面齐
- 无审批 commit 仍 fail-closed；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`726 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G118 AI Tools / Memory Thin Probe

- 接受 ADR-0137；Smart Terminal Admin Register/Invoke tool + Write/Read memory；approval/commit 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`724 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G117 AI Runtime Status / Run Thin Probe

- 接受 ADR-0136；`GET /v1/ai/status`；Smart Terminal Admin Create/Get run（trusted header `ai_employee`）；tools/memory/approval 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`722 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G116 Brain Execute Fail-Closed Thin Probe

- 接受 ADR-0135；Smart Terminal Admin Execute brain insight（expect 403）；Brain Terminal 运维面齐
- 不打开 execute 执行权；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`720 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G115 Brain Status / Insight Thin Probe

- 接受 ADR-0134；`GET /v1/brain/status`；Smart Terminal Admin Publish/Get insight；execute 仍 fail-closed
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`718 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G114 Twin Authorize Fail-Closed Thin Probe

- 接受 ADR-0133；Smart Terminal Admin Authorize from twin（expect 403）；Twin Terminal 运维面齐
- 不打开 authorize 执行权；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`716 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G113 Twin Status / Snapshot Thin Probe

- 接受 ADR-0132；`GET /v1/twin/status`；Smart Terminal Admin Upsert/Get snapshot；authorize 仍 fail-closed
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`714 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G112 Knowledge Link / Provenance Thin Probe

- 接受 ADR-0131；Smart Terminal Admin Create link / Get provenance；Knowledge Terminal 运维面齐
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：见 contracts 全绿；七步复核 Fully Accepted

### 2026-07-20 — PHX-G111 Knowledge Archive / Share / Search Thin Probe

- 接受 ADR-0130；Smart Terminal Admin Archive/Share entity + Search；link/provenance 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`710 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G110 Knowledge Status / Entity Thin Probe

- 接受 ADR-0129；`GET /v1/knowledge/status`；Smart Terminal Admin Upsert/Get/List entity；archive/share/search 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`708 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G109 Package Publish / Install / Disable / Resolve Thin Probe

- 接受 ADR-0128；Smart Terminal Admin Publish/Install/Disable/Resolve（既有 G27 路径）；Package Terminal 运维面齐
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`706 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G108 Package Status / Manifest / Surfaces Thin Probe

- 接受 ADR-0127；`GET /v1/packages/status`；Smart Terminal Admin Register/Get manifest + List surfaces；publish/install 另批
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`704 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G107 Workflow Compensate / Escalate Thin Probe

- 接受 ADR-0126；Smart Terminal Admin Compensate instance / Escalate task（既有 compensation/escalation）；Workflow Terminal 运维面齐
- 状态真相仍归 Workflow Kernel；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`702 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G106 Workflow Signal / Cancel Thin Probe

- 接受 ADR-0125；Smart Terminal Admin Signal/Cancel workflow instance（既有 signals/cancellation）；compensate/escalate 另批
- 状态真相仍归 Workflow Kernel；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`700 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G105 Workflow Task Approve / Reject Thin Probe

- 接受 ADR-0124；Smart Terminal Admin Approve/Reject workflow task（既有 approval/rejection）；signal/cancel 另批
- 审批真相仍归 Workflow Kernel；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`698 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G104 Workflow Status / Definition / Instance Thin Probe

- 接受 ADR-0123；`GET /v1/workflow/status`；Smart Terminal Admin 定义/实例/任务薄探针（无审批写路径 UI）
- 审批真相仍归 Workflow Kernel；支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`696 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G103 Marketplace Acquire Technical Thin Probe

- 接受 ADR-0122；Smart Terminal Admin Acquire listing（既有技术 `/acquire`）；≠ 支付清算
- 支付清算仍 fail-closed；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`694 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G102 Marketplace Listing Lifecycle Thin Probe

- 接受 ADR-0121；Smart Terminal Admin listing signature/submit/review/publish/revoke（既有生命周期路径）
- 无 acquire/支付清算 UI；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`692 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G101 Marketplace Status + Listing Thin Probe

- 接受 ADR-0120；`GET /v1/marketplace/status`（payment_clearing/external_arbitration/metering=fail_closed）；Terminal Create/Get listing
- 不实现支付清算；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`690 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G100 Terminal Event Subscribe/Replay Thin Probe

- 接受 ADR-0119；Smart Terminal Admin Subscribe event + Replay event（既有 `/subscriptions`、`/{id}/replay`）
- Terminal 不采集 signing_secret；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`688 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G99 Terminal Event Enqueue/Publish Thin Probe

- 接受 ADR-0118；Smart Terminal Admin Enqueue outbox + Publish event（既有 `/v1/events/outbox`、`/v1/events`）
- 无订阅配置 UI；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`686 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G98 Terminal Event Dispatch Thin Probe

- 接受 ADR-0117；Smart Terminal Admin Dispatch due events + Get event（既有 `/v1/events/dispatch`、`/v1/events/{id}`）
- 无订阅配置 UI；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`684 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G97 Terminal Event Bus Stats Thin Probe

- 接受 ADR-0116；Smart Terminal Admin Event delivery stats / List dead letters / Replay dead letter（既有 `/v1/events/*`）
- 无订阅配置 UI；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`682 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G96 JWT Denylist Status Observability

- 接受 ADR-0115；`GET /v1/auth/jwt/status` 脱敏摘要（denylist 来源/条目数/runtime revoke 计数）；Terminal「JWT status」
- 不下发 jti 列表或 denylist 原文；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`680 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G95 Terminal Effective Permissions Thin Probe

- 接受 ADR-0114；Smart Terminal Admin「List effective permissions」（既有 `/principals/{id}/effective-permissions`）
- path principal 独立输入；self-or-auditor 不变；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`677 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G94 Terminal Permission Evaluate Thin Probe

- 接受 ADR-0113；Smart Terminal Admin Evaluate permission + Explain last decision（既有 `/evaluations` / `/decisions/.../explanation`）
- 无 body 冒充 principal；无自动写 grant；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`675 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G93 Permission Roles Status Observability

- 接受 ADR-0112；`GET /v1/permission/roles/status` 脱敏摘要（store / catalog / grant_map 计数）；Terminal「Roles status」
- 无自动写 grant / 不下发 map 原文；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`673 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G92 Terminal Tenant Roles Catalog Read

- 接受 ADR-0111；Smart Terminal Admin「List tenant roles catalog」（租户上下文调用既有 `/v1/permission/roles`）
- 无写路径 / 无自动写 grant；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`670 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G91 Terminal Platform Roles Admin Thin Ops

- 接受 ADR-0110；Smart Terminal Admin 声明角色 List / Upsert / Disable（调用既有 `/v1/platform/roles`）
- 无自动写 grant；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0029`
- 最终验证：`668 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G90 Declared EAOS Roles Catalog SQL Store

- 接受 ADR-0109；`EAOS_ROLE_CATALOG_STORE=memory|sql`；表 `kernel.eaos_declared_roles`；平台 `/v1/platform/roles`
- 无自动写 grant；支付清算另批；包版本仍 `0.2.0`；Alembic head `0029`
- 最终验证：`666 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G89 OIDC MFA Enrollment URL Gate

- 接受 ADR-0108；`EAOS_OIDC_MFA_ENROLLMENT_URL` + `/mfa-enrollment` 302；amr/acr deny 可附 URL；Terminal 薄链
- 无 WebAuthn 产品页；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`661 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G88 Opt-in EAOS Roles Catalog Gate

- 接受 ADR-0107；`GET /v1/permission/roles` 聚合 catalog/oidc_map/grant_map；可选 `EAOS_ROLE_CATALOG`
- 无 Role SQL / 自动写 grant；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`656 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G87 OIDC Authorize ACR/Prompt Step-Up Gate

- 接受 ADR-0106；`EAOS_OIDC_AUTHORIZE_ACR_VALUES` / `AUTHORIZE_PROMPT` → authorize 附加参数；status 可观测
- 无 MFA 注册 UX；与 G80 token 门禁互补；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`653 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G86 OIDC Provider End-Session Catalog Gate

- 接受 ADR-0105；`LOGIN_PROVIDERS` 第 7 段 `end_session`；logout overlay 优先；catalog `has_end_session`
- 无 MFA 注册 / Role 目录；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`649 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G85 OIDC Per-Provider Refresh Gate

- 接受 ADR-0104；JWT `eaos_oidc_login_provider` 驱动 refresh/logout overlay；无 Alembic
- 无 MFA 注册 / provider end_session 目录；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`645 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G84 OIDC Multi-Provider Login Gate

- 接受 ADR-0103；`EAOS_OIDC_LOGIN_PROVIDERS` + `/login?provider=` + `/providers`；Terminal 薄链接
- 无完整社交 UX / MFA 注册 / per-provider refresh；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`640 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G83 Opt-in Context Roles Evaluate Grant Map Gate

- 接受 ADR-0102；`EAOS_PERMISSION_ROLE_GRANT_MAP` → evaluate ephemeral allow；`MATCHED_CONTEXT_ROLE`；deny 优先
- 无 Role 表 / grant 写入 / social login；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`635 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G82 JWT eaos_roles → ExecutionContext Roles Gate

- 接受 ADR-0101；JWT `eaos_roles` → `ExecutionContext.roles`；`/v1/context` 暴露；body 不可提升
- 无 Permission sync / social login；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`627 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G81 OIDC Claim→Role JWT Mint Gate

- 接受 ADR-0100；`EAOS_OIDC_ROLE_CLAIM` + `ROLE_MAP` → JWT `eaos_roles`；可选 `REQUIRE_MAPPED_ROLE`
- 无 Permission sync / social login；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`621 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G80 OIDC amr/acr Auth Context Gate

- 接受 ADR-0099；`EAOS_OIDC_REQUIRED_AMR` / `REQUIRED_ACR`；callback/refresh remap fail-closed；status `required_amr*` / `required_acr*`
- 无 MFA 注册 UI / social login；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`614 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G79 OIDC Required Claims Gate

- 接受 ADR-0098；`EAOS_OIDC_REQUIRED_CLAIMS`；callback/refresh remap fail-closed；status `required_claims*`
- 无 MFA / social login / claim→role；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0028`
- 最终验证：`608 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G78 Tenant IdP Federation Issuer Priority

- 接受 ADR-0097；绑定 `priority`（默认 100，越小越优先）；`POST .../bindings/{id}/priority`；Terminal Set priority
- Alembic `0028`；enforce 语义不变；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`603 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G77 Tenant IdP Federation Policy Matrix

- 接受 ADR-0096；`GET /v1/platform/idp/federation/matrix`；Terminal Admin Matrix；status `federation.matrix`
- 无策略引擎 / social login；支付清算另批；包版本仍 `0.2.0`；Alembic 仍 `0027`
- 最终验证：`595 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G76 Deploy Region Identity Foundation

- 接受 ADR-0095；可选 `EAOS_DEPLOY_REGION`；`/v1/release.deploy_region`；Helm `region.id` + Compose
- 非 multi-region SaaS / failover；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`587 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G75 OIDC Refresh KMS Key Provider

- 接受 ADR-0094；`KEY_PROVIDER=kms` + `KMS_BACKEND=http|aws|gcp|azure`；http 可测；云 SDK 可选 extras
- status 暴露 `refresh_encrypt_kms_backend`；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`580 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G74 OIDC Refresh Fernet Key Provider

- 接受 ADR-0093；`EAOS_OIDC_REFRESH_KEY_PROVIDER=env|file`；file 经 `*_KEY_FILE`；`kms` Foundation fail-closed
- status 暴露 `refresh_encrypt_key_provider`；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`576 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G73 Service Mesh AuthorizationPolicy Foundation

- 接受 ADR-0092；opt-in Istio AuthorizationPolicy；`mesh.authz.enabled` 默认关；ALLOW 已认证 principals
- 不替代应用 JWT；不装控制面；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`572 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G72 Service Mesh Traffic CRD Foundation

- 接受 ADR-0091；opt-in Istio VirtualService + DestinationRule；`mesh.traffic.enabled` 默认关
- ISTIO_MUTUAL；不装控制面；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`568 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G71 Service Mesh Policy CRD Foundation

- 接受 ADR-0090；opt-in Istio `PeerAuthentication`；`mesh.policy.enabled` 默认关；需 `mesh.enabled`
- 不装控制面；无 VS/DR；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`564 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G70 OIDC Refresh Re-encrypt On Read

- 接受 ADR-0089；`EAOS_OIDC_REFRESH_REENCRYPT_ON_READ`；get 路径旧密文迁主密钥；status 暴露开关
- 默认 off；无 Alembic；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`560 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G69 Tenant IdP Federation Terminal Ops

- 接受 ADR-0088；Terminal Admin List/Bind/Unbind；复用 `/v1/platform/idp/federation/*`；platform 上下文
- path 租户独立输入；无策略矩阵；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`557 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G68 JWT Tenant IdP Federation Enforcement

- 接受 ADR-0087；租户面 JWT 与 OIDC 共用 `EAOS_TENANT_IDP_FEDERATION`；`eaos_oidc_issuer` 优先
- 平台面/开发头不强制；`federation.planes` 含 jwt；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`553 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G67 Tenant IdP Federation SQL Adapter

- 接受 ADR-0086；`EAOS_TENANT_IDP_FEDERATION_STORE=memory|sql`（默认 memory）；Alembic `0027`
- 联邦绑定可持久化；缺 URL fail-closed；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`547 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G66 Tenant IdP Federation Binding

- 接受 ADR-0085；平台面租户↔issuer bind/list/unbind；`EAOS_TENANT_IDP_FEDERATION` 可选 OIDC fail-closed
- 进程内存；无联邦 UI/SQL；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`544 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G65 OIDC Refresh Fernet Key Rotation

- 接受 ADR-0084；`EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS` + MultiFernet；status `refresh_encrypt_key_count`
- 主密钥加密、旧密钥解密窗口；无 Alembic 变更；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`540 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G64 OIDC Refresh Token Field Encryption

- 接受 ADR-0083；`EAOS_OIDC_REFRESH_ENCRYPT` + Fernet 密钥；密文前缀 `eaos1:`；默认 off
- status 暴露 `refresh_encrypt`；无 Alembic 变更；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`536 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G63 OIDC Refresh Binding SQL Adapter

- 接受 ADR-0082；`EAOS_OIDC_REFRESH_STORE=memory|sql`（默认 memory）；Alembic `0026`
- Refresh 绑定可持久化；缺 URL fail-closed；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`532 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G62 Platform IdP Registry Terminal Ops

- 接受 ADR-0081；Terminal Admin List/Register/Disable/Discovery sync；平台上下文无租户提升
- 复用 `/v1/platform/idp/*`；无组织联邦引擎；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`529 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-20 — PHX-G61 OIDC Refresh + RP-Logout

- 接受 ADR-0080；`EAOS_OIDC_REFRESH` / `EAOS_OIDC_RP_LOGOUT`；`POST /v1/auth/oidc/refresh|logout`
- 进程内 refresh 绑定 + runtime jti revoke；Terminal 薄按钮；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`525 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G60 OIDC Discovery → Registry Writeback

- 接受 ADR-0079；`EAOS_OIDC_DISCOVERY_REGISTRY_WRITE`；Discovery `jwks_uri` upsert 注册表；不写 env
- 平台 `POST /v1/platform/idp/discovery/sync`；env/wire 仍优先；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`520 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G59 Service Mesh Foundation

- 接受 ADR-0078；Helm `mesh` opt-in 注入标签/注解（默认关）；厂商无关；不渲染网格 CRD
- 不安装控制面；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`515 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G58 KEDA Foundation

- 接受 ADR-0077；Helm `keda` opt-in ScaledObject（默认关）；与 HPA/VPA 互斥 fail-closed
- 不安装 KEDA operator；Service Mesh/支付清算另批；包版本仍 `0.2.0`
- 最终验证：`510 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G57 IdP Registry SQL Adapter

- 接受 ADR-0076；`EAOS_IDP_REGISTRY_STORE=memory|sql`（默认 memory）；SQL 复用 Alembic `0025`
- Gateway 仓储接线；缺 `EAOS_DATABASE_URL` fail-closed；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`505 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G56 Multi-IdP Write Registry

- 接受 ADR-0075；平台面 `/v1/platform/idp/issuers`；进程内注册表；校验合并 env 优先
- Alembic `0025_idp_issuer_bindings_g56`；SQL 适配器另切片；支付清算另批；包版本仍 `0.2.0`
- 最终验证：`500 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G55 Multi-IdP Status UI

- 接受 ADR-0074；`GET /v1/auth/idp/status` 只读脱敏；Terminal Admin「IdP / JWT status」探针
- 写注册表见后续 G56；支付清算另批；版本仍 `0.2.0`
- 最终验证：`496 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G54 VPA Foundation

- 接受 ADR-0073；Helm `vpa` opt-in（默认关，`updateMode=Off`）；与 HPA 互斥 fail-closed
- 不安装 VPA components；Mesh/支付清算另批；版本仍 `0.2.0`
- 最终验证：`493 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G53 HPA Foundation

- 接受 ADR-0072；Helm `autoscaling` opt-in（默认关）+ `autoscaling/v2` HPA；启用时省略 Deployment.replicas
- 不安装 metrics-server；VPA/Mesh/支付清算另批；版本仍 `0.2.0`
- 最终验证：`488 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G52 Ingress / TLS Foundation

- 接受 ADR-0071；Helm `ingress` opt-in（默认关）+ TLS / cert-manager 注解；`INGRESS.md`
- 不安装 Controller/Operator；支付清算另批；版本仍 `0.2.0`
- 最终验证：`483 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G51 Kubernetes Helm Foundation

- 接受 ADR-0070；`deploy/helm/eaos` 单副本 Gateway + 可选 Postgres；`HELM.md`
- Ingress/HPA/多区域/支付清算另批；版本仍 `0.2.0`
- 最终验证：`478 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G50 Docker Compose Foundation

- 接受 ADR-0069；`deploy/docker`（compose + Dockerfile + entrypoint）；`COMPOSE.md`
- 映射 G49 单主机拓扑；K8s/支付清算另批；版本仍 `0.2.0`
- 最终验证：`472 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G49 Production Deploy Topology

- 接受 ADR-0068；`PRODUCTION_TOPOLOGY.md` 单主机 Gateway+PostgreSQL；Runbook/Checklist 扩展
- 生产基线 `REQUIRE_JWT` + 关闭开发头；Compose/K8s/支付清算另批；版本仍 `0.2.0`
- 最终验证：`466 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G48 OIDC Discovery → JWKS Wire

- 接受 ADR-0067；`EAOS_OIDC_JWKS_WIRE` 将 Discovery `jwks_uri` 注入 JWT allowlist；显式 JWKS 优先
- 保留 G40 EAOS HS256 issuer；Bearer 路径 fail-closed；支付清算另批；无 schema 变更
- 最终验证：`461 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G47 OIDC IdP Discovery

- 接受 ADR-0066；`EAOS_OIDC_DISCOVERY` / `DISCOVERY_URL`；issuer 匹配 fail-closed；显式 endpoint 优先
- `/v1/auth/oidc/status` 暴露 discovery 与解析后端点；支付清算另批；无 schema 变更
- 最终验证：`453 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G46 JWT Denylist

- 接受 ADR-0065；`EAOS_JWT_DENYLIST_JSON` / `URL`；`jti`（可选 `iss`）命中 → `GATEWAY_JWT_REVOKED`
- 支付清算另批；无 schema 变更
- 最终验证：`446 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G45 JWT Multi-Issuer JWKS

- 接受 ADR-0064；`EAOS_JWT_ISSUERS_JSON` 多发行方 JWKS allowlist；未知 iss fail-closed
- URL JWKS `kid` 未命中时强制刷新一次；支付清算显式另批
- 最终验证：`442 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted

### 2026-07-19 — PHX-G44 Terminal Extension Signature Cryptography

- 接受 ADR-0063；`smart_terminal.signing`；activate HMAC/Ed25519 校验
- 默认 mode=off 兼容；`EAOS_EXTENSION_SIGNING_*`；无 schema 变更
- 最终验证：`438 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-M18 Marketplace Package Signature Cryptography

- 接受 ADR-0062；`signing` HMAC/Ed25519；attach/submit/publish 校验
- 默认 mode=off 兼容；REQUIRED/密钥缺失 fail-closed；无 schema 变更
- 最终验证：`435 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G43 Terminal Extension Worker Runtime

- 接受 ADR-0061；首方 `demo-worker.js`；与 G42 共享 bridge allowlist（`channel=worker`）
- UI Start worker → 宿主映射 `invoke_extension_action`；CSP 仍覆盖 `/terminal/extensions/`
- 最终验证：`431 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted

### 2026-07-19 — PHX-G42 Terminal Extension iframe + CSP

- 接受 ADR-0060；首方 demo-panel；sandbox iframe；postMessage 桥接到既有 invoke
- Gateway 对 `/terminal/extensions/` 附加严格 CSP；`executed` 仍为 false
- 最终验证：`428 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted

### 2026-07-19 — PHX-G41 Terminal Extension SQL Persistence

- 接受 ADR-0059；`kernel.terminal_extensions` + SQLAlchemy 仓储；Transactional 转发
- Alembic `0024_terminal_extension_sql_g41`；默认 Gateway 仍可内存；SQL 模式替换不双写
- 最终验证：`425 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G40 OIDC Authorization Code Login

- 接受 ADR-0058；Authorization Code + PKCE S256；callback 签发 EAOS HS256 JWT
- Gateway `/v1/auth/oidc/status|login|callback`；Terminal Bearer（fragment / sessionStorage）
- 最终验证：`424 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted

### 2026-07-19 — PHX-G39 Terminal Extension Host

- 接受 ADR-0057；Extension 登记/激活/撤销/声明 invoke；禁止特权能力与网络
- Gateway `/v1/terminal/extensions*`；UI Extensions 表面；无任意代码运行时
- 最终验证：`421 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted

### 2026-07-19 — PHX-E22 Event Webhook HMAC

- 接受 ADR-0056；可选 `signing_secret`；`v1` HMAC-SHA256 签名头
- Alembic `0023_event_webhook_hmac_e22`；无 secret 时兼容 E21 未签名
- 最终验证：`418 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G38 JWT JWKS / RS256

- 接受 ADR-0055；Bearer 支持 RS256 + JWKS（JSON/HTTPS URL）与 HS256 并列
- `kid` 多密钥选择；api extra 增加 `cryptography`
- 最终验证：`415 passed`（contracts）；无 schema 变更；OIDC 登录页仍延后

### 2026-07-19 — PHX-M17 Marketplace Commercial Policy

- 接受 ADR-0054 Foundation 政策：固定价 / immediate 发票 / 分成 bps / 发布方租户争议
- Alembic `0022_marketplace_m17_commercial`；Gateway 商业路由；Acquire ≠ 购买合同
- 支付清算与外部仲裁仍 fail-closed
- 最终验证：`412 passed`（contracts）；七步复核 Fully Accepted

### 2026-07-19 — PHX-G37 JWT/OIDC Trusted Context

- 接受 ADR-0053；Bearer HS256 → ExecutionContext；开发头默认保留、可强制 JWT
- 租户面拒 `eaos_platform_scope=true`；平台面仅 `/v1/platform/*`
- 最终验证：`410 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted（HS256 基础面）
- Explicit defer：OIDC 登录页 / JWKS·RS256；下一步 M17 需政策输入

### 2026-07-19 — PHX-G36 Complete Terminal UI

- 接受 ADR-0052；四表面 Operator / Approval / Admin / AI Collaboration
- Session/Preview refresh、Approval request/present、Admin 只读探针
- 最终验证：`405 passed`（contracts）；无 schema 变更；七步复核 Fully Accepted
- 同期登记：M17 商业与 G37 OIDC 已人工批准、待实现

### 2026-07-18 — PHX-E21 Event Webhook Transport

- 接受 ADR-0051；可选 `delivery_url` webhook；SSRF 基础门禁；Alembic `0021`
- 投递仍归 Event Bus outbox/retry/DLQ；签名产品化延后
- 最终验证：`402 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-E20 Permission DecisionRecorded Wiring

- 接受 ADR-0050；`evaluate` 成功后发射 `permission.decision.recorded`（摘要 payload）
- 闭合 E19 目录缺口；高基数由订阅方消化；无 Broker
- 最终验证：`398 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G35 Smart Terminal Operator Shell

- 接受 ADR-0049；`smart_terminal/ui` + Gateway `/terminal/` 静态挂载
- 壳仅消费 `/v1/terminal/*`；body 提升字段剥离；品牌 UX / Extension 仍延后
- 最终验证：`397 passed`，另有 `19 PostgreSQL passed`；技术壳 Fully Accepted

### 2026-07-18 — PHX-G34 Gateway Marketplace Technical HTTP Surface

- 接受 ADR-0048；Listing 生命周期 + acquire 薄适配；pricing 仍 fail-closed
- 最终验证：`393 passed`，另有 `19 PostgreSQL passed`；技术面 Fully Accepted

### 2026-07-18 — PHX-G32 Gateway Organization Route Completions

- 接受 ADR-0047；补齐 Enterprise/Unit/Membership 生命周期 HTTP
- 最终验证：`393 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G31 Gateway Domain Route Completions

- 接受 ADR-0046；补齐 Workflow 生命周期、Knowledge archive/share、Permission deprecate/delegate
- 最终验证：`387 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G30 Gateway Smart Terminal HTTP Surface

- 接受 ADR-0045；十路由薄适配（session/intent/preview/approval/commit）
- claimed_* 提升拒绝；high-impact 无审批仍 403；默认共享 Workflow
- 最终验证：`383 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G29 Gateway AI Runtime HTTP Surface

- 接受 ADR-0044；八路由薄适配（run/tool/memory/approval/commit）
- 默认 AI 共享 Workflow + Knowledge；非 AI subject / 无审批 commit 仍拒绝
- 最终验证：`378 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G28 Gateway Twin & Brain HTTP Surface

- 接受 ADR-0043；Twin/Brain 六路由薄适配；authorize/execute 恒 403
- 默认 Brain 注入 TwinService 为 reader；扩展 TWIN_*/BRAIN_* HTTP 映射
- 最终验证：`374 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G27 Gateway Package Platform HTTP Surface

- 接受 ADR-0042；七路由薄适配（manifest/publish/install/disable/surfaces/resolve）
- Kernel fork 拒绝经 HTTP 映射；扩展 PACKAGE_* 错误码
- 最终验证：`369 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G26 Gateway Event Bus HTTP Surface

- 接受 ADR-0041；九路由薄适配（publish/outbox/dispatch/get/replay/subscribe/stats/DLQ）
- HTTP subscribe 仅登记 no-op handler；真实 handler 仍进程内；扩展 EVENT_* HTTP 映射
- 最终验证：`365 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G25 Gateway Platform Tenant Lifecycle

- 接受 ADR-0040；新增 `derive_platform_context`（仅 `/v1/platform/*`）
- 交付 create/suspend/reactivate 租户 HTTP；租户面不可提升 platform_scope
- 最终验证：`358 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G24 Gateway Knowledge HTTP Surface

- 接受 ADR-0039；六路由薄适配（upsert/query/get/link/search/provenance）
- 默认 `KnowledgeService` 共享 gateway Permission；扩展 KNOWLEDGE_* HTTP 映射
- 最终验证：`352 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G23 Gateway Workflow HTTP Surface

- 接受 ADR-0038；六路由薄适配（definition/start/get/approve/reject/list tasks）
- 默认 `WorkflowService` 共享 gateway Permission；扩展 WORKFLOW_* HTTP 映射
- 最终验证：`346 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G22 Gateway Permission HTTP Surface

- 接受 ADR-0037；七路由薄适配（policy/grant/evaluate/explain/effective）
- Evaluate principal 固定为受信头 subject；扩展 PERMISSION_* HTTP 映射
- 最终验证：`339 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G21 Gateway Organization HTTP Surface

- 接受 ADR-0036；租户面六路由薄适配（平台租户 HTTP 延后）
- 扩展 ORG_* HTTP 错误映射与 `app.state.organization` DI
- 最终验证：`331 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G20 Gateway Identity HTTP Surface

- 接受 ADR-0035；在 G18 受信边界上交付 Identity 五路由薄适配
- 区分上下文覆盖拒绝与资源 `subject_id`；DI 注入 Identity 服务
- 最终验证：`322 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-E19 Domain Event Catalog Wiring

- 接受 ADR-0034；Permission/Workflow/Knowledge 事件名归一为 `domain.entity.action`
- 交付受信 `DomainEventEmitter` 与同 UoW `SQLAlchemyOutboxWriter`
- Organization / Permission / Workflow / Knowledge 状态变更命令同事务 enqueue（DecisionRecorded 延后）
- 最终验证：`314 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-G18 API Gateway Foundation

- 接受 ADR-0033；落点 `api/gateway`（可选 extra `noventi-eaos[api]`）
- 最小 FastAPI：health / release / adapters / context；受信头派生上下文
- 请求体安全字段提升失败关闭；Marketplace 定价 HTTP `403`
- 最终验证：`305 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-R17 EAOS Release Train

- 接受 ADR-0032；发布基线 **EAOS Phoenix Foundation `0.2.0`**
- 交付 `eaos_sdk`、`api.adapters` 契约目录、Compat/Runbook/Manifest/Checklist
- 固化 OpenAPI 11 份清单与 Alembic head `0020_marketplace_m16` 发布检查
- 最终验证：`300 passed`，另有 `19 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-M16 Marketplace Technical Foundation

- 接受 ADR-0031；用户批准启动技术骨架；商业政策仍显式延后
- 实现 Listing / Signature / Review / Publish / Revoke / Acquire
- 定价/账单/争议/分成 API 恒 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`
- 新增 Alembic `0020_marketplace_m16`、OpenAPI 3.1 与状态机
- 最终验证：`294 passed`，另有 `19 PostgreSQL passed`；技术七步复核 Accepted

### 2026-07-18 — PHX-E15 Enterprise Brain & Twin

- 接受 ADR-0030 与 PHX-E15 Architecture Gate，固定 Twin/Brain Shared Capability 落点
- 实现 Twin Snapshot（provenance/confidence）与 Brain Insight（永久 advisory）
- `authorize_from_twin` / `request_execution` 恒失败关闭，落实建议与执行权分离
- 新增 Alembic `0019_enterprise_brain_twin_e15`、OpenAPI 3.1 与状态机
- 最终验证：`285 passed`，另有 `18 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-B14 Business Package Platform

- 接受 ADR-0029 与 PHX-B14 Architecture Gate，固定 Shared Capability 落点 `eaos_platform.package`
- 实现 Manifest 注册/发布、租户安装、Surface 列表与 Action 解析
- 强制 `pkg.*` 资源类型与 Kernel fork 防护；样例包 `packages/sample_ops`
- 新增 Alembic `0018_package_platform_b14`、OpenAPI 3.1 与状态机
- 最终验证：`274 passed`，另有 `17 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-T13 Smart Terminal Foundation

- 接受 ADR-0028 与 PHX-T13 Architecture Gate，固定独立交互层落点 `smart_terminal/`
- 实现 Session、Intent、Plan Preview、Approval Presenter、Commit Receipt
- 强制上下文不可提升、审批读 Workflow、高影响双闸门与设备信任
- 新增 Alembic `0017_smart_terminal_t13`、OpenAPI 3.1 与状态机
- 最终验证：`263 passed`，另有 `16 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-A12 AI Runtime & Agent

- 接受 ADR-0027 与 PHX-A12 Architecture Gate，固定 Runtime 落点与审批桥
- 实现 Agent Run、工具声明/调用、AI Memory、RequestApproval/CommitAction
- 新增 Alembic `0016_ai_runtime_a12`、OpenAPI 3.1 与状态机
- 高影响动作复用 Workflow `verify_approved_action` 双闸门
- 最终验证：`251 passed`，另有 `15 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-P11 Event Delivery / Outbox

- 接受 ADR-0026 与 PHX-P11 Architecture Gate，固定 Outbox / Lease / DLQ
- 实现 `enqueue`、`dispatch_due`、退避重试、`replay_dead_letter` 与 delivery stats
- 新增 Alembic `0015_event_outbox_dlq`、OpenAPI 3.1 与状态机
- 保持 `publish` 同步兼容路径；可靠路径走 outbox + worker
- 最终验证：`240 passed`，另有 `14 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-K10 Knowledge Shared Capability

- 接受 ADR-0025 与 PHX-K10 Architecture Gate，固定 Shared 所有权与 Core 治理端口
- 实现 Entity / Link / Provenance / Retention / Share / 关键词 Search
- 强制 derived 标注、provenance 必填、secrets 拒绝与 archived/expired fail-closed
- 新增 Alembic `0014_knowledge_k10`、OpenAPI 3.1、状态机与事件目录
- 实现包：`eaos_platform.knowledge`；TransactionalKnowledgeService 复用 persistence foundation
- 最终验证：`229 passed`，另有 `13 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-K09 Workflow Kernel

- 接受 ADR-0024 与 PHX-K09 Architecture Gate，固定审批唯一真相源与双闸门
- 闭合 Instance/Task 乐观锁、reject 独立鉴权、escalate/cancel 守卫与 Signal 幂等收敛
- 扩展批准绑定（plan_version/scope/expires_at）、DeprecateDefinition、business_key 活跃唯一
- 实现 Task due_at 逾期 fail-closed 与 compensate → compensated 最小路径
- 新增 Alembic `0013_workflow_k09`、OpenAPI 3.1、状态机与事件目录
- 最终验证：`215 passed`，另有 `12 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-K08 Permission Kernel

- 接受 ADR-0023 与 PHX-K08 Architecture Gate，固定 Policy / Scope / Delegation / Explain
- conditions_ref、Principal eligibility 与 Explain/ListEffective 可见性失败关闭
- 实现类型化 Policy/Rule、deny-overrides、Organization Scope Resolver
- 实现 Delegation 父链、depth 递减与范围只能缩小
- 新增 Alembic `0012_permission_policy_scope`、OpenAPI 3.1、状态机与事件目录
- 最终验证：`201 passed`，另有 `11 PostgreSQL passed`；七步复核 Fully Accepted

### 2026-07-18 — PHX-K07 Organization Kernel

- 接受 ADR-0022 与 PHX-K07 Architecture Gate，固定 L0 Tenant / L0.5 Enterprise / L1 Unit / L2 Membership
- 将 Tenant 隔离边界与 Enterprise 法人/组织主体分离，CreateTenant 原子创建 primary Enterprise
- 新增 Alembic `0011_organization_enterprises`，支持已有 0010 数据安全回填
- 实现多 Enterprise 生命周期、Unit 无环森林、Membership 生命周期与 expected_version 乐观锁
- 通过 Enterprise 行级锁与 PostgreSQL 层级锁序列化生命周期、成员新增和并发 reparent
- 新增 Organization OpenAPI 3.1、状态机、领域事件目录及 PHX-K07 Acceptance
- 最终验证：`184 passed`，另有 `10 PostgreSQL passed`，零 lint；七步复核 Fully Accepted

### 2026-07-18 — PHX-G02 / PHX-A03 Compliance Closure

- 完成 BOOK00–BOOK23 二次宪法合规、交叉引用与最终只读复核，结论 Fully Compliant
- 统一 24 本宪法为 EAOS Charter v2.1 生效态，并关闭 PHX-001 实施阶段混写
- 收敛风险 taxonomy、Enterprise Brain、Smart Terminal/UI、AI taxonomy 与 BOOK22 工程顺序
- 明确 Knowledge 与 Event Bus 的 Shared Platform Capability 唯一所有权及兼容路径
- 统一 Roadmap v3 编号，旧编号仅保留于明确标注的历史记录
- 新增 Second-Pass Compliance Report 与 PHX-A03 Acceptance
- 宪法文档契约测试 8/8、完整回归 163/163 通过；项目焦点转入 PHX-K07

### 2026-07-18 — Project Phoenix Constitutional Convergence

- 完成 BOOK00–BOOK22 全量只读 Constitution Conformance Review
- 人工批准 Constitutional Kernel/Core Kernel 双层解释、AI 四层 taxonomy 与 Smart Terminal 独立交互层定位
- 修订 BOOK03/15/17/19/22，解决 Kernel 拓扑、AI 主体与术语冲突
- 新增 BOOK XXIII Smart Terminal Constitution
- 新增 ADR-0021、Smart Terminal Blueprint 与 Roadmap v3
- 启动 BOOK XXIII 二次宪法合规审查

### 2026-07-18 — PHX-006 Identity Kernel Accepted

- 人工批准 PHX-006 技术退出标准
- Identity Session、Credential、Governor、Assignment、Profile、Org L2、OpenAPI 与状态机全部收敛
- 验收基线：`160 passed`，包含 5 项真实 PostgreSQL 集成契约，零 lint 错误
- 当时项目焦点转入旧编号 PHX-007；该路线现已由 Roadmap v3 的 PHX-G02 → PHX-A03 → PHX-K07 取代

### 2026-07-18 — PHX-006 Identity IDL and State Machines

- 接受 ADR-0020，以 OpenAPI 3.1 YAML 作为 Identity HTTP 契约真相源
- 覆盖 Subject、AI Profile、Credential、Session、Governor、Assignment 与协调式改派
- tenant/subject/session/platform scope 仅由受信认证边界派生
- 新增六类 Identity 状态机规范与 OpenAPI 自动契约
- 当前结果：`160 passed`；PHX-006 技术退出标准完成

### 2026-07-18 — PHX-006 Identity ↔ Organization L2

- 接受 ADR-0019，Org.AddMembership 通过 Identity eligibility port 失败关闭
- 租户主体要求 tenant_id 匹配；AI 要求同租户 active assignment
- 实现 TransactionalIdentityOrganizationCoordinator
- 跨租户 AI 改派在同一 UoW 结束旧 active memberships
- 当前结果：`155 passed`，包含 5 项真实 PostgreSQL 集成契约

### 2026-07-18 — PHX-006 AI Profile Persistence

- 接受 ADR-0018，采用独立 `ai_employee_profiles` 一对一模型
- RegisterAIEmployee 在同一事务持久化 Subject 与 Profile
- Capability / owner policy 仅保存策略引用，授权继续由 Permission 判定
- 实现 Governor-only 更新与 expected_version 乐观锁
- 新增 Alembic `0010` 与 PostgreSQL round-trip 契约
- 当前结果：`152 passed`，零 lint 错误

### 2026-07-18 — PHX-006 AI Assignment Semantics

- 接受 ADR-0017：AI Employee 全局最多一个 active tenant assignment
- INHERIT 仅记录 predecessor 管理谱系，不复制权限、知识、记忆或会话
- ARCHIVE 不再要求目标租户；非法多活状态失败关闭
- 新增 Alembic `0009` 与数据库全局 active 唯一约束
- 当前结果：`150 passed`，包含 4 项真实 PostgreSQL 集成契约

### 2026-07-18 — PHX-006 Platform Identity Governor Persistence

- 接受 ADR-0016，采用独立 Governor 授权历史表
- Bootstrap UUID 仅在无持久 Governor 时引导首条授权
- 首条授权后数据库成为唯一 Identity 治理真相源
- 实现 Grant/Revoke、active 唯一约束与最后 Governor 防锁死
- 新增 Alembic `0008`，通过服务重组与真实 PostgreSQL 验证
- 当前结果：`148 passed`，零 lint 错误

### 2026-07-18 — PHX-006 Identity Credential Lifecycle

- 接受 ADR-0015，移除 CreateSession 对裸 `auth_factors_ok` 的信任
- 新增 ValidateCredential / RevokeCredential 非秘密视图与生命周期
- CreateSession 强制绑定 active、未过期且匹配 tenant/subject 的 Credential
- 撤销 Credential 仅阻止新 Session，不级联终止既有 Session
- 新增 Alembic `0007` 与 Session credential_id 可追溯绑定
- 当前结果：`146 passed`（含真实 PostgreSQL），零 lint 错误

### 2026-07-18 — PHX-006 Identity Session Boundary Closure

- 接受 ADR-0014，Identity 返回具体会话错误，Runtime 统一映射 `CTX_INVALID`
- 实现 `Identity.ValidateSession` 与 TransactionalIdentity 接线
- 校验 session 的租户、主体、撤销与过期状态
- Runtime 对携带 `session_id` 的执行强制注入 SessionValidator
- 覆盖内存、SQLite 事务与真实 PostgreSQL Create/Validate/Revoke
- 当前结果：`143 passed`，零 lint 错误

### 2026-07-18 — PHX-005 Runtime Foundation

- 接受 ADR-0013，锁定 Runtime 与 Kernel、API、AI、异步 worker 边界
- 发布 Runtime 接口、契约测试计划与 PHX-005 验收清单
- 实现入站上下文构造、安全传播、版本化 JSON 快照与恢复
- 实现显式 RuntimeExecutor 和 allowlist ObservabilityBinding
- Runtime → Permission Kernel 探针证明上下文原样贯通
- 当前结果：`138 passed`（含真实 PostgreSQL），零 lint 错误
- PHX-005 Foundation 获人工批准并正式完成

### 2026-07-18 — PHX-004 真实 PostgreSQL 技术验收

- 部署隔离 PostgreSQL 17 便携实例与专用 `eaos_test`
- 通过 `base → 0006 → base` 迁移链及四项 PostgreSQL 集成契约
- 发现并修复 Workflow History 在 Instance 之前 flush 的外键冲突
- 发现并修复 Event Delivery 在 Event 之前 flush 的外键冲突
- 完整结果：`123 passed`，零跳过、零 lint 错误
- PHX-004 技术验收通过并获人工批准，里程碑正式完成

### 2026-07-18 — PHX-004 Foundation 条件验收

- 新增显式 PHX-004 退出清单，状态为“条件通过”
- 在事务型 Workflow 补齐 W-04/W-05 AI 人工审批与绑定契约
- 增加事务型 Organization ↔ Permission L2 边界契约
- PostgreSQL 套件扩展至 Organization、Permission、Workflow 与 Event 往返
- 清理 Kernel、数据库标准、测试计划与项目状态中的陈旧描述
- 当前结果：`119 passed, 1 PostgreSQL skipped`；最终退出等待 T-0069 与人工确认

### 2026-07-18 — PHX-004 Transactional Event Bus

- 新增 Event / Subscription Metadata / Delivery Attempt ORM 与 Alembic `0006`
- 将不可持久化 Python handler 分离到进程内 `EventHandlerRegistry`
- 实现租户绑定 Event Repository 与 TransactionalEventBus
- Event、Permission Decision、Audit 与投递状态共享事务
- 失败尝试持久化并保持受控重放资格；明确 at-least-once 边界
- 当前结果：`116 passed, 1 PostgreSQL skipped`，零 lint 错误

### 2026-07-18 — PHX-004 Transactional Workflow

- 新增 Workflow 五表 ORM 与 Alembic `0005`
- 实现租户绑定 Repository、显式状态 save 与 Signal Receipt
- Workflow 与 Permission 求值、Decision、Audit 共享事务
- Permission 拒绝保留决策审计且不创建 Workflow 副作用
- 修复 PostgreSQL 63 字符外键名称上限
- 当前结果：`112 passed, 1 PostgreSQL skipped`，零 lint 错误

### 2026-07-18 — PHX-004 Transactional Permission

- 新增 Grant / PermissionDecision ORM 与 Alembic `0004`
- Grant actions 使用 PostgreSQL JSONB，并约束等价活跃授权唯一
- 实现租户绑定 Permission Repository 与事务型 Service
- 默认拒绝、Allow/Deny 决策和 Audit 原子持久化
- 当前结果：`108 passed, 1 PostgreSQL skipped`，零 lint 错误

### 2026-07-18 — PHX-004 Transactional Organization

- 新增 Tenant / OrganizationUnit / Membership ORM 与 Alembic `0003`
- 通过复合外键在数据库层阻断跨租户父单元与成员关系
- 实现租户绑定 Organization Repository 与事务型 Service
- Tenant 状态、Unit、Membership 与 Audit 原子持久化
- 当前结果：`103 passed, 1 PostgreSQL skipped`，零 lint 错误

### 2026-07-18 — PHX-004 Platform Identity Governor

- 为 RegisterAIEmployee 与跨租户 ReassignAI 增加显式 Governor 集合
- `platform_scope=True` 不再自动等同于 Identity 治理权限
- TransactionalIdentityService 显式注入 Governor
- 未授权操作返回 `PERMISSION_DENIED` 且不产生 Domain/Audit 残留
- 当前结果：`98 passed, 1 PostgreSQL skipped`，零 lint 错误

### 2026-07-18 — PHX-004 PostgreSQL Integration Harness

- 新增真实 PostgreSQL 破坏性集成测试套件
- 强制 `postgresql+psycopg` 且数据库名以 `eaos_test` 开头
- 覆盖 Alembic upgrade/downgrade、事务型 Identity/Audit 与 partial unique index
- 当前机器无 Docker/PostgreSQL 工具且未配置测试 URL，因此未伪装为已验证
- 当前结果：`96 passed, 1 skipped`，零 lint 错误

### 2026-07-18 — PHX-004 Transactional Identity

- 新增 `TransactionalIdentityService`，每个调用独占 Session 与 Unit of Work
- Identity Domain 写入与 AuditEvent 在同一事务中提交
- 业务失败、数据库冲突和 SQL 错误统一回滚
- 跨租户 AI 改派收紧为平台上下文
- 完整测试结果：`96 passed`，零 lint 错误

### 2026-07-18 — PHX-004 Shared Audit / Identity SQL Repositories

- 实现租户绑定的 SQLAlchemy Identity Repository 与 AuditLog
- 补充 Subject、Session、Assignment 显式 `save_*` 持久化端口
- 全局 AI 对租户可见但禁止租户级修改
- 跨租户查询隐藏，跨租户写入返回稳定错误码
- 数据库读取时间统一恢复为 UTC
- 完整测试结果：`89 passed`，零 lint 错误

### 2026-07-18 — PHX-004 SQLAlchemy Unit of Work

- 实现 PostgreSQL Engine 与显式 Session Factory
- 实现 SQLAlchemy Unit of Work 并满足共享端口
- 未显式提交、异常和提交失败路径均 fail-closed 回滚
- 禁止嵌套进入及提交后继续使用 Session
- 完整测试结果：`83 passed`，零 lint 错误

### 2026-07-18 — PHX-004 Shared Audit / Identity ORM

- 新增独立 SQLAlchemy 映射，Domain Model 保持无 ORM 依赖
- 创建 `kernel` schema 的 Audit 与 Identity 六张表
- 加入租户、状态、外键、外部引用和活跃 AI 派驻唯一性约束
- 新增 Alembic `0002_shared_audit_identity`
- 修正 CheckConstraint 命名约定重复前缀问题
- 完整测试结果：`77 passed`，离线迁移编译成功，零 lint 错误

### 2026-07-18 — PHX-004 SQL Foundation

- 添加 SQLAlchemy 2、Alembic 与 psycopg 可选依赖
- 建立统一 metadata、Declarative Base 与确定性约束命名
- 创建 Alembic `0001_kernel_baseline` 空基线
- 数据库 URL 仅允许 `postgresql+psycopg` 且缺失时 fail-closed
- 完整测试结果：`69 passed`，Alembic 修订链有效，零 lint 错误

### 2026-07-18 — PHX-004 Persistence Ports

- 为 Identity、Organization、Permission、Workflow、Event 定义 Repository Protocol
- AuditLog 与 Service 从具体内存实现解耦
- 新增 Unit of Work Protocol 及内存生命周期适配器
- 明确生产 Repository 查询层的租户强制边界
- 完整测试结果：`63 passed`，零 lint 错误

### 2026-07-18 — PHX-004 持久化技术选型

- 接受 ADR-0012：PostgreSQL + SQLAlchemy 2 + Alembic
- Domain Model 与 ORM Model 保持分离
- Service 依赖 Repository / Unit of Work Protocol
- 明确租户条件、事务、outbox 与迁移边界

### 2026-07-18 — PHX-004 Workflow 幂等与 Event 投递决策

- Workflow 定义在 `(tenant scope, name, version)` 范围内强制唯一
- Signal 强制幂等键；相同请求重试返回首次结果，不重复推进状态
- 同一幂等键被不同请求复用时 fail-closed
- 接受 ADR-0011：append-only、transactional outbox、at-least-once 与 DLQ
- 完整测试结果：`54 passed`，零 lint 错误

### 2026-07-18 — PHX-004 Event Bus 信封切片

- 实现 `kernel/event_bus`：不可变事件信封、订阅、发布、读取与受控重放
- payload 仅允许 JSON 安全值并深度冻结
- Event 操作全部接入 Permission Kernel
- 租户绑定订阅阻止跨租户投递
- 成功投递按 `(subscriber_id, event_id)` 幂等；失败投递可重放
- 完整测试结果：`51 passed`，零 lint 错误

### 2026-07-18 — PHX-004 Workflow 与 AI 审批闸门

- 实现 `kernel/workflow` 内存状态机：定义、实例、任务、审批/拒绝、信号、升级与取消
- Workflow 所有敏感操作经 Permission Kernel 求值
- 增加 Organization ↔ Permission 集成契约，确认组织角色不隐式授予权限
- AI 高影响审批绑定目标主体、动作与资源，禁止跨 AI/动作/资源复用
- 完整测试结果：`42 passed`，零 lint 错误
- 未引入 FastAPI/SQL；未修改遗留仓库

### 2026-07-18 — PHX-004 Organization / Permission 切片

- 实现 `kernel/organization`：租户、组织单元、成员关系与跨租户防护
- 实现 `kernel/permission`：Grant、Revoke、Evaluate 默认拒绝、Explain 与决策审计
- 新增 Organization / Permission 契约测试
- 增加显式平台治理主体与 Grant 管理主体白名单，默认无管理权限
- 完整测试结果：`31 passed`
- 新增 `.gitignore` 并清理本地 `*.egg-info` 生成物
- 未引入 FastAPI/SQL；未修改遗留仓库

### 2026-07-18 — PHX-004 首个可执行切片

- 新增 `pyproject.toml`，包名 `noventi-eaos`
- 实现 `kernel/shared`：ExecutionContext、ErrorCode、KernelResult、InMemoryAuditLog
- 实现 `kernel/identity`：IdentityService 垂直切片（内存仓储，ADR-0010）
- 契约测试：`tests/contracts/test_execution_context.py`、`test_identity_service.py`
- `pytest` 全部通过
- 未引入 FastAPI/SQL；未修改遗留仓库

### 2026-07-18 — PHX-004 契约层补齐

- ADR-0009：逻辑多租户 + 自有持久化模型（不映射遗留表）
- 发布 `ERROR_CODES.md` 错误码总表
- 发布 `EXECUTION_CONTEXT.md` 执行上下文契约
- 更新 `kernel/shared` 文档锚点
- 仍无实现代码；遗留仓库未改动

### 2026-07-18 — PHX-004 启动（Foundation 文档 + 骨架）

- 发布 `KERNEL_DATA_MODEL.md`（Identity/Org/Permission 概念模型，无 SQL）
- 发布 Organization / Workflow 接口细化
- 发布 `KERNEL_CONTRACT_TEST_PLAN.md`
- 建立 `kernel/{shared,identity,organization,permission,workflow}/` README 骨架
- 建立 `tests/contracts/` 占位目录
- 仍无 Python / FastAPI / SQL 实现；遗留仓库未改动

### 2026-07-18 — PHX-001 完成 + 接口/ADR 就绪

- BOOK00–BOOK22 全部充实为工作宪章基线
- 新增 ADR-0006 事件信封、ADR-0007 租户隔离、ADR-0008 AI 人工审批
- 新增 Identity / Permission 接口细化规格
- PHX-004 进入门槛大部分已满足；下一步为数据模型草案与契约测试计划
- 仍无业务实现代码；遗留仓库未改动

### 2026-07-18 — PHX-001（宪法正文推进 + 接口大纲）

- 充实 BOOK00 / BOOK01 / BOOK19 为生效基线
- 充实 BOOK03 / BOOK04 / BOOK05 / BOOK10 / BOOK13 / BOOK14 / BOOK17
- 发布 `docs/architecture/KERNEL_INTERFACES.md`（Kernel 接口大纲，无实现代码）
- 遗留仓库仅只读参考，未做任何修改

### 2026-07-18 — PHX-001（结构初始化）

- 在 `docs/constitution/` 创建 BOOK00–BOOK22 占位书目与索引

### 2026-07-18 — PHX-002 / PHX-003（完成）

- 充实 `docs/blueprint/` 全部蓝图（原则、边界、概念模型、交叉引用）
- 充实 `docs/architecture/`：愿景、架构总览、系统原则
- 充实 `docs/standards/`：编码/数据库/API/命名/事件/AI/结构/Git 标准基线
- 更新项目状态：PHX-002、PHX-003 标记为完成
- 仍无 Python / FastAPI / SQL / 业务模块实现

### 2026-07-18 — PHX-000（完成）

- Established `NOVENTI-EAOS` as the sole writable development repository
- Declared Legacy `EZAM_CRM-9.0` / `EZAM_CRM - 9.0` permanently read-only
- Initialized top-level platform directories with README files
- Initialized `docs/constitution`, `docs/blueprint`, `docs/standards`, `docs/architecture`, `docs/decisions`, `docs/project`
- Created project governance documents
- Created Architecture Blueprint placeholders
- Created Development Standards placeholders
- Created architecture vision/principles placeholders
- Published `DIRECTORY_TREE.md` and `MIGRATION_STATUS.md`
- Documented inadvertent PHX files previously written under Legacy (not moved; Legacy untouched)

## Future Expansion

Append dated entries at every milestone and logical checkpoint.

## Related Documents

- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)
- [MIGRATION_STATUS.md](MIGRATION_STATUS.md)
