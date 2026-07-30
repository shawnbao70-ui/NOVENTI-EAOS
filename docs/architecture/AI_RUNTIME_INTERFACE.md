# AI Runtime 接口规格

**文档 ID：** IF-AI-001  
**版本：** 1.0  
**阶段：** PHX-A12  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

## 目的

细化 Agent Run、工具治理、AI Memory、Approval Bridge 与 Knowledge 访问接口，确保「AI 不越权且可解释」。

## 不变式

1. AI 操作经 `runtime/ai` AI Runtime；非 AI 主体创建 run 失败关闭  
2. 工具须注册；Invoke 经 Permission `invoke_tool`  
3. high_impact 工具与 CommitAction 须 Workflow `verify_approved_action`  
4. Memory ≠ Knowledge；禁止秘密字段  
5. Knowledge 只读委托 Shared Knowledge Capability  
6. 关键可审计（run_id + correlation_id）  
7. API 不接受客户端声明 execution context 字段  

## 接口

| 接口 | HTTP | 权限要点 |
|------|------|----------|
| CreateAgentRun | `POST /ai/runs` | `ai_run:create`；主体须 AI |
| GetAgentRun | `GET /ai/runs/{runId}` | `ai_run:read` |
| RegisterTool | `POST /ai/tools` | `tool:register` |
| InvokeTool | `POST /ai/runs/{runId}/tools/invocations` | `tool:invoke_tool`；high_impact 需批准 |
| Write/ReadMemory | memory 路径 | `ai_memory:write/read` |
| RequestApproval | `POST .../approvals` | 启动 Workflow 审批实例 |
| CommitAction | `POST .../commits` | 双闸门后提交 |

## 错误

`AI_RUNTIME_REQUIRED`、`AI_TOOL_DENIED`、`AI_APPROVAL_REQUIRED`、`AI_COMMIT_FORBIDDEN`、`AI_MEMORY_DENIED`、`AI_KNOWLEDGE_DENIED`

## 关联

- [AI_RUNTIME_STATE_MACHINES.md](AI_RUNTIME_STATE_MACHINES.md)
- [../api/ai.openapi.yaml](../api/ai.openapi.yaml)
- [../decisions/ADR-0027-ai-runtime-boundary.md](../decisions/ADR-0027-ai-runtime-boundary.md)
- [../project/PHX-A12_ARCHITECTURE_GATE.md](../project/PHX-A12_ARCHITECTURE_GATE.md)
