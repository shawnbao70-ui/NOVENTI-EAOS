# runtime/ai/

AI Runtime（PHX-A12）：Agent Run、工具治理、Memory、Workflow approval bridge。

## 能力

- `CreateAgentRun` / `GetAgentRun`
- `RegisterTool` / `InvokeTool`（Permission + high_impact 审批）
- `WriteMemory` / `ReadMemory`
- `RequestApproval` / `CommitAction`
- `AccessKnowledge`（委托 Knowledge Capability）

## 边界

- 实现落点 Platform Runtime；不拥有 Identity Grant 或企业知识真相源
- 不包含模型提供商、工具沙箱、Terminal UX
