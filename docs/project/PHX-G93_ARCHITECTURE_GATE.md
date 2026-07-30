# PHX-G93 Permission Roles Status Observability Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission / Smart Terminal  
**规范源：** ADR-0112  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

只读暴露角色目录与 opt-in grant map 运行态摘要，供运维探针；Terminal Admin 薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | `GET /v1/permission/roles/status`（租户上下文） |
| 内容 | store 标签、catalog/grant_map 启用与计数；无 secret |
| UI | Admin「Roles status」 |
| Write | 禁止；不解析/不下发原始 env 密文以外的配置串 |

## 3. Exit Criteria

1. ADR-0112 Accepted。  
2. 契约绿；Terminal 控件绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G93_ACCEPTANCE.md](PHX-G93_ACCEPTANCE.md)。
