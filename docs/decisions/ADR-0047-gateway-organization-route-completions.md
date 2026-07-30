# ADR-0047 — Gateway Organization Route Completions

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G32  
**归属：** Platform API Gateway

## 背景

G21/G25 已交付 Organization 租户面主路径与平台租户生命周期。OpenAPI 仍缺企业/单元/成员扩展操作的 HTTP 薄适配。

## 决策

### 1. 本切片补齐（租户面）

| 区域 | 路由 |
|------|------|
| Enterprise | GET；DELETE close；POST/DELETE suspension |
| Org Unit | GET tree；PUT status |
| Membership | DELETE end；PUT unit transfer；POST/DELETE suspension |

### 2. 边界不变

- `derive_tenant_context` + `reject_context_override`
- 平台租户仍仅 `/v1/platform/*`（G25）
- 网关不宿主业务规则

### 3. Explicit Defer

- JWT/OIDC；Marketplace 商业；完整 Terminal UI

## 关联

- [ADR-0036-gateway-organization-http-surface.md](ADR-0036-gateway-organization-http-surface.md)
- [ADR-0040-gateway-platform-tenant-http.md](ADR-0040-gateway-platform-tenant-http.md)
- [../project/PHX-G32_ARCHITECTURE_GATE.md](../project/PHX-G32_ARCHITECTURE_GATE.md)
