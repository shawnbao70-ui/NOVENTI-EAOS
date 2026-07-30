# PHX-G113 Twin Status / Snapshot Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Twin  
**规范源：** ADR-0132  
**人工确认：** 支付清算另批；authorize/Brain Terminal 另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Twin 状态与 snapshot upsert/get 做薄接线；authorize 仍 fail-closed。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/twin/status` 只读 |
| UI | Twin status / Upsert snapshot / Get snapshot |
| API | 仅调用既有 snapshots；不接线 authorize |
| Out | Brain Terminal；支付清算；Role→grant |

## 3. Exit Criteria

1. ADR-0132 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G113_ACCEPTANCE.md](PHX-G113_ACCEPTANCE.md)。
