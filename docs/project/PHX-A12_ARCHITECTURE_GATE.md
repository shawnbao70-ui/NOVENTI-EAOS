# PHX-A12 AI Runtime & Agent Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Platform Runtime / AI Runtime  
**规范源：** BOOK03、BOOK10、BOOK17、BOOK19、BOOK22、ADR-0008、ADR-0021、ADR-0027  
**退出门禁：** AI 不越权且可解释

## 1. 门禁目标

交付 AI Runtime 最小垂直切片：Agent Run 生命周期、工具治理、AI Memory、Workflow approval bridge，并证明 Permission + Approval 双闸门与审计可解释性。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Constitutional AI Runtime；实现于 `runtime/ai` |
| Agent Run | planned → running → pending_approval → completed/failed |
| Tools | 声明制；Invoke 经 Permission；high_impact 经 Workflow 批准 |
| Approval | 复用 Workflow；不平行审批状态 |
| Memory | 租户+run 作用域；≠ Knowledge |
| Knowledge | 只读经 Knowledge Capability |
| Explainability | Audit + run 状态 + correlation_id |

## 3. Action / Resource Contract

- `ai.run.create` / `ai.run.read`
- `ai.tool.register` / `ai.tool.invoke`
- `ai.memory.read` / `ai.memory.write`
- `ai.knowledge.read`
- `ai.approval.request` / `ai.action.commit`

资源：

- `ai_run:{run_id}`
- `tool:{tool_name}`
- `ai_memory:{run_id}`

## 4. 实现切片

### Slice A — Domain

- AgentRun / ToolDeclaration / MemoryEntry
- CreateRun / RegisterTool / InvokeTool / Memory R/W

### Slice B — Approval Bridge + Knowledge

- RequestApproval / CommitAction
- AccessKnowledge 委托

### Slice C — Persistence

- SQLAlchemy + Transactional facade + Alembic `0016`

### Slice D — Contracts

- OpenAPI / 状态机 / PostgreSQL / 七步自审

## 5. Exit Criteria

1. AI 动作经 AI Runtime；工具无 Grant 默认拒绝。  
2. high_impact 工具与 CommitAction 无完成批准则失败关闭。  
3. Memory 租户隔离且禁止秘密；与 Knowledge 分离。  
4. Knowledge 访问走治理 Capability。  
5. 关键可审计（run_id + correlation_id）。  
6. OpenAPI / Data Model / Migration / Code 一致。  
7. PostgreSQL 与完整回归通过。

## 6. Explicit Defer

- 模型提供商、多 Agent 编排产品化
- 工具沙箱与包执行引擎
- Memory 向量/长期分层
- Terminal UX、Enterprise Brain、FastAPI Router
