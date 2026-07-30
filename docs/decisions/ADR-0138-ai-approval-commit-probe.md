# ADR-0138 — AI Approval / Commit Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G119  
**归属：** Smart Terminal / AI Runtime

## 背景

G117–G118 已覆盖 AI Runtime 状态、run、tools 与 memory。运维仍缺 Terminal 内对 approval request 与 commit 审批门禁的薄调用面。

## 决策

1. Terminal Admin 增加 Request AI approval、Commit AI action（approval-gated）。  
2. 仅调用既有 `POST /v1/ai/runs/{id}/approvals` 与 `POST /v1/ai/runs/{id}/commits`。  
3. 使用 `ai_employee` trusted header；definition/approver 可回退既有 Workflow/Operator 输入；禁止 body 上下文提升。  
4. Commit 在无审批时期望 403 / `AI_APPROVAL_REQUIRED`；AI Runtime Terminal 运维面齐。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  
- Role→Policy 绑定  
- 打开无审批 commit  

## 关联

- [ADR-0137-ai-tools-memory-probe.md](ADR-0137-ai-tools-memory-probe.md)
- [../project/PHX-G119_ARCHITECTURE_GATE.md](../project/PHX-G119_ARCHITECTURE_GATE.md)
