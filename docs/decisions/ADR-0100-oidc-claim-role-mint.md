# ADR-0100 — OIDC Claim→Role JWT Mint Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G81  
**归属：** Platform API Gateway / OIDC boundary

## 背景

G79/G80 完成声明与 amr/acr 门禁。仍需将 IdP 组/角色声明映射进 EAOS JWT，而不做 Permission Kernel 同步或 SQL 映射表。

## 决策

1. `EAOS_OIDC_ROLE_CLAIM`：IdP 声明名（如 `groups`）；空=关闭。  
2. `EAOS_OIDC_ROLE_MAP`：`idpValue=eaosRole,...`（`=` 分隔，逗号多项）；与 claim 同时非空才启用。  
3. 映射结果写入 EAOS JWT `eaos_roles: string[]`（排序去重）；无命中则省略该 claim。  
4. 可选 `EAOS_OIDC_REQUIRE_MAPPED_ROLE=1`：启用且无映射角色 → `401` + `GATEWAY_OIDC_ROLE_REQUIRED`。  
5. 挂在 `map_oidc_claims_to_eaos`（G79/G80 之后）；status 暴露 `role_claim` / `role_claim_enabled` / `role_map_size` / `require_mapped_role`。  
6. 无 Alembic；不写 Permission grants；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- SQL 映射表 / Permission Kernel 自动授权  
- Social login / MFA 注册 UX  
- `ExecutionContext.roles` 产品化消费（见 ADR-0101 / PHX-G82）  

## 关联

- [ADR-0098-oidc-required-claims-gate.md](ADR-0098-oidc-required-claims-gate.md)
- [ADR-0099-oidc-amr-acr-gate.md](ADR-0099-oidc-amr-acr-gate.md)
- [../project/PHX-G81_ARCHITECTURE_GATE.md](../project/PHX-G81_ARCHITECTURE_GATE.md)
