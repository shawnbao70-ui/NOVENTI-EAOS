# ADR-0089 — OIDC Refresh Re-encrypt On Read

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G70  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G65 提供旧密钥解密窗口，但密文不会自动迁到新主密钥。需可选读时重加密以缩短旧密钥依赖窗口。

## 决策

1. `EAOS_OIDC_REFRESH_REENCRYPT_ON_READ=0|1`（默认 `0`）。  
2. 仅在加密开启时生效；`get` 路径：若字段密文不能被**仅主密钥**解密但可被 MultiFernet 解密，则用主密钥 re-seal 写回。  
3. `pop` 不重写（即将删除）。  
4. `/v1/auth/oidc/status` 暴露 `refresh_reencrypt_on_read`（bool）。  
5. 无 Alembic；密钥提供方见 ADR-0093；云 KMS 适配器另切片；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 云 KMS 适配器 / 批量离线迁移作业  
- 多区域  

## 关联

- [ADR-0084-oidc-refresh-key-rotation.md](ADR-0084-oidc-refresh-key-rotation.md)
- [../project/PHX-G70_ARCHITECTURE_GATE.md](../project/PHX-G70_ARCHITECTURE_GATE.md)
