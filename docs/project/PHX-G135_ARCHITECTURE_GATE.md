# PHX-G135 Platform OpenAPI Catalog Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Platform  
**规范源：** ADR-0154  
**人工确认：** 仅契约；≠ Role→grant；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将既有平台面 Roles + IdP/Federation Gateway 路径纳入规范性 OpenAPI 与 Release Manifest。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | `docs/api/platform.openapi.yaml`（新） |
| Paths | `/platform/roles*` · `/platform/idp/issuers*` · discovery/sync · federation/* |
| Inventory | Manifest / adapters 12 → 13 |
| Out | Role→grant；WebAuthn；支付清算；`/permission/roles`；`0.2.1` |

## 3. Exit Criteria

1. ADR-0154 Accepted。  
2. OpenAPI + release inventory 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G135_ACCEPTANCE.md](PHX-G135_ACCEPTANCE.md)。
