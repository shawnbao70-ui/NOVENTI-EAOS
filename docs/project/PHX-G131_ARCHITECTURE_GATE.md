# PHX-G131 Auth OpenAPI Status Catalog Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**规范源：** ADR-0150  
**人工确认：** 仅 status；无 login/callback OpenAPI；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将 Auth 边界三条脱敏 status 探针纳入规范性 OpenAPI 与 Release Manifest。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | `docs/api/auth.openapi.yaml`（新） |
| Paths | `GET /auth/oidc/status` · `/auth/idp/status` · `/auth/jwt/status` |
| Inventory | Manifest / adapters 11 → 12 |
| Out | login/callback/refresh/logout；WebAuthn |

## 3. Exit Criteria

1. ADR-0150 Accepted。  
2. OpenAPI + release inventory 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G131_ACCEPTANCE.md](PHX-G131_ACCEPTANCE.md)。
