# PHX-G65 OIDC Refresh Fernet Key Rotation Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0084  
**人工确认：** 支付清算另批  

## 1. 门禁目标

主密钥加密 + 旧密钥解密窗口；默认行为与 G64 兼容。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Primary | `EAOS_OIDC_REFRESH_FERNET_KEY` |
| Previous | `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS`（逗号分隔） |
| Crypto | `MultiFernet` |
| Status | `refresh_encrypt_key_count` |
| Schema | 无变更 |

## 3. Exit Criteria

1. ADR-0084 Accepted。  
2. 旧密文在窗口内可解密；新写入用主密钥；契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G65_ACCEPTANCE.md](PHX-G65_ACCEPTANCE.md)。
