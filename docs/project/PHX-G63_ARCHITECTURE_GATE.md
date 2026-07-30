# PHX-G63 OIDC Refresh Binding SQL Adapter Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0082  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选 SQL 仓储持久化 OIDC refresh 绑定；默认 memory。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_OIDC_REFRESH_STORE` |
| Default | `memory` |
| Schema | Alembic `0026` `kernel.oidc_refresh_bindings` |
| URL | fail-closed `postgresql+psycopg` |

## 3. Exit Criteria

1. ADR-0082 Accepted。  
2. sql/memory 可切换；契约绿；head `0026`。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G63_ACCEPTANCE.md](PHX-G63_ACCEPTANCE.md)。
