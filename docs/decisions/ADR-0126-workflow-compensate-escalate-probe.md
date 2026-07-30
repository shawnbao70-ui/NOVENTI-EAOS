# ADR-0126 — Workflow Compensate / Escalate Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G107  
**归属：** Smart Terminal / Workflow

## 背景

G104–G106 已覆盖 Workflow 状态、定义/实例/任务、approve/reject 与 signal/cancel。运维仍缺 Terminal 内对既有 compensate 与 task escalate 的薄调用面。

## 决策

1. Terminal Admin 增加「Compensate workflow instance」「Escalate workflow task」薄控件。  
2. 仅调用既有 `POST .../compensation` 与 `.../tasks/{task_id}/escalation`。  
3. path id 经独立输入；escalate 需 `to_subject_id` + `reason`；禁止 body 上下文提升。  
4. 状态真相仍归 Workflow Kernel。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  
- Package / Knowledge Terminal 薄探针（另域切片）  

## 关联

- [ADR-0125-workflow-signal-cancel-probe.md](ADR-0125-workflow-signal-cancel-probe.md)
- [ADR-0038-gateway-workflow-http-surface.md](ADR-0038-gateway-workflow-http-surface.md)
- [../project/PHX-G107_ARCHITECTURE_GATE.md](../project/PHX-G107_ARCHITECTURE_GATE.md)
