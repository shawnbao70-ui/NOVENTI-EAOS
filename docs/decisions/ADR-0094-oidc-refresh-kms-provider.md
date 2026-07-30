# ADR-0094 — OIDC Refresh KMS Key Provider

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G75  
**归属：** Platform API Gateway / Persistence boundary

## 背景

ADR-0093 将 `kms` 标为 Foundation fail-closed。需可插拔云 KMS / HTTP 密钥后端，仍保持 Fernet 字段加密与 Gateway 薄边界。

## 决策

1. `EAOS_OIDC_REFRESH_KEY_PROVIDER=kms` 合法；须同时设 `EAOS_OIDC_REFRESH_KMS_BACKEND=http|aws|gcp|azure`。  
2. **http**：`GET EAOS_OIDC_REFRESH_KMS_HTTP_URL`；正文为 Fernet 主密钥单行，或 JSON `{"primary":"...","previous":["..."]}`；可选 `EAOS_OIDC_REFRESH_KMS_HTTP_BEARER`。  
3. **aws / gcp / azure**：用 KMS Decrypt/Unwrap 解出 Fernet 密钥材料；密文 `EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64`；各后端专用 key 标识 env（见拓扑表）。SDK 为可选依赖，未安装则 fail-closed 明示。  
4. 进程内缓存解出的密钥环；永不经 status/日志回传密钥材料。  
5. status 暴露 `refresh_encrypt_key_provider=kms` 与 `refresh_encrypt_kms_backend`。  
6. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 多区域 KMS 复制 / 自动轮换作业  
- 将 boto3 / google-cloud-kms / azure-keyvault 纳入默认依赖  

## 关联

- [ADR-0093-oidc-refresh-key-provider.md](ADR-0093-oidc-refresh-key-provider.md)
- [../project/PHX-G75_ARCHITECTURE_GATE.md](../project/PHX-G75_ARCHITECTURE_GATE.md)
