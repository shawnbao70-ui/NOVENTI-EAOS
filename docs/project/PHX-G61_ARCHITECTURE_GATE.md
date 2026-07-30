# PHX-G61 OIDC Refresh + RP-Logout Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0080  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in Refresh 与 RP-Logout；本地 jti revoke；Terminal 薄操作；无联邦 UI。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Refresh switch | `EAOS_OIDC_REFRESH` |
| Logout switch | `EAOS_OIDC_RP_LOGOUT` |
| Binding | 进程内 `jti` → refresh/id_token |
| Revoke | runtime denylist（G46 兼容） |
| Terminal | Refresh / Logout 按钮 |

## 3. Exit Criteria

1. ADR-0080 Accepted。  
2. API + status + Terminal + 契约绿；包 `0.2.0`。  
3. 全量 contracts 绿。  

见 [PHX-G61_ACCEPTANCE.md](PHX-G61_ACCEPTANCE.md)。
