# Convert Atomicity Deepen — Legacy Knowledge Pack

## Purpose

本包深化 EZAM_CRM 9.0 Quote→SO 的唯一性、事务提交、副作用及商业快照边界。它记录可证运行行为，不复制源码，不将“同 connection”“页面成功”或“存在 quote_id”扩大解释为完整原子性。

## Modules

- [`so_uniqueness.md`](so_uniqueness.md)：应用层防重与数据库唯一/锁缺口。
- [`commission_atomicity.md`](commission_atomicity.md)：SO、TC、行和 quote 写回的 commit/异常边界。
- [`lifecycle_hook_atomicity.md`](lifecycle_hook_atomicity.md)：Requirement/Opportunity 链接的 post-commit best-effort 语义。
- [`term_snapshot_on_convert.md`](term_snapshot_on_convert.md)：付款、信用、FX、折扣、税和 Incoterms 快照矩阵。
- [`INDEX.md`](INDEX.md)：证据强度、跨包边界和覆盖检查。

## Evidence Posture

1. **Strong**：active Sales/Quotation services、repositories、runtime DDL、bootstrap route ownership。
2. **Strong negative**：在 DDL、migration、repository 和报告中未观察到 unique、lock、outbox、retry 或全条款目标列。
3. **Mixed**：异常请求的最终 SQLite rollback、私有生产 schema、非标准启动入口只能标 UNKNOWN。
4. **Cross-reference**：commission-ledger-deepen、quote-convert-policy-deepen、commercial-terms 只作为既有知识边界，不修改其正文。

## Critical Honesty Findings

- 一报价一 SO 是 SELECT-then-INSERT 的顺序防重，不是已证 DB 并发唯一。
- 正常路径的 SO、TC、items、quote 写回共用 connection 并在 quote 更新时 commit；TC helper 可静默失败，使 SO 成功但无佣金。
- Lifecycle hook 位于主 commit 后，并可分多次 commit；失败不撤销 Convert，且可能部分链接。
- Convert 复制金额与行净价结果，不冻结完整付款、信用、FX、折扣、税或 Incoterms 合同快照。

## Hard Boundaries

- 本包不提供 Convert、佣金、审批、付款或修复 CRUD。
- 不修改邻包权威正文。
- 不把 Pending TC 当作已批准/发放。
- 不把 Human Approved、lifecycle link 或 quote `已确认` 当作原子提交证明。
- 只写 `docs/knowledge/legacy-extract/convert-atomicity-deepen/**`。

## Read-only Roots

- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\`
- `H:\Workspace\EZAM_CRM - 9.0\database\`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
