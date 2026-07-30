# 编号唯一约束与删除后重号（Uniqueness Constraints）— Legacy Knowledge

**Evidence strength:** Strong for DDL/index definitions and generators; strong negative for Quote/SO/DO/Sample business-number uniqueness  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页区分 DB UNIQUE、普通 index、应用层存在性 guard 与无约束格式。OPP/REQ 的 code 列显式 UNIQUE；Quote/SO/DO/Sample 编号列未观察到 UNIQUE，仅有普通索引或索引错位。`COUNT(*)+1` 会受删除、并发和手工导入影响；DB UNIQUE 只能拒绝 OPP/REQ 冲突，不会自动重算或重试。

## 2. Constraint Matrix

| Entity | Number column | DB UNIQUE | Index | Application protection |
|--------|---------------|-----------|-------|------------------------|
| Opportunity | opportunity_code | Yes | implicit unique | none before insert |
| Requirement | requirement_code | Yes | implicit unique | none before insert |
| Quote | quote_no | No observed | non-unique `idx_quotes_no` | none |
| SO | so_no | No observed | index targets `order_no`, not `so_no` | one-SO-per-quote SELECT guard |
| DO | do_no | No observed | no unique observed | paths differ; no unified number guard |
| Sample | sample_no | No observed | non-unique `idx_samples_no` | none |

## 3. Business Rules

| ID | Rule | Consequence |
|----|------|-------------|
| UC-R1 | OPP code 列是 TEXT UNIQUE | 重复 insert 由 DB 拒绝 |
| UC-R2 | REQ code 列是 TEXT UNIQUE | 同上 |
| UC-R3 | OPP/REQ generator 不捕获 unique 后 retry | 碰撞向请求抛错 |
| UC-R4 | OPP/REQ 允许 caller 提供 code | 格式和序列可被绕过 |
| UC-R5 | OPP/REQ `COUNT(*)+1` 依赖当前行数 | 删除改变未来候选 |
| UC-R6 | 删除非末尾记录可令 count+1 命中仍存在的高号 | DB UNIQUE 拒绝 |
| UC-R7 | 删除最高号可令 count+1 重用已删除 code | 唯一约束允许重用 |
| UC-R8 | Quote 新建同样基于全表 count+1 | 删除可能重号 |
| UC-R9 | Quote code 无 UNIQUE | 重号可静默落库 |
| UC-R10 | Customer 删除路径可级联删除其 Quotes/SOs | 全表 count 后退 |
| UC-R11 | Quote Copy 使用 timestamp，不受 count 删除影响 | 仍有同秒碰撞 |
| UC-R12 | SO number 无 UNIQUE | source-ID 规则不能替代 constraint |
| UC-R13 | 一 quote 一 SO guard 按 quote_id | 不检查 so_no |
| UC-R14 | SO 普通索引使用 `order_no`，而 Convert 写 `so_no` | 不能保护业务号 |
| UC-R15 | DO/Sample 编号无 UNIQUE | timestamp/source 重号可持久化 |
| UC-R16 | 普通 index 只优化查询 | 不拒绝 duplicate |
| UC-R17 | AUTOINCREMENT 主键唯一与业务号唯一分离 | ID 安全不代表显示号安全 |
| UC-R18 | nullable TEXT 编号允许空值的 schema 风险 | 应用路径负责填值 |
| UC-R19 | 未见共享 sequence table | 各模块无法由 DB 原子取号 |
| UC-R20 | 未见 collision audit/repair | 已存在重号需人工识别 |
| UC-R21 | 状态或打印不会修复重复业务号 | 重号持续传播到搜索/文档 |
| UC-R22 | EAOS 不得把 ordinary index 称为 unique constraint | 两者语义不同 |
| UC-R23 | OPP/REQ schema 与 count generator 未包含 tenant_id | UNIQUE/序列呈全局口径 |
| UC-R24 | Quote count 未调用 tenant-scoped count helper | 各租户会共同影响后缀 |

## 4. Delete / Reuse Scenarios

