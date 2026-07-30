# ADR-0135 — Brain Execute Fail-Closed Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G116  
**归属：** Smart Terminal / Brain

## 背景

G115 已覆盖 Brain 状态与 insight publish/get。运维仍需在 Terminal 内显式验证 execute 恒 fail-closed，而不打开执行路径。

## 决策

1. Terminal Admin 增加 Execute brain insight（expect 403）。  
2. 仅调用既有 `POST /v1/brain/insights/{id}/execute`；期望 HTTP 403 / `BRAIN_EXECUTION_FORBIDDEN`。  
3. UI 展示 fail-closed 观测结果；禁止上下文提升；不放宽执行权。  
4. Brain Terminal 运维面齐；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- 打开 Brain execute 执行权  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  
- Role→Policy 绑定  

## 关联

- [ADR-0134-brain-status-insight-probe.md](ADR-0134-brain-status-insight-probe.md)
- [../project/PHX-G116_ARCHITECTURE_GATE.md](../project/PHX-G116_ARCHITECTURE_GATE.md)
