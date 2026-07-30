# PHX-G94 Terminal Permission Evaluate Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**规范源：** ADR-0113  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 `POST /v1/permission/evaluations` 做薄探针，便于验证 grant / role map；可选拉取 explanation。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Admin Evaluate + optional Explain |
| API | 仅调用既有 evaluations / decisions/.../explanation |
| Principal | 受信上下文 subject；禁止 body 冒充 |
| Write | 不创建 grant/policy |

## 3. Exit Criteria

1. ADR-0113 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G94_ACCEPTANCE.md](PHX-G94_ACCEPTANCE.md)。
