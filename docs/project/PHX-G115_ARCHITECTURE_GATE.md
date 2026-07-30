# PHX-G115 Brain Status / Insight Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Brain  
**规范源：** ADR-0134  
**人工确认：** execute 仍 fail-closed；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Brain 状态与 insight publish/get 做薄接线；execute 仍 fail-closed。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/brain/status` 只读 |
| UI | Brain status / Publish insight / Get insight |
| API | 仅调用既有 insights；不接线 execute |
| Out | 打开执行权；支付清算；Role→grant |

## 3. Exit Criteria

1. ADR-0134 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G115_ACCEPTANCE.md](PHX-G115_ACCEPTANCE.md)。
