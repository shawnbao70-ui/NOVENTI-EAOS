# ADR-0055 — JWT JWKS / RS256 Verification

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G38  
**归属：** Platform API Gateway / Identity boundary

## 背景

ADR-0053 交付 HS256 Bearer 派生。已批准的 OIDC 产品化下一刀为 JWKS 多密钥与 RS256 校验，仍不在本切片实现 Authorization Code 登录页。

## 决策

1. `Authorization: Bearer` 校验按 `alg` 分流：`HS256`（`EAOS_JWT_SECRET`）与 `RS256`（JWKS）。  
2. JWKS 来源（择一或并用）：  
   - `EAOS_JWT_JWKS_JSON` — 内联 JWKS 文档  
   - `EAOS_JWT_JWKS_URL` — HTTPS 拉取（短 TTL 缓存）  
3. 密钥选择：优先 `kid` 匹配；无 `kid` 时仅当 JWKS 恰有一把 RSA 公钥。  
4. 声明映射与提升拒绝规则仍遵循 ADR-0053。  
5. 依赖：`cryptography`（api extra）用于 RSA 校验。

## Explicit Defer

- OIDC Authorization Code / 登录页 / Session Cookie（见 ADR-0058）  
- 多发行方 JWKS allowlist（见 ADR-0064 / PHX-G45）  
- 密钥吊销列表（Foundation 见 ADR-0065 / PHX-G46）  
- ES256 / EdDSA

## 关联

- [ADR-0053-jwt-oidc-trusted-context.md](ADR-0053-jwt-oidc-trusted-context.md)
- [../project/PHX-G38_ARCHITECTURE_GATE.md](../project/PHX-G38_ARCHITECTURE_GATE.md)
