# PHX-G62 Platform IdP Registry Terminal Ops Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform API Gateway  
**规范源：** ADR-0081  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Terminal Admin 薄操作复用平台 IdP API；平台上下文；无组织联邦策略引擎。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Terminal Admin only |
| APIs | 既有 `/v1/platform/idp/*` |
| Context | platform headers / platform Bearer |
| Secrets | UI 不展示完整 JWKS / secret |
| Non-goal | 组织级联邦策略 UI |

## 3. Exit Criteria

1. ADR-0081 Accepted。  
2. UI + 契约绿；无新 migration；包 `0.2.0`。  
3. 全量 contracts 绿。  

见 [PHX-G62_ACCEPTANCE.md](PHX-G62_ACCEPTANCE.md)。