| Scenario | Candidate generation | Result |
|----------|----------------------|--------|
| OPP rows 1..5, delete 3 | count=4 → candidate 5 | UNIQUE conflict with existing 5 |
| OPP rows 1..5, delete 5 | count=4 → candidate 5 | deleted code reused |
| Quote rows 1..5, delete one via customer cascade | count decreases | current-date suffix may collide; no DB block |
| Timestamp record deleted | next code depends wall clock | no direct count reuse, but same-second collision remains |
| SO source quote retained | ID-derived number stable | duplicate conversion can persist same so_no |
| DO source SO retained | ID-derived path stable | repeated conversion can persist same do_no |

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| UC-V1 | OPP code unique | DB Hard |
| UC-V2 | REQ code unique | DB Hard |
| UC-V3 | OPP/REQ collision retry | Missing |
| UC-V4 | Quote/SO/DO/Sample number unique | Missing |
| UC-V5 | business number non-null | Missing at DB |
| UC-V6 | custom OPP/REQ code format/prefix | Missing |
| UC-V7 | deletion must not permit number reuse | Missing |
| UC-V8 | SO guard must be DB unique quote_id | Missing |
| UC-V9 | DO source must obey one/many policy | Missing/unified policy unknown |
| UC-V10 | index must cover actual business-number column | Violated risk for SO |
| UC-V11 | duplicate scan before migration/export | Missing |
| UC-V12 | conflict must log/retry with new number | Missing |

## 6. Data Semantics

| Concept | Honest meaning |
|---------|----------------|
| UNIQUE column | DB rejects duplicate non-null code |
| ordinary index | lookup optimization only |
| AUTOINCREMENT id | technical row identity |
| business number | mutable/unconstrained display key for most modules |
| COUNT(*) | live cardinality, not historical sequence |
| count+1 | candidate suffix, not reserved number |
| deleted maximum | number reuse opening |
| deleted gap | candidate collision opening |
| `quote_id` guard | SO business uniqueness at application layer |
| `so_no` | actual Convert-written SO number |
| `order_no` | parallel indexed SO column |
| nullable number | schema permits missing business code |
| unique violation | OPP/REQ failure surface |
| retry | not observed |
| duplicate audit | not observed |
| shared sequence | not observed |
| tenant-scoped sequence | 未观察到；当前 count 为全表 |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| unique | enforced by DB constraint |
| indexed | query-optimized, duplicates allowed |
| reused | deleted business code generated again |
| collision | candidate already in use |
| duplicate persisted | collision accepted because no unique |
| rejected collision | DB UNIQUE aborts insert |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 生产 DB 是否有手工 unique index | runtime/database migrations/health checks |
| OPP/REQ 是否有 delete UI | lifecycle routes/repository/templates |
| Customer cascade delete 是否在生产获准 | customer services/repository/permissions |
| unique violation 如何呈现给用户 | lifecycle routes/error middleware |
| PostgreSQL schema 是否不同于 SQLite patch | database adapters/migrations/config |
| business number 空值的现有数据量 | schema/code only；未读取生产 DB |
| duplicate cleanup/backfill 脚本 | scripts/reports/database |
| SO `order_no` 与 `so_no` 的迁移意图 | upgrade patch/health report |
| tenant-scoped uniqueness 是否需要 | tenant schema/query/business modules |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `database/business_lifecycle_schema.py` | OPP/REQ UNIQUE |
| `v15/business_lifecycle/repository.py` | count+1 与无 retry |
| `runtime/v14/legacy_support.py` | Quote/SO/DO/Sample DDL 与 ordinary indexes |
| `database/upgrade_patch.py` | SO order_no patch |
| `database/phase3_indexes.sql` | 非唯一业务索引 |
| `database_health_check.py` | expected index 口径 |
| `apps/quotation/services.py` | Quote count/timestamp generators |
| `apps/quotation/repository.py` | Quote count 和 insert |
| `apps/sales/services.py` | SO source-ID number/guard |
| `apps/sales/repository.py` | SO insert/query |
| `apps/inventory/services.py` | DO source-ID insert |
| `apps/sample/services.py` | Sample timestamp insert |
| `apps/customer/repository.py` | customer cascade deletes Quotes/SOs |
| `core/database/transaction.py` | generic transaction exists但 generators 未使用 reservation |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | owner/chain |
| `docs/knowledge/legacy-extract/document-ops/numbering.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
