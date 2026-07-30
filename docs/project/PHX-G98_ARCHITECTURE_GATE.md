# PHX-G98 Terminal Event Dispatch Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Event Bus  
**规范源：** ADR-0117  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 `POST /v1/events/dispatch` 与 `GET /v1/events/{id}` 做薄运维探针，衔接 G97 stats/DLQ。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Dispatch due + Get event |
| API | 仅调用既有 dispatch / get-by-id |
| Body | `worker_id` + optional `limit`；禁止 context 提升 |
| Out | 订阅/Webhook 配置 UI；支付清算 |

## 3. Exit Criteria

1. ADR-0117 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G98_ACCEPTANCE.md](PHX-G98_ACCEPTANCE.md)。
