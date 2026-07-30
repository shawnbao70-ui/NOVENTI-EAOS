# PHX-G120 Identity Status / Subject Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Identity  
**规范源：** ADR-0139  
**人工确认：** credential/session 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Identity 状态与 subject register/resolve 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/identity/status` 只读 |
| UI | status / Register subject / Resolve subject |
| Out | credentials / sessions；Organization；支付清算 |

## 3. Exit Criteria

1. ADR-0139 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G120_ACCEPTANCE.md](PHX-G120_ACCEPTANCE.md)。
