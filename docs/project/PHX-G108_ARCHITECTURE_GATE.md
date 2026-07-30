# PHX-G108 Package Status / Manifest / Surfaces Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package  
**规范源：** ADR-0127  
**人工确认：** 支付清算另批；publish/install 另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Package 做状态 + manifest 注册/读取 + surfaces 列表薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/packages/status` 只读 |
| UI | status / register / get manifest / list surfaces |
| API | 仅调用既有 manifests / surfaces |
| Out | publish / install / disable / resolve；支付清算 |

## 3. Exit Criteria

1. ADR-0127 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G108_ACCEPTANCE.md](PHX-G108_ACCEPTANCE.md)。
