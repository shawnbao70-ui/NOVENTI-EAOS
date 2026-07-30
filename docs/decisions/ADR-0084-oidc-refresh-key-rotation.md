# ADR-0084 — OIDC Refresh Fernet Key Rotation Window

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G65  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G64 仅支持单 Fernet 密钥。运维轮换时需在窗口内同时解密旧密文，同时仅用新主密钥加密。

## 决策

1. 主密钥仍为 `EAOS_OIDC_REFRESH_FERNET_KEY`（加密与解密）。  
2. 可选 `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS`：逗号分隔的旧密钥列表，**仅参与解密**。  
3. 使用 `cryptography.fernet.MultiFernet`：首钥加密；环内全部密钥可解密。  
4. `/v1/auth/oidc/status` 暴露 `refresh_encrypt_key_count`（整数；加密关闭时为 `0`）；永不回传密钥材料。  
5. 无效密钥 fail-closed；无 Alembic 变更；包版本仍 `0.2.0`。  
6. 读时重加密见 ADR-0089；外部 KMS 另切片。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 外部 KMS  
- 组织级联邦 UI / 网格 CRD / 多区域  

## 关联

- [ADR-0083-oidc-refresh-encrypt.md](ADR-0083-oidc-refresh-encrypt.md)
- [../project/PHX-G65_ARCHITECTURE_GATE.md](../project/PHX-G65_ARCHITECTURE_GATE.md)
