# PHX-G139 Gateway Ops OpenAPI Catalog Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Gateway meta  
**规范源：** ADR-0158  
**人工确认：** 仅契约；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将 G18 Gateway 元面纳入规范性 OpenAPI 与 Release Manifest。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | `docs/api/ops.openapi.yaml`（新） |
| Paths | `/health` · `/release` · `/adapters` · `/context` · `/context/echo` |
| Inventory | Manifest / adapters 13 → 14 |
| Out | Role→grant；WebAuthn；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0158 Accepted。  
2. OpenAPI + release inventory 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G139_ACCEPTANCE.md](PHX-G139_ACCEPTANCE.md)。
