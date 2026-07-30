# ADR-0088 — Tenant IdP Federation Terminal Ops

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G69  
**归属：** Smart Terminal / Platform API Gateway interaction boundary

## 背景

G66–G68 已提供租户联邦绑定 API 与 OIDC/JWT 强制。Terminal Admin 仍缺薄操作面。

## 决策

1. Terminal Admin 增加联邦绑定薄操作：List / Bind / Unbind。  
2. 调用既有 `/v1/platform/idp/federation/*`；**platform** 上下文（开发态无租户头）或 platform-scope Bearer。  
3. UI 用独立输入框收集 path 用 `tenant_id`（`#fedTenantId`），**禁止**写入 JSON body；body 仅 `{issuer}`。  
4. 不新增 Gateway 规则；无 Alembic；包版本仍 `0.2.0`。  
5. 非目标：社交登录、租户面 CRUD；矩阵见 ADR-0096。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Social login / 策略引擎  
- 多区域生产 SaaS  

## 关联

- [ADR-0085-tenant-idp-federation-binding.md](ADR-0085-tenant-idp-federation-binding.md)
- [ADR-0081-platform-idp-registry-terminal-ops.md](ADR-0081-platform-idp-registry-terminal-ops.md)
- [ADR-0096-tenant-idp-federation-matrix.md](ADR-0096-tenant-idp-federation-matrix.md)
- [../project/PHX-G69_ARCHITECTURE_GATE.md](../project/PHX-G69_ARCHITECTURE_GATE.md)
