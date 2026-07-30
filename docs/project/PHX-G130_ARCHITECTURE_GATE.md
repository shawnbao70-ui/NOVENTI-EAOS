# PHX-G130 OpenAPI Foundation Status Catalog Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts  
**规范源：** ADR-0149  
**人工确认：** auth OpenAPI 另批；无运行时/Alembic/版本 bump；支付清算另批  

## 1. 门禁目标

将既有 Gateway Foundation `GET */status` 探针纳入规范性 OpenAPI 目录。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Scope | 9 份既有域 YAML；11 条 status GET |
| Schema | FoundationStatusEnvelope；Roles 专用 RoleCatalogStatusEnvelope |
| Out | auth status YAML；运行时行为变更 |

## 3. Exit Criteria

1. ADR-0149 Accepted。  
2. OpenAPI 路径与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G130_ACCEPTANCE.md](PHX-G130_ACCEPTANCE.md)。
