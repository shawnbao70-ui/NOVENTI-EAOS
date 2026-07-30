# ADR-0017 — AI Employee 派驻与 INHERIT 语义

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. AI Employee 身份全球唯一，但全局最多一个 active tenant assignment。
2. 跨租户移动必须由 active Platform Identity Governor 调用 ReassignAI。
3. `REASSIGN` 结束当前 assignment 并创建目标租户 assignment。
4. `INHERIT` 同样移动租户，并在新记录保存 `predecessor_assignment_id`。
5. INHERIT 仅表达 Identity 管理谱系，不复制 Permission Grant、Knowledge、Memory 或 Session。
6. `ARCHIVE` 不要求 `to_tenant_id`；结束当前派驻并归档 AI Subject。
7. `REASSIGN` / `INHERIT` 必须提供目标租户且必须存在恰好一个当前 active assignment。
8. 检测到历史数据存在多个 active assignment 时失败关闭，不自动选择或合并。

## 后果

- 数据库增加 AI subject 全局 active 唯一索引。
- assignment 增加可空 self-reference predecessor。
- 共享跨租户 AI 能力未来应使用受治理服务模型，不复用 Digital Employee 派驻。

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [ADR-0007-tenant-isolation.md](ADR-0007-tenant-isolation.md)
- [ADR-0016-platform-identity-governor-persistence.md](ADR-0016-platform-identity-governor-persistence.md)
