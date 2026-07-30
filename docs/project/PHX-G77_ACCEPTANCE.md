# PHX-G77 Tenant IdP Federation Policy Matrix Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Terminal  
**退出门禁：** 矩阵只读 API + Terminal Matrix；复用 G66–G69；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0096 + Architecture Gate |
| B | `GET /v1/platform/idp/federation/matrix` |
| C | Terminal Admin Federation matrix |
| D | `federation.matrix` status 摘要 + 契约 |

## 2. 核心不变量

- Platform 只读；Bind/Unbind 仍走既有路由  
- body 禁止 `tenant_id` / `platform_scope`  
- 无策略引擎 / social login / 租户面 CRUD  

## 3. 自动化证据

- 本地完整回归：`595 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0096 |
| Constitution Review | 通过；Gateway / platform 边界 |
| Cross-reference Review | 通过；G66–G69 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 策略引擎、social login、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Social login / 租户面 IdP CRUD  
- Claim 映射 / MFA / 多 issuer 优先级  
- 多区域生产 SaaS / failover  

## 6. 证据索引

- [PHX-G77 Architecture Gate](PHX-G77_ARCHITECTURE_GATE.md)
- [ADR-0096](../decisions/ADR-0096-tenant-idp-federation-matrix.md)
