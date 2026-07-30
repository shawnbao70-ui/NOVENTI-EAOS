# DO 创建路由权限缺口（Convert / Create DO Route Gaps）— Legacy Knowledge

**Evidence strength:** Strong for route signatures, service gates and duplicate behavior  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

Legacy 同时暴露 `/create_do/{so_id}` 与 `/convert_do/{so_id}`。前者由 Sales canonical route 承载，模板按 `Delivery Orders.add` 隐藏，但 server handler 无 request/permission；后者由 Inventory canonical route 承载，将 request 传给 service 并检查 `Sales Orders.edit`。两条均为 GET mutation，均未统一检查 SO 状态、行项目、已存在 DO、owner/tenant 或来源唯一性。

## 2. Route Matrix

| Path | Canonical owner | Method | UI gate | Server gate | Numbering |
|------|-----------------|--------|---------|-------------|-----------|
| `/create_do/{so_id}` | `apps/sales/router.py` | GET | Delivery Orders add | None | timestamp DO |
| `/convert_do/{so_id}` | `apps/inventory/router.py` | GET | weak/legacy context | Sales Orders edit in service | `DO{so_id:04d}` |
| residual create_do | platform v14 | GET | UNKNOWN | none | timestamp |
| residual convert_do | inventory v14 | GET | UNKNOWN | Sales Orders edit | source-ID |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| CDR-R1 | `/create_do` handler 不接 request | 无法 server-check principal |
| CDR-R2 | Sales detail/list/dashboard UI 只对 Delivery Orders add 显示按钮 | UI-only policy |
| CDR-R3 | Receipt detail 也可显示 create DO 链接且未见同等 gate | 入口策略漂移 |
| CDR-R4 | `/create_do` service 只检查 SO 存在 | 不检查权限/owner/status |
| CDR-R5 | `/create_do` 复制 SO header/lines | 创建即写业务事实 |
| CDR-R6 | `/create_do` 使用秒级 DO number | 同秒碰撞风险 |
| CDR-R7 | `/convert_do` route 接收 request | 可调用 runtime checker |
| CDR-R8 | `_legacy_convert_do` 要求 Sales Orders edit | 与 UI Delivery Orders add 不同资源/action |
| CDR-R9 | `/convert_do` 使用 SO-ID-derived number | 重复调用同号 |
| CDR-R10 | 两条路径都不要求 SO Open/Approved | Draft/pending/Delivered 等政策未执行 |
| CDR-R11 | 两条路径都不要求至少一行 | 可建立空 DO |
| CDR-R12 | 两条路径都未检查已有 DO | 一 SO 可重复建 DO |
| CDR-R13 | 两条路径都未校验可交付剩余数量 | 无 partial/reservation gate |
| CDR-R14 | 两条路径创建 DO 时不扣库存 | Ship 是后续独立 gate |
| CDR-R15 | 两条路径都使用 GET mutation | 可被重放/预取/CSRF |
| CDR-R16 | browser confirm 仅出现在部分 UI | 直链不需要 confirm |
| CDR-R17 | standard bootstrap 先挂 business pages | residual 同 path 被过滤 |
| CDR-R18 | 替代启动方式的 route owner 仍 UNKNOWN | 权限可能随 owner 漂移 |
| CDR-R19 | 仅 canonical `/create_do` 写 SO status=`Delivery Created`；`/convert_do` 不写 | 双入口状态副作用漂移 |
| CDR-R20 | `/create_do` 无 idempotency key/DB source unique | 批量/重复可多 DO |
| CDR-R21 | UI `Delivery Orders.add` 与 `/convert_do` 的 `Sales Orders.edit` 不同 | 无统一 policy contract |
| CDR-R22 | EAOS 不得把 create DO 与 Ship 合并理解 | 权限和库存动作不同 |

## 4. Process

### 4.1 `/create_do`

1. 任何可达调用者给出 SO ID。
2. Router 不读取 request。
3. Service 读取 SO；不存在才 404。
4. 生成 timestamp DO，复制 header/lines。
5. 写 SO Delivery Created 并 commit。

### 4.2 `/convert_do`

