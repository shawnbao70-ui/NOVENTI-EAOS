# 关键写路由服务端鉴权覆盖矩阵

**Evidence strength:** Strong for sampled canonical handlers and methods; production proxy/alternate startup UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页以“改变业务事实的 HTTP handler”为 command surface，核对 authenticated principal、module/action RBAC、对象范围、状态前置、CSRF 与审计。Legacy checker 被调用时 default-deny，但 route 调用是 opt-in；UI gate 不计为 server coverage。

## 2. Coverage Matrix

| Domain / command | Method | Server RBAC | Object/state | Audit actor | Coverage |
|---|---|---|---|---|---|
| Quote approve | POST | Quotes edit | quote exists + Human Confirm | session actor | Strong |
| Quote status | GET | None | enum only | none | Critical gap |
| Quote→SO | GET | None | exists + one-SO app guard | none | Critical gap |
| Create SO POST | POST→GET | None | delegated | none | Critical gap |
| SO status | GET | Sales Orders edit | Open redirects Approve; other weak | none | Partial |
| SO approve | POST | Sales Orders edit | line/status + Human Confirm | session actor | Strong |
| SO→DO create | GET | None | SO exists | none | Critical gap |
| SO→DO convert | GET | Sales Orders edit in service | SO exists | none | Partial |
| DO ship | POST | Delivery Orders edit | open + stock + Human Confirm | actor passed | Strong |
| DO complete/reopen | GET | Delivery Orders edit in service | stage checks | no operation log | Partial |
| Inventory adjust | POST | Inventory edit | inventory exists + numeric | weak/no reason authority | Strong RBAC |
| Inventory delete | GET | Inventory delete | stock guard | none | Partial |
| Receipt create | GET | Receipts add | SO exists/amount path | session username | Partial |
| DO Post AR | POST | AR add OR Delivery edit | DO + confirm + dedupe | actor passed | Strong |
| Purchase invoice create | GET | None | purchase exists | none | Critical gap |
| Expense add/approve | POST/GET | None | weak | hardcoded SYSTEM/BOSS | Critical gap |
| Approval approve/reject | GET | None | no assigned approver/Pending condition | username or absent | Critical gap |
| Customer/Product/Supplier/Purchase delete | GET | resource delete | domain guards vary | inconsistent | Partial |
| User add/edit | POST | Users add/edit | duplicate/hash | add only logs | Partial |
| User delete | GET | None | ID only | none | Critical gap |
| Commission rule/TC ledger adjuncts | mixed | inconsistent/none | weak | none | Critical gap |
| Marketing distributor CRUD | POST/GET | None | ID/existence only | none | Critical gap |
| Platform org/security/session delete | GET | None/inconsistent | ID only | none | Critical gap |
| Document file delete | GET | None | file exists | none | Critical gap |
| Knowledge attach/delete | POST/GET | `knowledge_allowed` local policy | local object checks | weak | Partial |
| Brand save/upload | POST | `can_modify_branding` | brand lock/field whitelist | actor+reason | Strong |
| Document Designer save | POST | None | template key | none | Critical gap |
| Product category/upload/application | mixed | None/inconsistent | local validation | none | Critical gap |

## 3. Business Rules

| ID | Rule |
|---|---|
| SRC-R01 | 只有 handler/service 显式调用 checker 才形成 RBAC coverage。 |
| SRC-R02 | request-less handler 无法绑定当前 principal。 |
| SRC-R03 | Template `has_permission` 不计 server coverage。 |
| SRC-R04 | Quote Approve 和 SO Approve 的 POST Type A 同时具 RBAC 与 Human Confirm。 |
| SRC-R05 | Quote status、Convert SO、Create DO 是 request-less command。 |
| SRC-R06 | `/convert_do` 是少数 service 内补 gate 的 GET command。 |
| SRC-R07 | DO Ship POST 的 server coverage 强于 Create/Complete/Reopen。 |
| SRC-R08 | Complete/Reopen 有 service RBAC/状态校验但仍为 GET。 |
| SRC-R09 | Finance 同一 router 内强 gate 与无 gate 写入口并存。 |
| SRC-R10 | Approval Center 决策未校验指定 approver、Pending 原态与 approve permission。 |
| SRC-R11 | Admin/Super Admin 对已调用 checker 的命令无条件 allow。 |
| SRC-R12 | 无 checker 的命令不是 admin-only，而是 permission matrix 不参与。 |
| SRC-R13 | module/action RBAC 不自动提供 owner/tenant scope。 |
| SRC-R14 | CSRF 全局覆盖 unsafe methods，但 GET command 被当作 safe。 |
| SRC-R15 | state/existence guard 是业务校验，不等于主体授权。 |
| SRC-R16 | actor 参数只有来自 authenticated request 才具审计价值。 |
| SRC-R17 | hardcoded `SYSTEM`/`BOSS` 不能证明实际操作者。 |
| SRC-R18 | canonical/residual 同 path 可有不同 gate，标准注册赢家决定实际 coverage。 |
| SRC-R19 | API `routes.py` 与 page routers 是独立 surface，不继承页面 gate。 |
| SRC-R20 | EAOS command handler 必须默认要求 principal、policy、scope、intent 和 audit。 |
| SRC-R21 | Marketing 与 Platform residual 写面存在 principal-blind handlers。 |
| SRC-R22 | Brand save policy/audit 不传播到 Document Designer save。 |
| SRC-R23 | Knowledge 的 `knowledge_allowed` 是局部 policy，不保护 file-library 邻接面。 |
| SRC-R24 | Commission Center view gate 不保护 rule/test commission writes。 |
| SRC-R25 | Product 主记录 RBAC 不代表 category/upload/application 子面受同策略保护。 |

