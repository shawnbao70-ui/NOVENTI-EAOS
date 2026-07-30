# PHX-G138 Identity AI Employee / Governor Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Smart Terminal / Identity  
**规范源：** ADR-0157  
**人工确认：** 仅 OpenAPI 已有路径；≠ Role→grant；无 Alembic/版本 bump  

## 1. 门禁目标

将 Kernel 已有 platform governor 与 AI employee 面接到薄 Gateway 与 Terminal。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Plane | governor / AI register·profile·reassign → platform；assign → tenant |
| Authz | bootstrap 或 persisted governor（Kernel） |
| UI | Grant/Revoke governor；Register/Get/Update/Assign/Reassign AI |
| Out | Role→grant；WebAuthn；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0157 Accepted。  
2. Gateway + Terminal 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G138_ACCEPTANCE.md](PHX-G138_ACCEPTANCE.md)。
