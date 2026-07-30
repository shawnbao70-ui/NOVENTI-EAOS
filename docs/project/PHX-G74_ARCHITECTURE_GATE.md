# PHX-G74 OIDC Refresh Fernet Key Provider Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0093  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可插拔密钥来源 env|file；默认 env；云 KMS 另批。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_OIDC_REFRESH_KEY_PROVIDER` |
| Default | `env` |
| File | `*_KEY_FILE` / `*_PREVIOUS_KEYS_FILE` |
| Status | `refresh_encrypt_key_provider` |

## 3. Exit Criteria

1. ADR-0093 Accepted。  
2. file/env 可测；kms fail-closed；契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G74_ACCEPTANCE.md](PHX-G74_ACCEPTANCE.md)。