## 4. Process

1. 识别写副作用，而非只按 HTTP method。
2. 定位标准 bootstrap 的 canonical owner。
3. 检查 route 是否接收 Request、login/RBAC 是否 route 或 service 执行。
4. 分离 module action、object scope、source state、Human Confirm、CSRF、audit。
5. 将仅 UI gate、仅存在性检查和 hardcoded actor 标为未覆盖。

## 5. Validation

| ID | Validation | Legacy |
|---|---|---|
| SRC-V01 | command 必须持有 authenticated principal | Missing/inconsistent |
| SRC-V02 | command 必须有 server module/action policy | Missing/inconsistent |
| SRC-V03 | command 必须校验 owner/tenant object scope | Missing/inconsistent |
| SRC-V04 | command 必须校验合法 source state | Partial |
| SRC-V05 | command 不得使用 GET | Violated broadly |
| SRC-V06 | unsafe method 必须 CSRF | Global for POST etc. |
| SRC-V07 | sensitive command 要 Human Confirm | Selected Type A only |
| SRC-V08 | actor 必须源自 session principal | Missing/inconsistent |
| SRC-V09 | override 必须 reason/audit | Missing |
| SRC-V10 | duplicate/replay 必须 idempotent | Partial |
| SRC-V11 | canonical/residual policy 必须一致 | Missing |
| SRC-V12 | denial 必须统一 401/403 | Inconsistent |

## 6. Data Semantics

| Concept | Meaning |
|---|---|
| server coverage | endpoint runtime authorization, not UI visibility |
| principal | authenticated request subject |
| module/action | role permission matrix key |
| object scope | authorization over a specific ID |
| tenant scope | tenant-bound query/update predicate |
| source-state guard | allowed transition origin |
| Human Confirm | explicit intent, not RBAC |
| CSRF | cross-site request intent for unsafe methods |
| request-less handler | command without principal context |
| service gate | authorization inside service |
| canonical owner | standard first registered route |
| residual alias | fallback legacy route |
| hardcoded actor | label not tied to authenticated subject |
| audit record | durable actor/action/target/time/reason |
| partial coverage | some of RBAC/state/method/audit present |
| critical gap | business write without server RBAC |

## 7. State Vocabulary

| State | Meaning |
|---|---|
| Strong | principal + RBAC + meaningful command guards |
| Partial | RBAC or state exists but HTTP/scope/audit incomplete |
| Critical gap | no server authorization on sensitive write |
| UI-only | hidden control with reachable endpoint |
| service-only | route delegates permission to a service |

## 8. UNKNOWN + 已查路径

| UNKNOWN | 已查路径 |
|---|---|
| reverse proxy path policy | deployment docs/config |
| alternate startup route winners | bootstrap/app entrypoints/reports |
| all manifest APIs permission dependency | apps/*/routes.py, core/router |
| production role/module rows | runtime seed/schema only |
| DB triggers/RLS adding authorization | database migrations/adapters |
| audit sink deployment completeness | operation_logs/audit services/reports |
| CSRF tokens present on every legacy form | middleware/templates sampling |
| webhooks/background jobs command authorization | apps/jobs/integrations |
| actual anonymous reachability | static code cannot prove network boundary |
| Permission Assessment score currency vs live routes | `docs/reports/Permission_Assessment_Report.md` (scores not runtime proof) |
| Broken/orphan write route residual winners in prod | `docs/reports/Broken_Route_Report.md`, `ROUTE_OWNER_REPORT.md`, bootstrap |

## 9. Evidence Table

| Read-only path | Evidence |
|---|---|
| `core/permission/checker.py` | opt-in RBAC and bypass |
| `core/security/csrf.py` | GET safe classification |
| `core/security/middleware.py` | no global resource RBAC |
| `apps/quotation/router.py` | approve/status coverage contrast |
| `apps/sales/router.py` | convert/status/create DO |
| `apps/inventory/router.py` | ship/complete/reopen/adjust |
| `apps/inventory/services.py` | service gates/state checks |
| `apps/finance/router.py` | mixed finance coverage |
| `apps/approval/router.py` | ungated decisions |
| `core/auth/routes.py` | user write inconsistencies |
| `apps/customer/router.py` | resource delete pattern |
| `apps/product/router.py` | GET delete with RBAC |
| `apps/supplier/router.py` | GET delete with RBAC |
| `apps/procurement/router.py` | receive/delete GET |
| `apps/sales/v14_residual.py` | commission surfaces |
| `apps/marketing/v14_residual.py` | distributor CRUD gaps |
| `apps/platform/org_pages.py` | organization delete gaps |
| `apps/platform/v14_residual.py` | security/session/tree mutations |
| `apps/document_center/knowledge_pages.py` | local knowledge policy |
| `apps/document_center/v14_residual.py` | file delete gap |
| `apps/brand_center/v14_residual.py` | brand vs designer policy split |
| `bootstrap/v14_residual.py` | route duplicate winner |
| `docs/knowledge/legacy-extract/permission-surface-deepen/ui_vs_server_rbac.md` | UI/server cross-reference |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | risk authority cross-reference |
| `docs/reports/Permission_Assessment_Report.md` | legacy report: data/API/field tables unused; 12/39 routers lack checks |
| `docs/reports/ROUTE_OWNER_REPORT.md` | route-owner inventory; permission lambda not global gate |
| `runtime/v14/legacy_support.py` | role_permissions/operation_logs schema seed; not route enforcement |
| `templates/` (sampled domain pages) | UI has_permission / confirm only; not server coverage |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
