# PHX-G57 IdP Registry SQL Adapter Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `EAOS_IDP_REGISTRY_STORE` 可切换；SQL 复用 Alembic `0025`；默认 memory；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0076 + Architecture Gate |
| B | SQLAlchemy 模型/仓储 + Gateway store 接线 |
| C | 契约（memory 默认 + SQL sqlite + fail-closed） |
| D | 状态/运维文档更新 |

## 2. 核心不变量

- 默认 `memory`（`process_memory`）；`sql` 需 `EAOS_DATABASE_URL`（`postgresql+psycopg`）  
- 缺 URL / 非法 store → fail-closed  
- 合并规则不变：env issuer 优先  
- 无新 Alembic；复用 `kernel.idp_issuer_bindings`  
- SQL 唯一 issuer：disabled 可重新激活  

## 3. 自动化证据

- 本地完整回归：`505 passed`（`tests/contracts`）  
- Alembic head：仍为 `0025_idp_issuer_bindings_g56`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0076 |
| Constitution Review | 通过；Gateway 薄适配 + Persistence 边界 |
| Cross-reference Review | 通过；G56 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | Mesh/KEDA、Discovery 写回、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Discovery 写回 env / 联邦策略 UI  
- Service Mesh / KEDA / 多区域  

## 6. 证据索引

- [PHX-G57 Architecture Gate](PHX-G57_ARCHITECTURE_GATE.md)
- [ADR-0076](../decisions/ADR-0076-idp-registry-sql.md)
