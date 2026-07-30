# PHX-G84 OIDC Multi-Provider Login Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0103  
**人工确认：** 支付清算另批；无完整社交品牌 UX / MFA 注册 / per-provider refresh  

## 1. 门禁目标

可选多 IdP 登录目录 + `?provider=`；默认关闭；共享主 redirect。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_OIDC_LOGIN_PROVIDERS`（空=off） |
| API | `/login?provider=` + `/providers` |
| State | `provider_key` 绑定 callback overlay |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0103 Accepted。  
2. 空目录行为不变；已知 provider 换发；未知 400。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G84_ACCEPTANCE.md](PHX-G84_ACCEPTANCE.md)。
