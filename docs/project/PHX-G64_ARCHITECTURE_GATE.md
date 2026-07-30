# PHX-G64 OIDC Refresh Token Field Encryption Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0083  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选 Fernet 加密 refresh/id_token 字段；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_OIDC_REFRESH_ENCRYPT` |
| Key | `EAOS_OIDC_REFRESH_FERNET_KEY` |
| Default | off |
| Cipher | Fernet + `eaos1:` 前缀 |
| Schema | 无变更（复用 `0026` Text 列） |

## 3. Exit Criteria

1. ADR-0083 Accepted。  
2. 加密开关可测；缺密钥 fail-closed；契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G64_ACCEPTANCE.md](PHX-G64_ACCEPTANCE.md)。
