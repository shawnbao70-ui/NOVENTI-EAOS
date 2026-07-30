# 并发编号碰撞（Concurrency Collision）— Legacy Knowledge

**Evidence strength:** Strong for deterministic collision windows; strong negative for reservation, lock and retry; runtime incidence UNKNOWN  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页分析并发双开、双提交和批量创建如何使 count+1、秒级 timestamp 与 source-ID-derived 编号碰撞。静态证据可证明候选相同的窗口，不能证明生产中已发生。OPP/REQ 会由 DB UNIQUE 拒绝其中一个；其余主业务号通常可静默重复。

## 2. Collision Matrix

| Entity/path | Same-candidate condition | DB outcome | Business outcome |
|-------------|--------------------------|------------|------------------|
| OPP | two requests read same COUNT | one UNIQUE conflict | one request fails, no retry |
| REQ | same | one UNIQUE conflict | opportunity requirement_count may need error handling |
| New Quote | two requests read same quote COUNT/date | duplicates allowed | two quotes same quote_no |
| Copy/Sample Quote | creations within same second | duplicates allowed | same QT timestamp |
| SO | concurrent Convert same quote | duplicates allowed | same SO number, different IDs |
| Sales DO | any two creates same second | duplicates allowed | same DO number |
| Inventory DO | repeated/concurrent same SO | duplicates allowed | same DO number |
| Sample | any two adds same second | duplicates allowed | same SP number |
| Receipt（相邻编号风险） | same SO requests read same received sum | duplicates allowed | same RC suffix |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| CCN-R1 | count+1 先读后写，不预留候选 | 有 TOCTOU |
| CCN-R2 | OPP 与 REQ 各自在独立表 count | 不互撞，但各自内部会撞 |
| CCN-R3 | OPP/REQ UNIQUE 是最终裁决 | 不自动产生下一号 |
| CCN-R4 | create methods 未见 unique conflict retry | 失败暴露给请求 |
| CCN-R5 | Quote count+1 无 DB UNIQUE | 并发可双写同号 |
| CCN-R6 | Quote count 是全表，不按 tenant/date加锁 | 多租户/日期不缩小窗口 |
| CCN-R7 | 秒级 timestamp 在整秒内恒定 | 同 prefix 的创建碰撞 |
| CCN-R8 | timestamp generator 无随机尾码/sequence | 无概率去重 |
| CCN-R9 | Copy Quote 与 Sample→Quote 共享 QT timestamp family | 跨入口也可能同秒碰撞 |
| CCN-R10 | SO 编号由 quote ID 确定 | 同 quote 的并发 Convert 必然同候选 |
| CCN-R11 | SO 防重是 SELECT-then-INSERT | 两请求可同时 guard miss |
| CCN-R12 | SO quote_id/so_no 无 DB UNIQUE | 双 SO 可持久化 |
| CCN-R13 | Sales DO timestamp 不按 SO 区分 | 不同 SO 同秒也可重号 |
| CCN-R14 | Inventory DO source-ID 规则无统一 guard | 同 SO 重复可重号 |
| CCN-R15 | Sample SP timestamp 无 unique | 批量导入同秒风险 |
| CCN-R16 | WAL/busy timeout/数据库写锁只影响调度 | 不等于业务号 reservation |
| CCN-R17 | 共享 connection/cursor 可能串行部分执行，但无编号原子契约 | 不能据此宣称安全 |
| CCN-R18 | PostgreSQL profile 不改变 SELECT-then-INSERT 算法 | 无 unique/lock 仍有 race |
| CCN-R19 | ordinary index 不阻止 duplicates | 搜索性能≠完整性 |
| CCN-R20 | 无 collision attempt/audit 表 | 无统一检测 |
| CCN-R21 | 无 retry suffix 或 regenerate loop | 冲突不自动恢复 |
| CCN-R22 | UUID-based intelligence OPP 不适用于 persisted lifecycle code | 不能作为主链修复证据 |
| CCN-R23 | 编号碰撞可污染搜索、打印、ledger source_no 与外部引用 | technical IDs 仍不同 |
| CCN-R24 | EAOS 不得把“尚无事故报告”作为并发安全证据 | 缺测试不等于无风险 |
| CCN-R25 | 注入的 `db_lock` 未观察到 handler 使用 | 存在锁对象不等于编号已串行 |
| CCN-R26 | Business page router 先占路径，V14 residual 冲突会被过滤 | 标准 runtime authority 在 apps services |
| CCN-R27 | Receipt 后缀基于 `int(SUM(amount))+1`，不是收款行数 | 双提交可读同一 sum 并生成同号 |
| CCN-R28 | Quote insert 自行 commit，但 count 与 insert 仍是两个步骤 | 未形成原子 reservation |
| CCN-R29 | 未观察到活动 MAX+1 生成器 | 不应把 count+1 与 max+1 混称 |
| CCN-R30 | `create_do` 与 `convert_do` 是不同 URL/算法 | 同 SO 可跨入口形成不同格式或重号 |

## 4. Collision Processes

