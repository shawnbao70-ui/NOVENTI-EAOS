# 一报价一销售订单：唯一性与锁（SO Uniqueness）— Legacy Knowledge

**Evidence strength:** Strong for application guard and schema; strong negative for database-enforced uniqueness and explicit locking  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页只回答“一报价一 SO”如何实现、并发时是否成立，以及重复记录的影响。Canonical Sales 路径在插入前按 `quote_id` 查询；运行 DDL 未观察到 `quote_id`/`so_no` UNIQUE、原子 upsert、显式 transaction begin 或 row lock。因此顺序重试通常幂等，并发请求并不具备数据库证明。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| SU-R1 | Convert 以 quote ID 为业务输入 | 无独立 conversion request ID |
| SU-R2 | quote 不存在时不创建 SO | 第一硬门 |
| SU-R3 | 插入前查询任一 `sales_orders.quote_id` | 顺序请求防重 |
| SU-R4 | 命中既有 SO 时直接返回列表 | 不返回既有 SO ID 或冲突 |
| SU-R5 | guard 是 SELECT-then-INSERT | 存在 TOCTOU window |
| SU-R6 | `sales_orders.quote_id` 未见 UNIQUE | DB 不保证一报价一单 |
| SU-R7 | `so_no` 由 quote ID 格式化生成 | 并发请求生成相同号码 |
| SU-R8 | `so_no` 未见 UNIQUE | 重号是否被部署扩展拦截 UNKNOWN |
| SU-R9 | 未见 `SELECT FOR UPDATE`、advisory lock 或原子 upsert | 无显式串行化 |
| SU-R10 | 未见 idempotency key/convert attempt 表 | 重放无法按请求去重 |
| SU-R11 | Convert 是 GET mutation | 重复点击、预取、重试均可触发 |
| SU-R12 | 浏览器 confirm 仅减少误点 | 不参与服务端唯一性 |
| SU-R13 | quote status 未作为 compare-and-set 条件 | 已确认也不能充当锁 |
| SU-R14 | canonical 与 quotation residual 存在双实现 | 标准 bootstrap 由 Sales owner 生效 |
| SU-R15 | residual filter 按 method+path 去重 | 减少双 handler，不修复 DB race |
| SU-R16 | 若并发产生双 SO，两者可各有行和 TC | quote status 两次写同值不暴露重复 |
| SU-R17 | 列表按 SO 主键逐条显示 | 未见按 quote 去重 |
| SU-R18 | DO、Receipt、AR 以 SO ID 延伸 | 重复 SO 可扩散下游事实 |
| SU-R19 | 未见自动重复检测/合并/冲销作业 | 修复政策 UNKNOWN |
| SU-R20 | EAOS 不得将 redirect 外观当作并发幂等证据 | 顺序与并发必须分开描述 |
| SU-R21 | 已查运行索引把 `idx_sales_orders_no` 建在 `order_no`，而 Convert 写 `so_no` | 该非唯一索引不保护实际转换号 |
| SU-R22 | 另一索引只覆盖 `order_date` | 与 quote 唯一性无关 |
| SU-R23 | 活动 page routes 共享注入的 connection/cursor，配置允许跨线程 | 未观察到 cursor 级互斥包装 |
| SU-R24 | production profile 可切换 PostgreSQL，但 migration 中仍未见 SO unique | 后端锁行为需部署核验 |

## 3. Process

### 3.1 顺序调用

1. 请求 A 读取 quote。
2. A 查询无 SO，插入 header、行和副作用并提交。
3. 请求 B 随后查询到 SO，返回列表。

### 3.2 并发调用

1. A、B 都在任一 insert 前完成 guard miss。
2. 两者生成相同 `SO{quote_id}`。
3. 若生产 schema 与已查 DDL一致，两者都可能 insert。
4. 每个 SO 继续复制行、尝试 TC，并写 quote 已确认。
5. 后续 DO/收款按不同 SO ID 各自发展。

### 3.3 Runtime owner

Enterprise bootstrap 先挂业务 routers，后挂 residual；冲突 method+path 被过滤。该事实确定标准 owner 是 Sales，但不能证明其他启动入口相同。

## 4. Validation

