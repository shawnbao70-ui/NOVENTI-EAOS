# ADR-0053 — JWT/OIDC Trusted Context Derivation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G37  
**归属：** Platform API Gateway / Identity boundary

## 背景

G18–G36 以开发态受信头派生 `ExecutionContext`。用户已批准 JWT/OIDC 产品化：Gateway 认证边界须能校验 Bearer 断言并派生上下文，body 仍不可提升。

## 决策

### 1. 派生优先级

1. `Authorization: Bearer <JWT>` → 校验后从 claims 派生上下文  
2. 若未提供 Bearer 且允许开发头（默认开）→ 既有 `X-EAOS-*` 头路径  
3. 若 `EAOS_REQUIRE_JWT=1` → 拒绝仅头路径

### 2. Claims 映射（租户面）

| Claim | 映射 |
|-------|------|
| `sub` | `subject_id`（UUID） |
| `eaos_tenant_id` | `tenant_id`（UUID） |
| `eaos_subject_type` | `subject_type`（可选，默认 human） |
| `jti` / 头 `X-Correlation-Id` | `correlation_id`（头优先，否则 jti，否则生成） |

平台面 JWT 额外要求 `eaos_platform_scope=true`；租户面 JWT 若带该 claim 且为 true → 拒绝（防头外提升）。

### 3. 校验（本切片）

- HS256 共享密钥（`EAOS_JWT_SECRET`）；可选 `iss` / `aud` / `exp`  
- 不在本切片实现完整 OIDC discovery / JWKS 拉取（预留接口，显式下一刀）

### 4. Explicit Defer

- OIDC Authorization Code 登录页与 IdP 联邦  
- JWKS / RS256 多密钥轮换产品化  
- Marketplace 商业政策（M17）

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G37_ARCHITECTURE_GATE.md](../project/PHX-G37_ARCHITECTURE_GATE.md)