### 4.1 Count+1

1. A、B 都执行 COUNT，得到 N。
2. A、B 都形成 N+1。
3. OPP/REQ：一个 insert 成功，另一个 UNIQUE error。
4. Quote：若无其他约束，两者均可成功。

### 4.2 Timestamp second

1. A、B 在同一秒调用 `strftime`.
2. prefix 和时间文本相同。
3. Copy/Sample Quote、Sales DO 或 Sample 分别写入各自表。
4. 无 unique 时重复成为持久数据。

### 4.3 Source ID

1. 同一个 quote/SO 被并发或重复转换。
2. 两次计算相同 `SO{quote_id}` / `DO{so_id}`。
3. 应用 guard 若非原子，两行可插入。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| CCN-V1 | candidate generation 与 insert 同一原子操作 | Missing |
| CCN-V2 | OPP/REQ unique | DB Hard |
| CCN-V3 | OPP/REQ conflict retry | Missing |
| CCN-V4 | Quote/SO/DO/Sample unique | Missing |
| CCN-V5 | count row/sequence lock | Missing |
| CCN-V6 | source conversion unique | Missing at DB |
| CCN-V7 | timestamp collision retry/random suffix | Missing |
| CCN-V8 | idempotency key for creates/converts | Missing |
| CCN-V9 | tenant-scoped sequence/unique | Missing |
| CCN-V10 | batch import number allocation | Missing |
| CCN-V11 | duplicate detection after insert | Missing |
| CCN-V12 | concurrency tests for all generators | Missing/not found |
| CCN-V13 | Receipt number unique / double-submit idempotent | Missing |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| collision window | 候选计算与 insert 之间 |
| same candidate | 两请求生成相同文本 |
| DB unique conflict | OPP/REQ insert 被拒 |
| silent duplicate | 无 unique 的两行同号 |
| business number | 可碰撞文本 |
| technical ID | 各成功 insert 的自增主键 |
| count snapshot | 某时点表行数 |
| second timestamp | 一秒粒度时钟文本 |
| source-ID candidate | 对同源确定性相同 |
| application guard | 非锁的先查检查 |
| ordinary index | 不提供排他性 |
| WAL | SQLite journal mode，不是业务序列 |
| busy timeout | 等待写锁，不重算候选 |
| retry policy | 未建模 |
| idempotency key | 未建模 |
| collision audit | 未建模 |
| receipt suffix | SO 已收金额总和取整后 +1，不是 row sequence |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| guard miss | 查询时未观察到记录 |
| reserved | Legacy 未实现的编号状态 |
| allocated | candidate 已计算但未保留 |
| committed duplicate | 同号多行已提交 |
| rejected collision | UNIQUE 阻断 |
| retried | 未观察到自动行为 |

## 8. Impact

| Surface | Collision impact |
|---------|------------------|
| list/search | keyword 命中多行 |
| detail routes | 仍按 ID 跳转，可能掩盖重号 |
| NDE/print | 多份文档展示同号 |
| SO/DO chain | source_no/ledger remark 模糊 |
| TC ledger | 同 SO display number 可对应不同 SO IDs |
| external integration | 无法以业务号稳定 upsert |
| audit | 操作者可能误认同一交易 |

## 9. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 生产实际碰撞数量 | 静态源码/报告，无生产 DB读取 |
| 并发测试是否在外部 CI | tests/scripts/reports |
| 全局 cursor 是否序列化所有 page requests | app/runtime/database manager |
| PostgreSQL 生产 DDL unique 差异 | adapters/migrations/config |
| server 多进程/多实例部署 | startup/deployment docs |
| clock rollback/NTP 对 timestamp 影响 | deployment/config/reports |
| collision error 的用户提示 | route exception middleware/templates |
| duplicate number cleanup | scripts/datafix/reports |
| external systems是否以业务号为 unique key | integrations/open platform/docs |

## 10. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `v15/business_lifecycle/repository.py` | count+1 / no retry |
| `database/business_lifecycle_schema.py` | OPP/REQ unique |
| `apps/quotation/services.py` | Quote count/timestamp generators |
| `apps/quotation/repository.py` | count query and insert |
| `apps/sales/services.py` | SO source-ID、DO timestamp |
| `apps/sales/repository.py` | guard/insert |
| `apps/inventory/services.py` | DO source-ID path |
| `apps/sample/services.py` | SP timestamp |
| `apps/finance/services.py` | Receipt SUM-derived suffix |
| `runtime/v14/legacy_support.py` | missing unique/ordinary indexes |
| `database/upgrade_patch.py` | schema/index drift |
| `config/database.py` | WAL/busy timeout/backend profiles |
| `core/database/manager.py` | connection model |
| `app.py` | injected global cursor/conn |
| `bootstrap/v14_residual.py` | business-page first、residual conflict filter |
| `bootstrap/enterprise_cutover.py` | runtime route ownership |
| `docs/reports/_static_route_ownership.txt` | parallel routes |
| `docs/knowledge/legacy-extract/document-ops/numbering.md` | EAOS 只读基线 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
