# PHX-G132 OIDC Login / Callback OpenAPI Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**规范源：** ADR-0151  
**人工确认：** 仅契约增补；refresh/logout/MFA 另批；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将 OIDC login / callback / providers 纳入 `auth.openapi.yaml`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | 扩展既有 `docs/api/auth.openapi.yaml` |
| Paths | login · callback · providers |
| Out | refresh；logout；MFA enrollment；WebAuthn |

## 3. Exit Criteria

1. ADR-0151 Accepted。  
2. OpenAPI 与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G132_ACCEPTANCE.md](PHX-G132_ACCEPTANCE.md)。
