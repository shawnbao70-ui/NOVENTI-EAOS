# PHX-G76 Deploy Region Identity Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Ops / Gateway  
**退出门禁：** 可选 `EAOS_DEPLOY_REGION`；`/v1/release.deploy_region`；Helm/Compose 接线；非 multi-region SaaS；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0095 + Architecture Gate |
| B | Gateway `deploy_region` + release 字段 |
| C | Helm `region.*` + Compose env |
| D | `REGION.md` + 契约 `test_ops_g76` / `test_api_gateway_g76_*` |

## 2. 核心不变量

- 空区域合法（未标注单主机）  
- 非法 token fail-closed  
- 不实现 failover / 副本 / 跨区域 SaaS  

## 3. 自动化证据

- 本地完整回归：`587 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0095 |
| Constitution Review | 通过；ops 薄边界 |
| Cross-reference Review | 通过；与 `region_policy_ref` / KMS region 分离 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 联邦策略矩阵、failover SaaS、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 联邦策略矩阵 UI  
- 多区域生产 SaaS / failover / 只读副本  

## 6. 证据索引

- [PHX-G76 Architecture Gate](PHX-G76_ARCHITECTURE_GATE.md)
- [ADR-0095](../decisions/ADR-0095-deploy-region-identity.md)
- [REGION.md](../release/REGION.md)