1. Router 传 request+SO ID。
2. Service 检查 Sales Orders edit。
3. 读取 SO；不存在返回列表。
4. 生成 source-ID DO，复制 header/lines并 commit。
5. 不写 SO `Delivery Created`；未见 existing-DO/status/line gate。

### 4.3 Ship boundary

DO 创建不改库存；后续 V18 Ship POST 才要求 Delivery Orders edit、Human Confirm、open stage、库存充足与 ledger 防重。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| CDR-V1 | SO 必须存在 | Hard |
| CDR-V2 | `/create_do` 需 Delivery Orders add | Missing server-side |
| CDR-V3 | `/convert_do` 需 Sales Orders edit | Hard in service |
| CDR-V4 | 两路径应使用同一资源/action | Missing |
| CDR-V5 | SO 必须 Approved/Open | Missing |
| CDR-V6 | SO 必须有行 | Missing |
| CDR-V7 | 同 SO/remaining qty 不得重复 DO | Missing |
| CDR-V8 | owner/tenant scope | Missing |
| CDR-V9 | request must use POST/CSRF | Missing |
| CDR-V10 | idempotency key/DB unique source | Missing |
| CDR-V11 | DO number unique | Missing |
| CDR-V12 | line qty ≤ remaining deliverable | Missing |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| `/create_do` | Sales-owned canonical creation URL |
| `/convert_do` | Inventory-owned legacy-compatible creation URL |
| Delivery Orders add | UI visibility permission |
| Sales Orders edit | convert_do service permission |
| request-less route | no current-principal checker |
| DO header | SO party/date/amount snapshot |
| DO items | SO line snapshot |
| `so_id` | authoritative source link |
| timestamp do_no | Sales path display number |
| source-ID do_no | Inventory path display number |
| Delivery Created | 仅 `/create_do` 写入的 SO label；`/convert_do` 不写 |
| Pending/Open DO | pre-Ship state |
| Ship permission | Delivery Orders edit |
| Human Confirm | Ship intent, not DO-create authorization |
| residual owner | fallback implementation filtered in standard bootstrap |
| duplicate DO | same SO multiple delivery headers |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| create | materialize DO header/lines |
| convert | legacy name for same materialization |
| Delivery Created | SO status after DO creation |
| Open/Pending | DO eligible stage family |
| Shipped | later inventory posting |
| UI-only authorized | button visible but server unguarded |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 一 SO 多 DO 是否正式支持 partial delivery | sales/inventory/business modules/reports |
| 非标准启动 route owner | bootstrap/app entrypoints/route reports |
| Receipt detail create DO 链接是否受 outer page权限间接限制 | finance templates/router |
| batch DO JS 是否有 hidden server token | sales_orders template/router |
| tenant/owner scope 是否由 DB policy强制 | repositories/tenant helpers |
| production schema 是否有 delivery_orders.so_id unique | runtime/database migrations |
| duplicate DO 清理/merge | sales/inventory scripts/reports |
| Delivery Orders.add 与 Sales Orders.edit 的产品意图 | permission catalog/reports |
| create_do CSRF/prefetch 防护 | middleware/security/proxy |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/router.py` | request-less `/create_do` |
| `apps/sales/services.py` | create DO checks/fields |
| `apps/sales/repository.py` | DO insert/line/status |
| `templates/sales_order_detail.html` | Delivery Orders add UI gate |
| `templates/sales_orders.html` | button/batch link |
| `templates/sales_dashboard.html` | UI confirm |
| `templates/receipt_detail.html` | alternate create DO link |
| `apps/inventory/router.py` | `/convert_do` route |
| `apps/inventory/services.py` | service-internal Sales edit gate |
| `apps/inventory/v14_residual.py` | residual convert_do |
| `apps/platform/v14_residual.py` | residual create_do |
| `bootstrap/enterprise_cutover.py` | business router order |
| `bootstrap/v14_residual.py` | duplicate path filtering |
| `runtime/v14/legacy_support.py` | delivery schema/constraints |
| `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` | route ownership |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | EAOS PH-002 baseline |
| `docs/knowledge/legacy-extract/platform-obs/platform.md` | EAOS platform route observation |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
