# PHX-G60 OIDC Discovery → Registry Writeback Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0079  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in 将 Discovery `jwks_uri` upsert 进 IdP 注册表；不写 env；env/wire 仍优先。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_OIDC_DISCOVERY_REGISTRY_WRITE` |
| Target | IdP registry（memory\|sql） |
| Env | 不写回 |
| Precedence | env / JWKS wire > registry |
| API | `POST /v1/platform/idp/discovery/sync` |

## 3. Exit Criteria

1. ADR-0079 Accepted。  
2. 写回 + status + 契约绿；无新 migration；包 `0.2.0`。  
3. 全量 contracts 绿。  

见 [PHX-G60_ACCEPTANCE.md](PHX-G60_ACCEPTANCE.md)。
