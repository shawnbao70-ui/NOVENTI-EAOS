# ADR-0123 — Workflow Status / Definition / Instance Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G104  
**归属：** Smart Terminal / Workflow

## 背景

G23/G31 已交付 Workflow HTTP 面，但 Smart Terminal Admin 仍缺只读状态与定义/实例/任务薄探针。Marketplace 技术面（G101–G103）已齐；下一薄切片切回 Workflow，不触及审批任务写路径（approve/reject/signal 另批）。

## 决策

1. 新增只读 `GET /v1/workflow/status`（脱敏能力清单；`writable=false`）。  
2. Terminal Admin 增加：Workflow status、Create definition、Start instance、Get instance、List tasks。  
3. 仅调用既有 `/definitions`、`/instances`、`/tasks`；审批真相仍归 Workflow Kernel。  
4. 不实现 Terminal 内 approve/reject/signal/cancel/compensate/escalate。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal 任务审批 / 信号 / 取消 / 补偿 / 升级 UI  
- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0038-gateway-workflow-http-surface.md](ADR-0038-gateway-workflow-http-surface.md)
- [../project/PHX-G104_ARCHITECTURE_GATE.md](../project/PHX-G104_ARCHITECTURE_GATE.md)