| ID | Validation | Strength |
|----|------------|----------|
| SU-V1 | quote 必须存在 | Hard |
| SU-V2 | 查询时不得已有 SO | Hard application guard |
| SU-V3 | `sales_orders.quote_id` 唯一 | Missing/not observed |
| SU-V4 | `sales_orders.so_no` 唯一 | Missing/not observed |
| SU-V5 | Convert 使用原子 insert-if-absent | Missing |
| SU-V6 | Convert 持有 quote/unique-key lock | Missing |
| SU-V7 | 每次请求携带 idempotency key | Missing |
| SU-V8 | quote status/version compare-and-set | Missing |
| SU-V9 | 重复请求返回同一 SO identity | Missing；仅相同 redirect |
| SU-V10 | duplicate SO 扫描和修复 | Missing |
| SU-V11 | 服务端 Sales Orders.add 权限 | Missing on route |
| SU-V12 | GET mutation 的 CSRF/replay 控制 | Missing/not proven |

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `quotes.id` | 转换输入与 SO number 来源 |
| `sales_orders.quote_id` | 应用层防重查询键；非已证 UNIQUE |
| `sales_orders.so_no` | quote ID 派生显示号 |
| `sales_orders.order_no` | 后补并被索引的平行号码列；Convert 不写 |
| existing SO query | 某一时点的 guard 观察 |
| `sales_orders.id` | 下游 DO/Receipt 等真实外键 |
| quote `status='已确认'` | 至少一次 Convert 写回，不证明只有一 SO |
| browser confirm | 客户端交互，不是锁 |
| redirect `/sales_orders` | guard hit 和成功共用结果 |
| route owner | 标准 bootstrap 的 canonical handler |
| residual route | 源码仍保留、标准挂载过滤的副本 |
| duplicate SO | 同 quote_id 多行；无专用状态 |
| conversion attempt | 未建模 |
| idempotency key | 未建模 |
| lock/version | 未建模 |
| `sales_order_items.so_id` | 重复 SO 各自的行快照归属 |
| downstream `so_id` | 重复事实扩散边界 |

## 6. State Vocabulary

| Term | Meaning |
|------|---------|
| guard miss | 查询时无 SO，不保证插入时仍无 |
| guard hit | 已观察到至少一个 SO |
| converted | 可由 SO 存在推导 |
| duplicate converted | 多个 SO 对同一 quote；无内建标签 |
| sequential idempotency | 后续请求命中 guard |
| concurrent safety | 未被 DB/lock 证明 |

## 7. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 生产库是否手工增加 quote_id UNIQUE | `runtime/v14/legacy_support.py`, `database/`, `apps/sales/repository.py` |
| so_no 是否在某迁移中唯一 | runtime DDL、upgrade/patch、repository |
| SQLite/部署连接如何串行化并发 writer | `core/database/`, runtime globals/config |
| 并发双转换是否有测试或生产事故 | tests/scripts、`docs/reports/` |
| 非 Enterprise 启动的 route owner | app entrypoints、bootstrap、residual routers |
| duplicate SO 在列表/KPI 是否折叠 | Sales repository/templates/ui_center |
| 重复 SO 的删除、合并和下游迁移流程 | sales/inventory/finance routes/services |
| GET 预取、CSRF 或缓存中间件限制 | middleware/security/router setup |
| quote 改价与 Convert 并发时快照来源 | quotation/sales services、version/history |

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | quote/duplicate guards、写入顺序 |
| `apps/sales/repository.py` | SELECT-by-quote 与 INSERT |
| `apps/sales/router.py` | GET Convert route |
| `apps/sales/validator.py` | 无领域锁/唯一校验 |
| `apps/quotation/quote_pages.py` | 平行转换实现 |
| `apps/quotation/v14_residual.py` | residual 附着 |
| `runtime/v14/legacy_support.py` | SO DDL/索引，无已证 UNIQUE |
| `database/upgrade_patch.py` | 升级约束检索 |
| `database/phase3_indexes.sql` | 仅 order_date 索引 |
| `database_health_check.py` | 非唯一 order_no 索引期望 |
| `bootstrap/enterprise_cutover.py` | 挂载顺序 |
| `bootstrap/v14_residual.py` | method/path 去重 |
| `bootstrap/manifest/business_manifest.py` | quotation→sales 挂载链 |
| `config/database.py` | WAL/busy timeout/backend profile |
| `app.py` | 全局 connection/cursor 注入 |
| `templates/quotes.html` | confirm 与 UI permission |
| `templates/sales_orders.html` | duplicate 显示边界 |
| `business_modules/sales.md` | Sales authority 描述 |
| `docs/reports/_static_route_ownership.txt` | canonical owner |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | 链路提取证据 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\`
