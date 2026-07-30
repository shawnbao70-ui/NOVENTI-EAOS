# PHX-G82 JWT eaos_roles → ExecutionContext Roles Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / ExecutionContext  
**规范源：** ADR-0101  
**人工确认：** 支付清算另批；无 Permission sync / social login / MFA 注册  

## 1. 门禁目标

将已 mint 的 JWT `eaos_roles` 灌入 `ExecutionContext.roles` 并经 `/v1/context` 可观测；不触碰 Kernel 授权。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| 模型 | `ExecutionContext.roles` |
| 来源 | 租户 JWT `eaos_roles` only |
| 非法类型 | `CTX_INVALID` |
| Body | 禁止 `roles` 覆盖 |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0101 Accepted。  
2. Bearer 带 `eaos_roles` → context/serialize；缺省 `[]`；body 不可提升。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G82_ACCEPTANCE.md](PHX-G82_ACCEPTANCE.md)。
