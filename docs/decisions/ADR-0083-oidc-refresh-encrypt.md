# ADR-0083 — OIDC Refresh Token Field Encryption

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G64  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G63 允许 refresh/id_token 明文落库。需可选应用层加密，默认关闭以保持兼容。

## 决策

1. `EAOS_OIDC_REFRESH_ENCRYPT=0|1`（默认 `0`）。  
2. 启用时要求 `EAOS_OIDC_REFRESH_FERNET_KEY`（Fernet URL-safe base64 密钥）；缺密钥 fail-closed。  
3. 密文前缀 `eaos1:`；加密覆盖 memory 与 sql store 的 `refresh_token` / `id_token` 字段。  
4. API 行为不变；不在响应回传令牌；`/v1/auth/oidc/status` 暴露 `refresh_encrypt`（`off`|`fernet`）。  
5. 无 Alembic 变更；包版本仍 `0.2.0`。  
6. 多密钥轮换窗口见 ADR-0084；外部 KMS / 读时重加密另切片。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 组织级联邦 UI / 网格 CRD / 多区域  
- 外部 KMS / 读时重加密  

## 关联

- [ADR-0082-oidc-refresh-sql.md](ADR-0082-oidc-refresh-sql.md)
- [../project/PHX-G64_ARCHITECTURE_GATE.md](../project/PHX-G64_ARCHITECTURE_GATE.md)
