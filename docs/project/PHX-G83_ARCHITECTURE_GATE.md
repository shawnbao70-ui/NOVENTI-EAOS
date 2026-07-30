# PHX-G83 Opt-in Context Roles Evaluate Grant Map Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Permission Kernel  
**规范源：** ADR-0102  
**人工确认：** 支付清算另批；无 Role 表 / grant 写入 / social / MFA  

## 1. 门禁目标

可选将 `ExecutionContext.roles` 作为 ephemeral allow 源接入 `PermissionService.evaluate`；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_PERMISSION_ROLE_GRANT_MAP`（空=off） |
| 优先级 | deny > grant/policy/role allow |
| 证据 | `matched_roles`；`MATCHED_CONTEXT_ROLE` |
| Schema | 无 Alembic（JSON evidence 扩字段） |

## 3. Exit Criteria

1. ADR-0102 Accepted。  
2. map off 行为不变；map on + roles 命中 → allow；deny 覆盖。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G83_ACCEPTANCE.md](PHX-G83_ACCEPTANCE.md)。
