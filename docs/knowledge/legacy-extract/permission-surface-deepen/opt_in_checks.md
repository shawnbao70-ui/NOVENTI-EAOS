# 可选式权限检查（Opt-in Checks）— Legacy Knowledge

**Evidence strength:** Strong for middleware/checker architecture and sampled route coverage  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

Legacy 有全局 session timeout、CSRF 与安全响应头，但没有已确认的全局资源授权 middleware。RBAC 依赖每个 template/router/service 显式调用 `has_permission`，因此是 opt-in enforcement。CSRF 默认覆盖 POST/PUT/PATCH/DELETE，却把 GET 视为 safe；Legacy 的 GET mutation 正好绕过此全局保护。

## 2. Enforcement Layers

| Layer | Default behavior | What it does not prove |
|-------|------------------|------------------------|
| Session middleware | session cookie available | route requires login |
| Session timeout | expires authenticated idle session | anonymous route denial |
| CSRF middleware | validates mutating HTTP methods | GET mutation intent/RBAC |
| Security headers | headers on response | resource authorization |
| `check_login` helper | returns authenticated bool | automatically invoked |
| `has_permission` helper | deny if missing principal/row | automatically invoked |
| template helper | hides controls | endpoint protected |
| router call | module/action gate | owner/tenant object scope |
| service call | occasional second gate | system-wide policy |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| OIC-R1 | checker 是普通函数，不是 FastAPI global dependency | routes must call it |
| OIC-R2 | route 无 Request 参数通常不能检查当前 user | principal-blind mutation |
| OIC-R3 | checker 缺 username/role/row 时 default deny | only if invoked |
| OIC-R4 | 未知 action 对非管理员 default deny | only if invoked |
| OIC-R5 | Admin/Super Admin 在 checker 内 default allow | privileged opt-out |
| OIC-R6 | module aliases 在 lookup 时 opt-in 使用 | 未调用 checker 则无意义 |
| OIC-R7 | CSRF SAFE_METHODS 包含 GET | GET writes bypass token |
| OIC-R8 | CSRF 对正常 POST 默认强制 | 比 RBAC 覆盖更集中 |
| OIC-R9 | `/login` 与静态资源有 CSRF exception | 不等于 RBAC exception |
| OIC-R10 | SessionTimeout 只处理已有 user_id 的 idle session | 不拒绝匿名业务 route |
| OIC-R11 | tenant context 缺失回退 default | 不构成强制 tenant authorization |
| OIC-R12 | Sales list/detail 显式 view gate | local opt-in example |
| OIC-R13 | Convert SO/Create DO 没有 route gate | adjacent opt-out example |
| OIC-R14 | Inventory 大多数 canonical routes 显式 gate | 较高局部覆盖 |
| OIC-R15 | legacy delivery methods有 service 内 gate | enforcement location漂移 |
| OIC-R16 | Approval decision routes 没有 checker | central approval not central authorization |
| OIC-R17 | Finance 同一 router 内 gated/ungated writes 并存 | module-level assumption unsafe |
| OIC-R18 | residual aliases 可与 canonical policy 不同 | route winner决定实际 guard |
| OIC-R19 | template checker 不触发 server checker | UI and server independent |
| OIC-R20 | owner filters 是 query opt-in | module permission不保证 object scope |
| OIC-R21 | `check_login` helper 也需 route显式调用 | authentication coverage需逐路由确认 |
| OIC-R22 | EAOS 要求 command/query handler 默认 deny | 禁止继承 route-by-route voluntary model |
| OIC-R23 | 多个 manifest `apps/*/routes.py` API 未接 checker/dependency | pages gate 不自动保护 JSON API |
| OIC-R24 | UX URL map 未命中时导航判断可 allow | 菜单可见性不是 server deny |
| OIC-R25 | Permission Engine/EPC metadata defer to legacy | schema/validator 不构成 enforcement |

## 4. Process

### 4.1 Protected route

Request → session/CSRF middleware → route → explicit `has_permission` → permission row/action → service → repository。

### 4.2 Unprotected GET mutation

Request → GET 被 CSRF 标为 safe → session timeout仅在已有 session时处理 → route无 checker → service写入。若不存在其他业务 guard，permission matrix完全不参与。

### 4.3 Residual collision

