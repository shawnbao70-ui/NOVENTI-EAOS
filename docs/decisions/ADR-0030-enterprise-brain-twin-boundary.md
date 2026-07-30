# ADR-0030 — Enterprise Brain 与 Digital Twin 边界

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-E15  
**归属：** Shared Platform Capability / Enterprise Brain · Digital Twin

## 背景

BOOK14/BOOK18/BOOK23 要求 Enterprise Brain 仅产生带 provenance 的洞察、建议与模拟，Digital Twin 是受治理映像而非执行授权。PHX-E15 退出门禁为「建议与执行权分离」。

## 决策

### 1. Ownership 与落点

- Digital Twin：`eaos_platform.twin` — 租户内受治理状态映像（snapshot）。
- Enterprise Brain：`eaos_platform.brain` — 洞察 / 建议 / 模拟（advisory）。
- 二者均不属 Core Kernel、Smart Terminal、Business Package 或 Marketplace。
- Knowledge / AI Runtime / Workflow 仍为其各自真相源；Brain/Twin 只读消费授权数据。

### 2. Digital Twin

- `UpsertTwinSnapshot` 强制 provenance（source_ref + reason）、置信度 ∈ [0,1]、租户隔离。
- Twin 状态变更可追溯；禁止秘密字段。
- Twin / 模拟 **不构成** 执行授权；无 commit/execute API。

### 3. Enterprise Brain

- `PublishInsight` 产出 `insight | recommendation | simulation`，永久 `advisory=true`。
- 必须携带置信度、provenance、可选 `twin_ref` / knowledge 引用与偏差说明。
- **禁止** 任何从 insight/recommendation/simulation 直接 Commit / Invoke / Authorize 的 API。
- 显式 `request_execution` → `BRAIN_EXECUTION_FORBIDDEN`（须改走 AI Runtime / Terminal / Workflow）。

### 4. 建议与执行权分离

```text
Twin / Brain output  →  advisory only
Commit / Tool / Approval  →  Workflow + Permission +（如需）AI Runtime / Terminal
```

模拟转为执行必须重新求值权限与审批；本里程碑在 Brain/Twin 内直接拒绝执行路径。

## Explicit Defer

- 向量推理引擎与多模型编排产品化
- 连续孪生同步管线 / 高频遥测
- Enterprise Brain → Terminal 完整 UX
- Marketplace 洞察包分发
- FastAPI Router

## 关联

- [ADR-0025-knowledge-shared-capability.md](ADR-0025-knowledge-shared-capability.md)
- [ADR-0027-ai-runtime-boundary.md](ADR-0027-ai-runtime-boundary.md)
- [ADR-0028-smart-terminal-boundary.md](ADR-0028-smart-terminal-boundary.md)
- [../project/PHX-E15_ARCHITECTURE_GATE.md](../project/PHX-E15_ARCHITECTURE_GATE.md)
