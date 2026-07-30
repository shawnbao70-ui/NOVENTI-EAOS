# ADR-0137 — AI Tools / Memory Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G118  
**归属：** Smart Terminal / AI Runtime

## 背景

G117 已覆盖 AI Runtime 状态与 run create/get。运维仍缺 Terminal 内对 tool register/invoke 与 memory write/read 的薄调用面。

## 决策

1. Terminal Admin 增加 Register AI tool、Invoke AI tool、Write/Read AI memory。  
2. 仅调用既有 `/v1/ai/tools`、`/runs/{id}/tools/invocations`、`/runs/{id}/memory`。  
3. Register 使用默认 human trusted header；Invoke/Memory 使用 `ai_employee`；禁止 body 上下文提升。  
4. approvals / commits Terminal 探针另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- AI approvals / commits Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0136-ai-status-run-probe.md](ADR-0136-ai-status-run-probe.md)
- [../project/PHX-G118_ARCHITECTURE_GATE.md](../project/PHX-G118_ARCHITECTURE_GATE.md)
