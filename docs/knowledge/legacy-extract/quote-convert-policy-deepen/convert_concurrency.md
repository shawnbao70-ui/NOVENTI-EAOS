# 报价转单并发与幂等（Convert Concurrency）— Legacy Knowledge

**Evidence strength:** Strong for read-before-write guard and commit order; strong negative for DB uniqueness/locking/compensation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块深化“一报价一 SO”的实现强度、并发 race、双转换实现、TC 佣金和 lifecycle 钩子的提交边界。它交叉引用 `../order-chain/so_convert.md` 和 `../commission-ledger-deepen/commission_on_convert.md`。

Legacy 的防重是先按 `quote_id` 查询、再插入；未观察到唯一索引、锁、upsert 或 idempotency token。正常 SQL 使用同一 connection 并在 quote 状态更新时 commit，但佣金异常被吞后可提交缺 TC 的 SO，lifecycle 又在该 commit 后 best-effort 执行。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CC-R1 | Convert 先查 quote 是否存在 | 不存在不写 |
| CC-R2 | 再查 `sales_orders.quote_id` 是否已有记录 | 命中即返回列表 |
| CC-R3 | 防重属于应用层 read-before-write | 查询与 insert 之间存在 race window |
| CC-R4 | 未观察到 `quote_id` UNIQUE | 数据库不保证一报价一单 |
| CC-R5 | SO number 由 quote ID 派生 | 并发重复也会得到相同 number |
| CC-R6 | 未观察到 SO number UNIQUE 冲突处理 | 是否由部署 schema 拦截 UNKNOWN |
| CC-R7 | Convert 使用 GET | 浏览器重放/预取/重复点击可能触发 |
| CC-R8 | UI confirm 不产生服务端 idempotency key | 只能减少误点 |
| CC-R9 | canonical 与 legacy Quotation 保留同 method/path 实现 | 标准 bootstrap 由 Sales first-match |
| CC-R10 | residual 去重减少双 route 同时可达 | 不删除遗留实现 |
| CC-R11 | 非标准启动方式的 route owner 仍需核验 | 源码双轨仍构成维护风险 |
| CC-R12 | 正常顺序为 SO header→TC→SO items→quote 已确认→commit | 同批 SQL 共享 connection |
| CC-R13 | commission 钩子异常被吞 | 后续 items/quote 仍 commit |
| CC-R14 | lifecycle link 在主 commit 后执行 | 失败不会回滚商业事实 |
| CC-R15 | lifecycle 失败也被吞 | 可有 SO 无追踪 link |
| CC-R16 | quote status 更新方法执行 commit | 是 canonical 主 SQL 提交点 |
| CC-R17 | line copy 中途异常的 rollback 行为未显式编排 | 依赖 connection/框架行为 |
| CC-R18 | 无转换 attempt、failure、retry 或 outbox 实体 | 无可靠补偿队列 |
| CC-R19 | `tc_ledger` 无 source 唯一键 | 并发可放大重复佣金 |
| CC-R20 | quote status 不是并发条件 | Convert 不做 compare-and-set |
| CC-R21 | quote version/history 不作为锁 | 不防批准/改价/转单交错 |
| CC-R22 | EAOS 不得把 redirect 幂等外观等同并发安全 | 顺序点击与真正并发不同 |

---

## 3. Process

### 3.1 顺序请求

1. 请求 A 查询 quote，未发现 SO。
2. A 插 SO、尝试 TC、复制行、写 quote 已确认并 commit。
3. 后续请求 B 查询时命中 SO，安全返回列表。

### 3.2 并发 race

1. 请求 A 与 B 均在任一 insert 前完成“无 SO”查询。
2. 两者生成相同 SO number 并尝试插入。
3. 若 schema 无唯一约束，两份 SO/行/TC 均可能写入。
4. quote status 两次写已确认，无法暴露重复。
5. lifecycle link 行为取决于后执行结果，未见去重保证。

### 3.3 部分成功

