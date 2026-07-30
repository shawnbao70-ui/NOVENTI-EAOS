# ADR-0081 — Platform IdP Registry Terminal Ops

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G62  
**归属：** Smart Terminal / Platform API Gateway interaction boundary

## 背景

G56/G57/G60 已提供平台 IdP 注册表 API 与 Discovery sync；Terminal Admin 仍仅有 G55 只读探针。需薄操作面，不引入组织级联邦策略引擎。

## 决策

1. Terminal Admin 增加平台 IdP 注册表薄操作：List / Register / Disable / Discovery sync。  
2. 调用既有 `/v1/platform/idp/*`；使用 **platform 受信头**（开发态无 `tenant_id`）或具备 platform scope 的 Bearer。  
3. UI 仅收集 `issuer` / `jwks_url` / 可选 `jwks_json` / `issuer id`；**禁止** body 携带 `tenant_id` / `platform_scope`；响应仍脱敏（`has_jwks_json`）。  
4. 不新增 Gateway 业务规则；无 Alembic；包版本仍 `0.2.0`。  
5. 明确非目标：组织级联邦策略矩阵、社交登录、租户面 IdP CRUD。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 组织级联邦策略 UI / social login  
- Refresh 绑定 SQL 持久化  
- 网格 CRD / 多区域  

## 关联

- [ADR-0074-multi-idp-status-ui.md](ADR-0074-multi-idp-status-ui.md)
- [ADR-0075-multi-idp-write-registry.md](ADR-0075-multi-idp-write-registry.md)
- [../project/PHX-G62_ARCHITECTURE_GATE.md](../project/PHX-G62_ARCHITECTURE_GATE.md)
- [../constitution/BOOK23.md](../constitution/BOOK23.md)
