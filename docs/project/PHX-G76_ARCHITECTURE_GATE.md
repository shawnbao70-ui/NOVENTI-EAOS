# PHX-G76 Deploy Region Identity Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Ops / Gateway  
**规范源：** ADR-0095  
**人工确认：** 支付清算另批；非 multi-region SaaS  

## 1. 门禁目标

可选部署区域身份标签；status/release 可观测；Helm/Compose 可接线；默认未标注仍合法。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_DEPLOY_REGION` |
| Helm | `region.id` + optional label |
| Surface | `/v1/release` → `deploy_region` |
| Non-goal | failover / 副本 / 跨区域 SaaS |

## 3. Exit Criteria

1. ADR-0095 Accepted。  
2. 未设置时 `deploy_region=null`；设置时可观测。  
3. 契约绿；包 `0.2.0`；Alembic `0027`。  

见 [PHX-G76_ACCEPTANCE.md](PHX-G76_ACCEPTANCE.md)。
