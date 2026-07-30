# PHX-G63 OIDC Refresh Binding SQL Adapter Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `EAOS_OIDC_REFRESH_STORE` 可切换；Alembic `0026`；默认 memory；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0082 + Architecture Gate |
| B | SQLAlchemy 模型/仓储 + store 接线 |
| C | Alembic `0026_oidc_refresh_bindings_g63` |
| D | 契约 `test_api_gateway_g63_*` |

## 2. 核心不变量

- 默认 `memory`；`sql` 需 `EAOS_DATABASE_URL`  
- Refresh/Logout API 不变  
- 响应不回传 refresh/id_token  
- status 暴露 `refresh_store`  

## 3. 自动化证据

- 本地完整回归：`532 passed`（`tests/contracts`）  
- Alembic head：`0026_oidc_refresh_bindings_g63`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0082 |
| Constitution Review | 通过；Persistence 边界 |
| Cross-reference Review | 通过；G61 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0026` |
| Gap Analysis | 令牌加密、支付清算、组织联邦 UI 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 令牌应用层加密  
- 组织级联邦 UI / 网格 CRD / 多区域  

## 6. 证据索引

- [PHX-G63 Architecture Gate](PHX-G63_ARCHITECTURE_GATE.md)
- [ADR-0082](../decisions/ADR-0082-oidc-refresh-sql.md)
