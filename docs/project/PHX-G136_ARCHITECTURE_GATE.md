# PHX-G136 Permission Roles List OpenAPI Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Permission  
**规范源：** ADR-0155  
**人工确认：** 只读 list；≠ Role→grant；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将既有 `GET /v1/permission/roles` 纳入 `permission.openapi.yaml`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | `permission.openapi.yaml` v1.1.0（additive） |
| Path | `GET /permission/roles`（flat `{enabled,roles}`） |
| Inventory | Manifest 仍 13 |
| Out | Role→grant；WebAuthn；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0155 Accepted。  
2. OpenAPI 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G136_ACCEPTANCE.md](PHX-G136_ACCEPTANCE.md)。
