# ADR-0079 — OIDC Discovery → IdP Registry Writeback

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G60  
**归属：** Platform API Gateway / Identity boundary

## 背景

G48 将 Discovery `jwks_uri` 注入 JWT allowlist（进程内）。G56/G57 已有可写 IdP 注册表。需可选把 Discovery 结果**持久化到注册表**（非写回进程 env），便于运维可见与 SQL 存储。

## 决策

1. Opt-in：`EAOS_OIDC_DISCOVERY_REGISTRY_WRITE=1`；需 OIDC Discovery 已启用。  
2. 解析 Discovery 后 `upsert` 注册表：`issuer` + `jwks_url=jwks_uri`；HTTPS（loopback 仅测试）。  
3. **不**写进程环境变量；同 issuer 合并规则不变——env / JWKS wire 优先于注册表。  
4. 惰性同步：有效 JWT 设置路径与 `GET /v1/auth/idp/status`；平台面 `POST /v1/platform/idp/discovery/sync` 可强制触发。  
5. status 暴露 `oidc.discovery_registry_write` 与 `registry.discovery_write`（含 action）。  
6. 无新 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Discovery 写回 env 文件  
- 联邦策略 UI / Refresh / RP-Logout  
- 多区域 / 网格 CRD  

## 关联

- [ADR-0067-oidc-discovery-jwks-wire.md](ADR-0067-oidc-discovery-jwks-wire.md)
- [ADR-0075-multi-idp-write-registry.md](ADR-0075-multi-idp-write-registry.md)
- [ADR-0076-idp-registry-sql.md](ADR-0076-idp-registry-sql.md)
- [../project/PHX-G60_ARCHITECTURE_GATE.md](../project/PHX-G60_ARCHITECTURE_GATE.md)
