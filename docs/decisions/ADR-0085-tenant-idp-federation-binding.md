# ADR-0085 — Tenant IdP Federation Binding (Thin API)

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G66  
**归属：** Platform API Gateway / Identity boundary

## 背景

平台 IdP 注册表（G56+）为全局目录。组织联邦需最小租户↔issuer 允许绑定，且默认不破坏现有单租户 OIDC。

## 决策

1. 进程内绑定存储：`(tenant_id, issuer)` + `status` ∈ `{active,disabled}` + `version`。  
2. 平台面薄 API（`derive_platform_context`）：  
   - `GET/POST /v1/platform/idp/federation/tenants/{tenant_id}/bindings`  
   - `POST /v1/platform/idp/federation/bindings/{id}/unbind`  
3. Body 禁止 `tenant_id` / `platform_scope`（路径承载租户）；不回传密钥。  
4. `EAOS_TENANT_IDP_FEDERATION=0|1`（默认 `0`）：开启后 OIDC 与租户面 JWT fail-closed（JWT 见 ADR-0087）。  
5. `/v1/auth/oidc/status` 暴露 `tenant_idp_federation`（bool）。  
6. 默认 memory；SQL 见 ADR-0086；联邦 UI / 社交登录另切片；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 组织联邦 UI / 策略矩阵 / social login  
- 网格 CRD / 多区域 / KMS  

## 关联

- [ADR-0075-multi-idp-write-registry.md](ADR-0075-multi-idp-write-registry.md)
- [ADR-0081-platform-idp-registry-terminal-ops.md](ADR-0081-platform-idp-registry-terminal-ops.md)
- [../project/PHX-G66_ARCHITECTURE_GATE.md](../project/PHX-G66_ARCHITECTURE_GATE.md)
