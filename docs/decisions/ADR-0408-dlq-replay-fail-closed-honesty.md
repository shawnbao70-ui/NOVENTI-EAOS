# ADR-0408 — DLQ / Replay Fail-Closed Honesty

**状态：** Accepted（PHX-G383）  
**日期：** 2026-07-27  
**里程碑：** PHX-G383  
**授权源：** [Coding Authorization](../project/DLQ_REPLAY_FAIL_CLOSED_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Dead-letter list/replay 与 event replay 保持 `event_stream` permission-gated；
   无 grant / 无受信头时 fail-closed（401/403），不提供 ungated bypass。
2. `GET /v1/events/status` 以 closed schema 声明该姿态；不 invent 开放 DLQ API。
3. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
