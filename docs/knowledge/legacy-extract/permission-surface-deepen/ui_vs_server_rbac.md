# UI 可见性与服务端 RBAC（UI vs Server RBAC）— Legacy Knowledge

**Evidence strength:** Strong for template/router checks; deployment-wide middleware remains UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页比较按钮/菜单 `has_permission` 与实际 router/service gate。Legacy 权限执行不是默认覆盖：模板隐藏、浏览器 confirm、Type A Human Confirm 均不能替代服务端授权。部分路径两层一致，部分只在 UI 隐藏，另有服务端检查但仍使用危险 GET。

交叉引用 `../risk-catalog/permission_holes.md` 与 `../platform-obs/identity_obs.md`，不重写其权威正文。

## 2. Surface Matrix

| Action | UI gate | Server gate | Result |
|--------|---------|-------------|--------|
| Quote Approve POST | Quotes edit | Quotes edit | Aligned |
| Quote status GET | Quotes edit button/menu | None on route | UI-only hole |
| Quote→SO Convert GET | Sales Orders add | None | UI-only hole |
| New/Create SO | entry may be menu-limited | no request/gate | Server hole |
| SO status GET | Sales Orders edit | Sales Orders edit | RBAC aligned, HTTP unsafe |
| SO Approve POST | Sales Orders edit | Sales Orders edit | Aligned |
| SO→DO `/create_do` | UI edit visibility | None | UI-only hole |
| SO→DO `/convert_do` | often Sales edit context | service checks Sales Orders edit | Server gate exists |
| DO Ship POST | Delivery Orders edit | Delivery Orders edit | Aligned |
| DO Complete/Reopen GET | Delivery Orders edit | service checks edit | RBAC aligned, HTTP unsafe |
| Inventory Adjust POST | Inventory edit | Inventory edit | Aligned |
| DO Post AR POST | AR add / Delivery edit | same OR gate | Aligned |
| Receipt create GET | Receipts add | router checks | RBAC aligned, HTTP unsafe |
| Approval approve/reject GET | confirm link | no RBAC/approver gate | Critical hole |
| Commission Center | Commission Center view | explicit residual gate | gate may miss DB `Commission` row |
| TC Ledger / periods / add rule | menu-limited | no explicit route gate | deep-link read/write hole |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| UVS-R1 | Template `has_permission` 只控制渲染 | 直链仍需 server gate |
| UVS-R2 | Browser confirm 只表达前端意图 | 可绕过/重放 |
| UVS-R3 | Quote Approve GET/POST 分别 view/edit | 服务端执行明确 |
| UVS-R4 | Quote status route 不接 request | 无法校验当前主体 |
| UVS-R5 | Convert SO route 不接 request | UI Sales add 不传递到服务端 |
| UVS-R6 | Create Sales Order POST 不接 request | 只重定向 Convert |
| UVS-R7 | `/create_do/{so_id}` 不接 request | 无 route RBAC/owner gate |
| UVS-R8 | `/convert_do/{so_id}` 把 request 交给 service | service 检查 Sales Orders edit |
| UVS-R9 | SO status 具 edit gate | 但非 Open 可 GET 直写任意字符串 |
| UVS-R10 | Open 状态被重定向 Type A Approve | 局部收紧，不覆盖其他值 |
| UVS-R11 | DO Ship Type A GET view / POST edit | Human Confirm 不替代 edit |
| UVS-R12 | Complete/Reopen service 内再查 Delivery edit | 有 RBAC 仍是 GET mutation |
| UVS-R13 | Inventory Adjust 页面与 POST 都查 edit | UI/Server 一致 |
| UVS-R14 | Post AR 允许 AR add 或 Delivery edit | 跨模块 OR policy |
| UVS-R15 | Receipt create route 有 Receipts add | 仍使用 GET 写入 |
| UVS-R16 | Approval approve/reject route 无指定 approver 校验 | 中心审批可直链决策 |
| UVS-R17 | 列表 owner filter 不自动传播到详情/action | 对象级 IDOR 风险 |
| UVS-R18 | Admin/Super Admin 通过 checker 全放行 | 即使 permission row 拒绝 |
| UVS-R19 | 模块 aliases 可能让另一名称的 row 生效 | UI/route 字符串需同 checker |
| UVS-R20 | 没有统一“mutation 必须授权”middleware 证据 | 每条 route 自愿调用 |
| UVS-R21 | Server gate 与安全 HTTP method 是两项独立要求 | 有 RBAC 的 GET 仍危险 |
| UVS-R22 | EAOS 不得将按钮不可见视为 deny | 必须以命令端授权为准 |
| UVS-R23 | Commission Center 有 route gate，而 TC Ledger/period/rule 邻接面无 gate | 同域策略分裂 |
| UVS-R24 | DB seed `Commission` 与 gate `Commission Center` 未见 alias | matrix row 与 runtime key 漂移 |

