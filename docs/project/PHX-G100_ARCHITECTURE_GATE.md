# PHX-G100 Terminal Event Subscribe/Replay Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Event Bus  
**规范源：** ADR-0119  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 `POST /v1/events/subscriptions` 与 `POST /v1/events/{id}/replay` 做薄运维探针，补齐 G97–G99 Event 面。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Subscribe + Replay event |
| API | 仅调用既有 subscriptions / event replay |
| Body | subscriber_id + event_name；可选 delivery_url；不下发/不回显 signing_secret |
| Out | 支付清算；完整 Webhook 密钥管理台 |

## 3. Exit Criteria

1. ADR-0119 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G100_ACCEPTANCE.md](PHX-G100_ACCEPTANCE.md)。
