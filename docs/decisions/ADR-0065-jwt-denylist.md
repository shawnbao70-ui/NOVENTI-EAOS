# ADR-0065 — JWT Denylist / Revocation (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G46  
**归属：** Platform API Gateway / Identity boundary

## 背景

G45 交付多发行方 JWKS。仍缺可运营的令牌吊销：被盗用或下线会话需在签名仍有效时拒绝。支付清算另批；本切片仅身份边界。

## 决策

1. Gateway 在签名与 `iss`/`aud`/`exp` 校验通过后检查 denylist。  
2. 配置（可空；空则不启用）：  
   - `EAOS_JWT_DENYLIST_JSON` — 条目数组  
   - `EAOS_JWT_DENYLIST_URL` — HTTPS 拉取（短 TTL 缓存；JSON 优先）  
3. 条目形态：`{"jti":"..."}` 或 `{"jti":"...","iss":"..."}`；可选 `exp`（条目过期后忽略）。亦接受纯 `jti` 字符串。  
4. 命中 → `GATEWAY_JWT_REVOKED`（401）。无 `jti` 的令牌无法被 denylist 命中（不强制所有令牌带 `jti`）。  
5. 无 Alembic / DB 注册表；进程内缓存 URL 文档。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 分布式实时吊销总线 / Redis  
- IdP Discovery 产品化 UI  
- 全量 CRL 标准互操作  

## 关联

- [ADR-0064-jwt-multi-issuer-jwks.md](ADR-0064-jwt-multi-issuer-jwks.md)
- [../project/PHX-G46_ARCHITECTURE_GATE.md](../project/PHX-G46_ARCHITECTURE_GATE.md)