Bootstrap 先注册 canonical route，再收集 residual；同 method/path 的 residual 可被过滤。替代启动方式若注册顺序不同，实际 policy 可能变更。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| OIC-V1 | missing user default deny | Hard in checker |
| OIC-V2 | missing role default deny | Hard in checker |
| OIC-V3 | missing permission row default deny | Hard in checker |
| OIC-V4 | unknown action default deny | Hard non-admin |
| OIC-V5 | every business route invokes checker | Missing |
| OIC-V6 | every business route requires login | Missing/not globally proven |
| OIC-V7 | every mutation uses unsafe-method CSRF enforcement | Violated by GET writes |
| OIC-V8 | every object query scopes owner/tenant | Missing |
| OIC-V9 | canonical/residual policy parity | Missing |
| OIC-V10 | permission denial uniformly 403 | Missing |
| OIC-V11 | permission module/action belongs to catalog | Weak; string-driven |
| OIC-V12 | privileged action has separate audit/re-auth | Missing |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| opt-in check | handler explicitly invokes helper |
| default deny | checker behavior after invocation |
| global middleware | session/CSRF/headers, not RBAC |
| SAFE_METHODS | GET/HEAD/OPTIONS/TRACE excluded from CSRF |
| CSRF token | cross-site intent proof for mutating methods |
| `check_login` | authentication helper |
| `has_permission` | role-module-action helper |
| FastAPI dependency | not used as universal RBAC requirement |
| request parameter | carrier of session principal |
| request-less handler | principal-independent endpoint |
| module string | permission lookup key |
| action string | can_* mapping input |
| alias | lookup fallback names |
| owner predicate | optional object scope |
| tenant helper | optional/default-compatible data filter |
| residual route | alternate handler subject to registration |
| canonical route | route intended to win standard bootstrap |
| Permission Denied | route-local response, not centralized exception |
| manifest API | 与 pages router 分离的 JSON surface |
| URL permission map | UX navigation filter，未覆盖不是 server policy |
| defer to legacy | 新 permission scaffold 不接管 runtime checker |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| invoked | checker participates |
| omitted | no RBAC decision |
| deny-by-checker | principal/row/action fails |
| CSRF-safe | HTTP method skipped by CSRF, not semantically read-only |
| canonical | primary standard route |
| residual | legacy fallback route |
| first-match | registration order determines handler |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| deployment proxy adds auth/RBAC | deployment/config/docs |
| all routers mounted only behind login shell | app/bootstrap/router registry |
| alternative app entrypoints install same middleware | app files/bootstrap manifests |
| WebSocket/SSE authorization policy | core/routers/apps searches |
| APIs use shared permission dependency | apps/*/routes.py/core/router |
| EPC registry 是否参与 route 决策 | permission engine/schema/validators |
| tenant DB RLS in PostgreSQL profile | DB adapters/migrations/docs |
| CSRF cookie deployment behavior | security config/csrf/templates |
| residual-only startup in production | entrypoints/route reports |
| anonymous accessibility of no-gate routes in deployed app | static code cannot prove proxy/runtime |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `core/security/middleware.py` | middleware scope |
| `core/security/csrf.py` | GET safe and POST token enforcement |
| `core/security/config.py` | security settings |
| `core/auth/session.py` | auth helpers |
| `core/permission/checker.py` | opt-in checker/default behavior |
| `core/permission/module_catalog.py` | permission vocabulary |
| `app.py` | check_login wrapper/runtime assembly |
| `bootstrap/enterprise_cutover.py` | canonical registration |
| `bootstrap/v14_residual.py` | residual duplicate filtering |
| `apps/sales/router.py` | protected/unprotected adjacency |
| `apps/inventory/router.py` | route/service mixed enforcement |
| `apps/approval/router.py` | decision omission |
| `apps/finance/router.py` | mixed finance gates |
| `apps/quotation/router.py` | status omission vs approve guard |
| `apps/customer/router.py` | owner/gate examples |
| `apps/permission_center/v14_residual.py` | permission self-gate |
| `apps/sales/routes.py` | manifest API without page RBAC |
| `v15/rbac/unified.py` | URL navigation allow-default |
| `core/permission/permission_engine.py` | defer-to-legacy scaffold |
| `core/database/tenant_scope.py` | optional dual-read scope |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | EAOS risk baseline |
| `docs/knowledge/legacy-extract/platform-obs/identity_obs.md` | EAOS identity observation |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
