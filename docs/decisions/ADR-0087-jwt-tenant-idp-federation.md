# ADR-0087 — JWT Tenant IdP Federation Enforcement

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G68  
**归属：** Platform API Gateway / Identity boundary

## 背景

G66 仅在 OIDC 映射路径强制租户↔issuer 绑定。租户面 Bearer JWT 仍可绕过绑定。

## 决策

1. 同一开关 `EAOS_TENANT_IDP_FEDERATION`：开启后在 `context_from_tenant_claims`（租户面）fail-closed。  
2. 绑定 issuer 解析：优先 `eaos_oidc_issuer`；否则若 `iss` 不等于配置的 EAOS JWT `issuer` 则用 `iss`；否则视为缺少联邦 provenance → deny。  
3. 平台面 JWT / 开发受信头不强制（控制面与开发旁路保持可运维）。  
4. `/v1/auth/idp/status` → `federation.planes` 含 `oidc` 与 `jwt`；包版本仍 `0.2.0`。  
5. 无 Alembic 变更；联邦 UI 另切片。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 联邦 UI / social login  
- 网格 CRD / 多区域 / KMS  

## 关联

- [ADR-0085-tenant-idp-federation-binding.md](ADR-0085-tenant-idp-federation-binding.md)
- [../project/PHX-G68_ARCHITECTURE_GATE.md](../project/PHX-G68_ARCHITECTURE_GATE.md)
