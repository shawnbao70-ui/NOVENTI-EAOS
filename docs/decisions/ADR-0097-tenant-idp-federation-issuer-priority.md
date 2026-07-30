# ADR-0097 — Tenant IdP Federation Issuer Priority

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G78  
**归属：** Platform API Gateway / Persistence

## 背景

G66–G77 允许多 issuer 绑定与矩阵观测，但无偏好序。需在绑定上增加可运维的优先级，而不引入 claim/MFA 策略引擎。

## 决策

1. 绑定字段 `priority: int`（默认 `100`；**数值越小越优先**；`>= 0`）。  
2. Platform `POST /v1/platform/idp/federation/bindings/{id}/priority`，body 仅 `{priority}`。  
3. List / matrix 按 `(tenant, priority, issuer)` 排序；序列化含 `priority`。  
4. 提供只读 `preferred_active_issuer(tenant_id)`；**不改变** `assert_tenant_idp_binding` 放行语义（任一 active issuer 仍通过）。  
5. Alembic `0028_tenant_idp_binding_priority_g78`；memory|sql 对等。  
6. Terminal Admin 薄操作 Set priority；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Claim 映射 / MFA / 策略引擎  
- Social login / OIDC 多 issuer 登录重定向  
- 多区域生产 SaaS / failover  

## 关联

- [ADR-0085-tenant-idp-federation-binding.md](ADR-0085-tenant-idp-federation-binding.md)
- [ADR-0096-tenant-idp-federation-matrix.md](ADR-0096-tenant-idp-federation-matrix.md)
- [../project/PHX-G78_ARCHITECTURE_GATE.md](../project/PHX-G78_ARCHITECTURE_GATE.md)
