# PHX-G97 Terminal Event Bus Stats Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Event Bus  
**规范源：** ADR-0116  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 Event Bus stats / dead-letters / replay 做薄运维探针。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Stats / List dead letters / Replay dead letter |
| API | 仅调用既有 `/v1/events/stats`、`/dead-letters`、`.../replay` |
| Auth | 租户受信上下文 |
| Write | 仅 replay（既有语义）；不新建订阅/投递配置 UI |

## 3. Exit Criteria

1. ADR-0116 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G97_ACCEPTANCE.md](PHX-G97_ACCEPTANCE.md)。
