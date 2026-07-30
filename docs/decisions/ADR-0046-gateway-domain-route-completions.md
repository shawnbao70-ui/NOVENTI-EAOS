# ADR-0046 — Gateway Domain Route Completions

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G31  
**归属：** Platform API Gateway

## 背景

G20–G30 已交付各域主路径 HTTP。OpenAPI 中仍有明确延后的扩展操作：Workflow 生命周期、Knowledge archive/share、Permission deprecate/delegate。

## 决策

### 1. 本切片补齐

| 域 | 路由 |
|----|------|
| Workflow | definition deprecation；instance signal/cancel/compensate；task escalation |
| Knowledge | entity archive；entity share |
| Permission | policy deprecation；grant delegation |

### 2. 边界不变

- 仍为薄适配；业务规则归 Kernel / Capability
- `derive_tenant_context` + `reject_context_override`
- OpenAPI 要求但 Kernel 未使用的字段（如部分 reason/expected_version）可接受于 body，不在网关内解释为业务语义

### 3. Explicit Defer

- Organization 其余企业/成员生命周期补齐（另切片）
- JWT/OIDC；Marketplace 商业；完整 Terminal UI

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G31_ARCHITECTURE_GATE.md](../project/PHX-G31_ARCHITECTURE_GATE.md)
