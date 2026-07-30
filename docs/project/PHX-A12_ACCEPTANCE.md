# PHX-A12 AI Runtime & Agent Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform Runtime / AI Runtime  
**退出门禁：** AI 不越权且可解释

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | AgentRun / Tool / Memory 内存服务 |
| B | RequestApproval / CommitAction / AccessKnowledge |
| C | SQLAlchemy + TransactionalAIRuntimeService + Alembic `0016` |
| D | OpenAPI / 状态机 / PostgreSQL / 七步自审 |

## 2. 核心不变量

- AI 操作经 `runtime/ai`；非 AI 主体创建 run → `AI_RUNTIME_REQUIRED`
- 工具 Invoke 经 Permission；未授权 → `AI_TOOL_DENIED`
- high_impact / Commit 经 Workflow 批准双闸门
- Memory 租户隔离、禁秘密；≠ Knowledge
- 动作可审计（run_id + correlation_id）

## 3. 自动化证据

- 本地完整回归：`251 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`15 passed`（`tests/integration`）
- Alembic head：`0016_ai_runtime_a12`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0008/0027 |
| Constitution Review | 通过；BOOK03/10/17/19 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 阻断项关闭；模型/沙箱/Brain/Terminal 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- LLM 提供商与提示词库
- 多 Agent 编排产品化
- 工具沙箱 / 包执行引擎
- Memory 向量长期分层
- Smart Terminal、Enterprise Brain、FastAPI Router

## 6. 证据索引

- [PHX-A12 Architecture Gate](PHX-A12_ARCHITECTURE_GATE.md)
- [ADR-0027](../decisions/ADR-0027-ai-runtime-boundary.md)
- [AI Runtime Interface](../architecture/AI_RUNTIME_INTERFACE.md)
- [AI Runtime State Machines](../architecture/AI_RUNTIME_STATE_MACHINES.md)
- [AI OpenAPI](../api/ai.openapi.yaml)
