# PHX-G70 OIDC Refresh Re-encrypt On Read Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0089  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选读时将旧密钥密文迁到主密钥；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_OIDC_REFRESH_REENCRYPT_ON_READ` |
| Hook | `get_oidc_session` |
| Detect | 主密钥 Fernet 解密失败且 MultiFernet 成功 |
| Status | `refresh_reencrypt_on_read` |

## 3. Exit Criteria

1. ADR-0089 Accepted。  
2. 旧密文 get 后迁主密钥；契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G70_ACCEPTANCE.md](PHX-G70_ACCEPTANCE.md)。
