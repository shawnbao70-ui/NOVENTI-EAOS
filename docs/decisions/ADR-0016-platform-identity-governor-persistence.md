# ADR-0016 — Platform Identity Governor 持久化

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. 采用独立 `platform_identity_governors` 授权历史表，不复用租户 Permission Grant。
2. 每次授予创建不可变历史记录；撤销更新该记录的状态、撤销人、时间与原因。
3. 同一主体最多一条 active Governor 授权。
4. 显式 bootstrap UUID 集合仅在数据库尚无 active Governor 时可授予首条记录。
5. 首条持久化授权后，bootstrap 集合不再提供治理权限；所有治理操作以数据库为准。
6. RegisterAIEmployee 与 ReassignAI 必须由 active 持久化 Governor 执行；兼容期仅在尚无持久化记录时允许 bootstrap。
7. 禁止撤销最后一个 active Governor，防止平台治理锁死。
8. Governor 历史为平台作用域，不携带 tenant_id。

## 非目标

- Organization Governor 合并
- Permission Policy 平台授权
- 外部 IAM / break-glass 流程
- Governor 主体生命周期自动同步

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [ADR-0015-identity-credential-lifecycle.md](ADR-0015-identity-credential-lifecycle.md)
