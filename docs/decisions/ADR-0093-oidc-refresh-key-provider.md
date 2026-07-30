# ADR-0093 — OIDC Refresh Fernet Key Provider

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G74  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G64–G70 仅从环境变量读取 Fernet 密钥。需可插拔密钥来源，为后续外部 KMS 留缝，且默认行为不变。

## 决策

1. `EAOS_OIDC_REFRESH_KEY_PROVIDER=env|file`（默认 `env`）。  
2. `env`：主密钥 `EAOS_OIDC_REFRESH_FERNET_KEY`；旧密钥 `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS`（逗号分隔）。  
3. `file`：主密钥文件 `EAOS_OIDC_REFRESH_FERNET_KEY_FILE`（单行）；可选 `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE`（每行一钥，`#` 注释）。缺文件 fail-closed。  
4. `kms` 见 ADR-0094（G75 启用云/HTTP 后端）。  
5. `/v1/auth/oidc/status` 暴露 `refresh_encrypt_key_provider`（永不回传密钥材料）。  
6. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 多区域  

## 关联

- [ADR-0083-oidc-refresh-encrypt.md](ADR-0083-oidc-refresh-encrypt.md)
- [ADR-0084-oidc-refresh-key-rotation.md](ADR-0084-oidc-refresh-key-rotation.md)
- [ADR-0094-oidc-refresh-kms-provider.md](ADR-0094-oidc-refresh-kms-provider.md)
- [../project/PHX-G74_ARCHITECTURE_GATE.md](../project/PHX-G74_ARCHITECTURE_GATE.md)
