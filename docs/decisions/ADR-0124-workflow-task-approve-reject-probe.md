# ADR-0124 — Workflow Task Approve / Reject Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G105  
**归属：** Smart Terminal / Workflow

## 背景

G104 已覆盖 Workflow 状态与定义/实例/任务只读薄探针。运维仍缺 Terminal 内对既有任务 approve/reject 写路径的薄调用面；signal/cancel/compensate/escalate 另批。

## 决策

1. Terminal Admin 增加「Approve workflow task」「Reject workflow task」薄控件。  
2. 仅调用既有 `POST .../tasks/{task_id}/approval` 与 `.../rejection`。  
3. instance_id / task_id 经独立输入（可由 start/list 回填）；禁止 body 上下文提升。  
4. 审批真相仍归 Workflow Kernel；壳不裁决。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal signal / cancel / compensate / escalate UI  
- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0123-workflow-status-definition-instance-probe.md](ADR-0123-workflow-status-definition-instance-probe.md)
- [ADR-0038-gateway-workflow-http-surface.md](ADR-0038-gateway-workflow-http-surface.md)
- [../project/PHX-G105_ARCHITECTURE_GATE.md](../project/PHX-G105_ARCHITECTURE_GATE.md)