## 4. Process

1. Template 根据 session/request 调用 `has_permission`，决定按钮/字段可见。
2. 用户可无视模板直接访问已知 URL。
3. Router 若显式调用 checker，则按当前 user role/module/action 判定。
4. Router 无调用时，service 通常只做业务校验；除少数 legacy service 内 gate 外不补权限。
5. Admin/Super Admin 在 checker 入口直接允许。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| UVS-V1 | 每个 mutation 必须有 server principal | Missing/inconsistent |
| UVS-V2 | UI 与 server module/action 必须一致 | Partial |
| UVS-V3 | 所有 GET 必须只读 | Violated |
| UVS-V4 | owner/tenant scope 必须在 get/update SQL | Missing/inconsistent |
| UVS-V5 | Quote Convert 需 Sales Orders add | Missing server-side |
| UVS-V6 | DO create 需 Sales Orders edit/add | Missing on `/create_do` |
| UVS-V7 | Approval decision 需 approver+Pending | Missing |
| UVS-V8 | Human Confirm 必须叠加 RBAC | Implemented on selected Type A |
| UVS-V9 | menu visibility 必须非安全边界 | Semantic guard only |
| UVS-V10 | canonical/residual aliases 必须同 policy | Missing/inconsistent |
| UVS-V11 | unauthorized 应统一 403 | Inconsistent HTML/redirect/dict |
| UVS-V12 | audit actor 必须来自 authenticated principal | Missing on request-less handlers |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| `has_permission` in template | UI visibility decision |
| `has_permission` in router | request-time RBAC gate |
| service business guard | existence/state/amount check，非授权 |
| browser confirm | client prompt |
| `human_confirm` | Type A intent value |
| session username | current principal input |
| users.role | runtime role source |
| role_permissions | role×module action matrix |
| module alias | alternate permission row lookup |
| owner filter | list data scope, not universal object policy |
| request-less handler | cannot call current-principal checker |
| GET mutation | unsafe method independent of RBAC |
| Permission Denied HTML | local denial response |
| redirect | may hide guard hit/failure |
| Admin bypass | privileged role unconditional allow |
| canonical route | standard first registered handler |
| Commission / Commission Center | 未被 checker alias 统一的权限模块名 |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| UI-only gate | button hidden, endpoint unprotected |
| aligned | UI and server both check same action |
| server-only | endpoint checks despite UI ambiguity |
| unsafe GET | authorized or unauthorized mutation by GET |
| object-scope hole | module permission without owner/tenant object check |
| privileged bypass | Admin/Super Admin allow all |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| reverse proxy 是否额外保护具体 routes | deployment/proxy docs、apps routers |
| global auth middleware 是否拦匿名请求 | core auth/session/middleware/bootstrap |
| CSRF middleware 对 GET/POST 覆盖 | core security/auth、templates |
| actual route table 在替代启动方式的 owner | bootstrap/entrypoints/reports |
| Manager 的对象级访问政策 | router owner filters/services |
| tenant scope 是否由 DB 自动强制 | tenant helpers/repositories |
| TC Ledger 深链的生产可达性 | sales residual/menu/bootstrap |
| production DB 是否存在 Commission Center row | upgrade patch/runtime seed |
| API routers 是否统一依赖 permission dependency | apps/*/routes.py、core/router |
| browser prefetch/caching 的实际配置 | templates/proxy/browser config |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `core/permission/checker.py` | central checker、aliases、bypass |
| `apps/quotation/router.py` | Approve/status gates |
| `templates/quote_detail.html` | UI status/convert visibility |
| `apps/sales/router.py` | Convert/Create DO gaps、SO gates |
| `templates/sales_order_detail.html` | UI DO/status actions |
| `apps/inventory/router.py` | DO/Inventory gates |
| `apps/inventory/services.py` | legacy service-internal permission |
| `apps/finance/router.py` | Receipt/AR mixed gates |
| `apps/approval/router.py` | decision route gaps |
| `apps/sales/v14_residual.py` | TC Ledger surface |
| `templates/tc_ledger.html` | view surface |
| `database/upgrade_patch.py` | permission row sync coverage |
| `bootstrap/v14_residual.py` | route winner/filter |
| `core/auth/session.py` | principal/session |
| `docs/reports/Route_Ownership_Registry.md` | duplicate route ownership |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | EAOS 权限风险基线 |
| `docs/knowledge/legacy-extract/platform-obs/identity_obs.md` | EAOS identity 观察交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
