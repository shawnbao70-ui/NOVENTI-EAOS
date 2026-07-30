# Numbering Collision Deepen — Legacy Knowledge Pack

## Purpose

本包深化 EZAM_CRM 9.0 Opportunity、Requirement、Quote、SO、DO 与 Sample 的编号生成、唯一约束、并发碰撞及展示/事务权威边界。内容只描述可证 Legacy 行为，不复制源码，不修改邻包。

## Modules

- [`generators_matrix.md`](generators_matrix.md)：各实体算法、前缀、时间、count 和 source-ID 对照。
- [`uniqueness_constraints.md`](uniqueness_constraints.md)：DB UNIQUE、普通 index、应用 guard 与删除后重号。
- [`concurrency_collision.md`](concurrency_collision.md)：count+1、timestamp 和 source-ID 的并发碰撞。
- [`display_vs_authority.md`](display_vs_authority.md)：显示号、技术 ID、FK、source_no 与打印号的权威区别。
- [`INDEX.md`](INDEX.md)：覆盖门槛、跨包引用和风险索引。

## Evidence Posture

1. **Strong**：活动 repository/service、运行 DDL、migration/index 和打印消费者。
2. **Strong negative**：Quote/SO/DO/Sample 未观察到 business-number UNIQUE、共享 sequence、reservation 或 collision retry。
3. **Mixed**：并发候选冲突可由算法证明；生产事故数量、私有 schema 和部署进程模型标 UNKNOWN。
4. **Cross-reference**：`document-ops/numbering.md` 仅作只读基线，不修改正文。

## Critical Honesty Findings

- OPP/REQ 使用全表 count+1 且 DB UNIQUE；碰撞会失败，没有自动重试。
- New Quote 的日期前缀配全表 count，并非日内 sequence；Quote Copy/Sample Quote 改用秒级 timestamp。
- SO 由 quote ID 派生，DO 同时存在 timestamp 与 SO-ID 两套格式。
- Quote/SO/DO/Sample 编号缺 DB UNIQUE；普通 index 不提供完整性。
- 交易关系主要依赖 numeric IDs，但 TC、AR、inventory ledger 使用业务号弱文本引用。

## Hard Boundaries

- 本包不创建编号服务、sequence、约束或数据修复。
- 不修改 document-ops、crm、sales、delivery 等邻包权威正文。
- 不把格式、普通索引或技术主键解释为业务号唯一。
- 只写 `docs/knowledge/legacy-extract/numbering-collision-deepen/**`。

## Read-only Roots

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\`
- `H:\Workspace\EZAM_CRM - 9.0\database\`
- `H:\Workspace\EZAM_CRM - 9.0\document\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
