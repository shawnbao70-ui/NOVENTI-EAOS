# PHX-G109 Package Publish / Install / Disable / Resolve Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package  
**规范源：** ADR-0128  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Package publish/install/disable/resolve 做薄接线；Package Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Publish / Install / Disable / Resolve |
| API | 仅调用既有 G27 路径 |
| Out | 支付清算；Knowledge Terminal 另域 |

## 3. Exit Criteria

1. ADR-0128 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G109_ACCEPTANCE.md](PHX-G109_ACCEPTANCE.md)。
