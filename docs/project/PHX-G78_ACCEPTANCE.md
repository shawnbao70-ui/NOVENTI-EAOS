# PHX-G78 Tenant IdP Federation Issuer Priority Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `priority` 字段 + set API；memory|sql；Alembic `0028`；enforce 语义不变；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0097 + Architecture Gate |
| B | `priority` + Alembic `0028` |
| C | `POST .../bindings/{id}/priority` + preferred helper |
| D | Terminal Set priority + 契约 |

## 2. 核心不变量

- 默认 `100`；越小越优先  
- 任一 active issuer 仍可通过 enforce  
- body 禁止 `tenant_id` / `platform_scope`  

## 3. 自动化证据

- 本地完整回归：`603 passed`（`tests/contracts`）  
- Alembic head：`0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0097 |
| Constitution Review | 通过；Gateway / platform 边界 |
| Cross-reference Review | 通过；G66–G77 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | claim/MFA、social login、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Claim 映射 / MFA / 完整策略引擎  
- Social login / OIDC 多 issuer 登录重定向  
- 多区域生产 SaaS / failover  

## 6. 证据索引

- [PHX-G78 Architecture Gate](PHX-G78_ARCHITECTURE_GATE.md)
- [ADR-0097](../decisions/ADR-0097-tenant-idp-federation-issuer-priority.md)
