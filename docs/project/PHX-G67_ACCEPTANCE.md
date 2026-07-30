# PHX-G67 Tenant IdP Federation SQL Adapter Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `EAOS_TENANT_IDP_FEDERATION_STORE` 可切换；Alembic `0027`；默认 memory；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0086 + Architecture Gate |
| B | SQLAlchemy 模型/仓储 + store 接线 |
| C | Alembic `0027_tenant_idp_bindings_g67` |
| D | 契约 `test_api_gateway_g67_*` |

## 2. 核心不变量

- 默认 `memory`；`sql` 需 `EAOS_DATABASE_URL`  
- API 不变；缺 URL → 503 `GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE`  
- `(tenant_id, lower(issuer))` 唯一；软禁用可 reactivate  

## 3. 自动化证据

- 本地完整回归：`547 passed`（`tests/contracts`）  
- Alembic head：`0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0086 |
| Constitution Review | 通过；Persistence 边界 |
| Cross-reference Review | 通过；G66 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 联邦 UI/JWT 强制、支付清算、网格 CRD 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 联邦 UI / JWT 强制绑定 / social login  
- 网格 CRD / 多区域 / KMS  

## 6. 证据索引

- [PHX-G67 Architecture Gate](PHX-G67_ARCHITECTURE_GATE.md)
- [ADR-0086](../decisions/ADR-0086-tenant-idp-federation-sql.md)
