# ADR-0027 — AI Runtime 边界与审批桥

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-A12  
**归属：** Platform Runtime / AI Runtime（Constitutional Kernel 能力）

## 背景

宪章要求所有 AI 经 AI Runtime，高影响动作双闸门（Permission + Workflow approval）。PHX-005 排除了 AI Runtime；Workflow 已提供 `verify_approved_action`。PHX-A12 需固定实现落点、工具治理、Memory 与 Knowledge 边界。

## 决策

### 1. Ownership 与落点

- Constitutional 能力：AI Runtime（BOOK19）。
- 技术实现：`runtime/ai/`（Platform Runtime 层），不放入 Core Kernel 域包。
- Identity AI Employee / Profile 仍属 Identity；AI Runtime 消费其主体身份，不复制 Grant/Knowledge。

### 2. Agent Run 生命周期

- `CreateAgentRun` 创建租户内受控运行：`planned → running → pending_approval → completed | failed | cancelled`。
- 运行绑定 `subject_id`（AI / AI Employee）与 `correlation_id`；不可跨租户。

### 3. 工具治理

- 工具须先 `RegisterTool`（tenant 作用域声明：name、high_impact）。
- `InvokeTool` 强制 `Permission.Evaluate(action=invoke_tool, resource_type=tool)`。
- `high_impact=true` 的工具在调用前必须通过 Workflow `verify_approved_action`。

### 4. Approval Bridge

- `RequestApproval` → `Workflow.StartInstance`（含 approval binding）；将 `instance_id` 记为 run.`approval_ref`。
- `CommitAction` → Permission（可选业务动作）+ `Workflow.verify_approved_action` + 审计；未批准不得提交。
- 不平行实现审批状态机。

### 5. Memory vs Knowledge

- AI Memory：run/subject 作用域执行上下文；禁止秘密字段；不等于企业知识。
- Knowledge 访问仅经 `eaos_platform.knowledge`；提升为知识必须另走 Knowledge 写入治理。

### 6. 可解释性

- 工具调用、记忆写、审批请求、提交动作均写 Shared Audit，并携带 correlation_id 与 run_id。

## Explicit Defer

- LLM/模型提供商与提示词库
- 多 Agent 编排与劳动力调度完整产品
- 工具沙箱 / 包内工具执行引擎
- Memory 向量分层与长期记忆产品化
- FastAPI Router、Smart Terminal、Enterprise Brain

## 关联

- [ADR-0008-ai-human-approval.md](ADR-0008-ai-human-approval.md)
- [ADR-0021-constitutional-platform-layering.md](ADR-0021-constitutional-platform-layering.md)
- [ADR-0024-workflow-approval-truth.md](ADR-0024-workflow-approval-truth.md)
- [../project/PHX-A12_ARCHITECTURE_GATE.md](../project/PHX-A12_ARCHITECTURE_GATE.md)