- TC 异常：SO、行和 quote 可成功，佣金缺失。
- lifecycle 异常：商业 SQL 已 commit，追踪 link 缺失。
- 行复制/quote commit 前异常：显式 rollback/补偿未观察到。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CC-V1 | quote 必须存在 | Hard | |
| CC-V2 | 查询时不得已有 SO | Hard application guard | |
| CC-V3 | DB 必须 UNIQUE `sales_orders.quote_id` | Missing/not proven | |
| CC-V4 | DB 必须 UNIQUE `sales_orders.so_no` | UNKNOWN | |
| CC-V5 | TC source 必须唯一 | Missing | |
| CC-V6 | Convert 必须携带 idempotency key | Missing | |
| CC-V7 | Convert 必须使用锁或原子 upsert | Missing | |
| CC-V8 | quote status/version 必须 compare-and-set | Missing | |
| CC-V9 | SO/header/items/TC/quote 必须有明确事务 | Mixed | 同 connection 但异常策略分裂 |
| CC-V10 | lifecycle 必须可靠投递/重试 | Missing | post-commit best-effort |
| CC-V11 | 佣金失败必须形成可重试事件 | Missing | 静默 |
| CC-V12 | 重复 SO 必须有修复与审计 | Missing | |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.quote_id` | 应用层幂等查询键 |
| `sales_orders.so_no` | quote ID 派生号，不是独立幂等 token |
| existing SO query | 顺序请求防重检查 |
| quote status `已确认` | 转换后写回，不能证明仅一 SO |
| `sales_order_items` | 每个成功 insert 的行快照 |
| `tc_ledger.source_no` | SO number 弱文本键 |
| `tc_ledger` Pending | best-effort 佣金副作用 |
| lifecycle link | post-commit 追踪副作用 |
| repository commit | quote status 更新时主 SQL 提交 |
| browser confirm | 客户端防误触，不是幂等事实 |
| redirect `/sales_orders` | 已有/成功均可返回的相同表面 |
| quote version | 报价版本槽位，未作为 concurrency token |
| route first-match | 标准 bootstrap 的 runtime owner 选择 |
| residual duplicate | 被过滤但仍存在的维护副本 |
| conversion attempt | UNKNOWN / 无专用记录 |

---

## 6. State Vocabulary

| Term | Meaning / caveat |
|------|------------------|
| not converted | 查询时无 `sales_orders.quote_id` |
| converted | 至少一个 SO 引用 quote |
| duplicate converted | 多个 SO 引用同 quote；无显式状态 |
| Pending commission | 可重复或缺失的转单副作用 |
| linked lifecycle | best-effort 追踪结果 |
| partial success | SO 存在但 TC/link 不完整 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 生产 DB 是否另加 quote_id/so_no 唯一索引 | runtime DDL、database migrations、sales repository |
| SQLite/部署连接对并发 writer 的锁行为 | database context/config、runtime reports |
| 非标准启动是否可让 legacy convert 成为 owner | bootstrap、app entrypoints、route reports |
| 行复制异常时 connection 是否自动 rollback | repository/base/context、middleware |
| lifecycle link 自身是否按 quote/SO 去重 | v15/business_lifecycle workflow/repository |
| TC 重复/漏记的对账作业 | sales/finance/commission scheduler/reports |
| quote 改价与 Convert 并发时采用哪个金额 | quotation/sales services、version/history |
| 重复 SO 的人工修复和引用迁移 | sales/inventory/finance delete/cancel paths |
| GET 预取、缓存或 CSRF 中间件是否限制 mutation | middleware/security/router reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 防重、写入顺序、钩子异常 |
| `apps/sales/repository.py` | existing query、insert 与 commit 点 |
| `apps/sales/router.py` | GET mutation |
| `apps/quotation/quote_pages.py` | 平行转换实现与 commit |
| `apps/quotation/v14_residual.py` | legacy route 附着 |
| `apps/quotation/repository.py` | quote 更新无版本条件 |
| `runtime/v14/legacy_support.py` | SO/TC schema 与无显式 unique 证据 |
| `bootstrap/enterprise_cutover.py` | 挂载顺序 |
| `bootstrap/v14_residual.py` | method/path first-match 去重 |
| `v15/business_lifecycle/workflow.py` | post-commit Quote→SO link |
| `templates/quotes.html` | confirm 和重复点击表面 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | canonical owner |
| `docs/reports/V15_RUNTIME_STABILITY_REPORT.md` | 运行时转换异常背景 |
| `docs/knowledge/legacy-extract/order-chain/so_convert.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/commission-ledger-deepen/commission_on_convert.md` | EAOS 佣金副作用交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
