# ADR-0096 — Tenant IdP Federation Policy Matrix

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G77  
**归属：** Platform API Gateway / Terminal Admin

## 背景

G66–G69 已提供租户↔issuer 绑定与 enforce。运维需要跨租户矩阵视图，而非新策略引擎或租户自助 CRUD。

## 决策

1. Platform 只读 `GET /v1/platform/idp/federation/matrix`：单元格 = `tenant × issuer → active|disabled|unbound`。  
2. 绑定行来自现有 federation store；可选并入 IdP registry 中尚未绑定的 issuer（`state=unbound`，`bound_tenant_id=null`）。  
3. Bind/Unbind 仍走既有路由；矩阵不改变 enforce 语义。  
4. Terminal Admin 增加 Matrix 操作（platform 上下文；body 禁止 `tenant_id` / `platform_scope`）。  
5. `GET /v1/auth/idp/status` → `federation.matrix` 摘要（计数，无密钥）。  
6. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Social login / 租户面 IdP CRUD  
- Claim 映射、MFA、多 issuer 优先级等策略引擎  
- 多区域生产 SaaS / failover  

## 关联

- [ADR-0085-tenant-idp-federation-binding.md](ADR-0085-tenant-idp-federation-binding.md)
- [ADR-0088-tenant-idp-federation-terminal-ops.md](ADR-0088-tenant-idp-federation-terminal-ops.md)
- [../project/PHX-G77_ARCHITECTURE_GATE.md](../project/PHX-G77_ARCHITECTURE_GATE.md)
