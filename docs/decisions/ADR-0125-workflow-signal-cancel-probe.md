# ADR-0125 — Workflow Signal / Cancel Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G106  
**归属：** Smart Terminal / Workflow

## 背景

G104–G105 已覆盖 Workflow 状态、定义/实例/任务与 approve/reject。运维仍缺 Terminal 内对既有 instance signal/cancel 的薄调用面；compensate/escalate 另批。

## 决策

1. Terminal Admin 增加「Signal workflow instance」「Cancel workflow instance」薄控件。  
2. 仅调用既有 `POST .../signals` 与 `.../cancellation`。  
3. instance_id 经独立输入；signal 需 `signal_name` + `idempotency_key`；禁止 body 上下文提升。  
4. 审批/状态真相仍归 Workflow Kernel。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal compensate / escalate UI  
- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0124-workflow-task-approve-reject-probe.md](ADR-0124-workflow-task-approve-reject-probe.md)
- [ADR-0038-gateway-workflow-http-surface.md](ADR-0038-gateway-workflow-http-surface.md)
- [../project/PHX-G106_ARCHITECTURE_GATE.md](../project/PHX-G106_ARCHITECTURE_GATE.md)
