# PHX-G137 Identity Credential/Session Revoke Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Smart Terminal / Identity  
**规范源：** ADR-0156  
**人工确认：** 仅 OpenAPI 已有路径；≠ AI employee/governor；无 Alembic/版本 bump  

## 1. 门禁目标

将 Kernel 已有 credential validate/revoke 与 session revoke 接到薄 Gateway 与 Terminal。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | validation GET；revocation POST → 204 + reason |
| UI | Validate credential / Revoke credential / Revoke session |
| Subject | 目标 subject 作 trusted header |
| Out | AI employee；platform governor；WebAuthn；Role→grant；支付清算 |

## 3. Exit Criteria

1. ADR-0156 Accepted。  
2. Gateway + Terminal 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G137_ACCEPTANCE.md](PHX-G137_ACCEPTANCE.md)。
