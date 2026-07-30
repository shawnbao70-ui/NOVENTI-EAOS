# ADR-0064 — JWT Multi-Issuer JWKS Allowlist (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G45  
**归属：** Platform API Gateway / Identity boundary

## 背景

G38 支持单 issuer + 全局 JWKS（含 `kid`）。生产常有多个 IdP；未知 `iss` 在未配置单 issuer 时曾可放行。需 fail-closed 的多发行方绑定与轮换刷新。

## 决策

1. 新增 `EAOS_JWT_ISSUERS_JSON`：发行方数组，每项含 `issuer` 与 `jwks_json` 和/或 `jwks_url`。  
2. 当该数组非空时进入多发行方模式：  
   - RS256 按 `iss` 选择 JWKS；未知/缺失 `iss` → `GATEWAY_JWT_INVALID`  
   - HS256 仍用全局 `EAOS_JWT_SECRET`，但 `iss` 必须在 allowlist  
3. 单发行方旧环境变量（`EAOS_JWT_ISSUER` / `EAOS_JWT_JWKS_*`）在 issuers 为空时保持兼容。  
4. URL JWKS：`kid` 未命中时强制刷新缓存一次后再失败（轮换窗口）。  
5. 无 schema / Alembic 变更。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- IdP 联邦管理 UI（Discovery / JWKS wire Foundation 见 ADR-0066/0067）  
- 吊销列表（Foundation 见 ADR-0065 / PHX-G46；分布式实时总线仍延后）  
- ES256 / EdDSA  

## 关联

- [ADR-0055-jwt-jwks-rs256.md](ADR-0055-jwt-jwks-rs256.md)
- [../project/PHX-G45_ARCHITECTURE_GATE.md](../project/PHX-G45_ARCHITECTURE_GATE.md)
