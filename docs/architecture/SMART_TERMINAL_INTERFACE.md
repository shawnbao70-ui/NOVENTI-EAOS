# Smart Terminal 接口规格

**文档 ID：** IF-TERM-001  
**版本：** 1.0  
**阶段：** PHX-T13  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

## 目的

细化 Session、Intent、Plan Preview、Approval Presenter 与 Commit Controller 接口，确保「不持有业务真相」。

## 不变式

1. Session / 安全上下文仅派生自受信 `ExecutionContext`；客户端提升失败关闭  
2. Intent / Preview 为工作区状态，不是业务实体真相  
3. Approval 状态每次从 Workflow 读取；本地仅存 `approval_ref`  
4. 高影响 Commit 经 Permission + `Workflow.verify_approved_action`  
5. 设备 untrusted 时拒绝高影响 Commit  
6. 禁止秘密字段进入 Intent / Impact 文本  
7. Commit 回执 ≠ 业务写入成功声明（无业务包实体突变）

## 接口

| 接口 | HTTP | 权限要点 |
|------|------|----------|
| OpenSession | `POST /terminal/sessions` | `terminal_session:open` |
| Get/CloseSession | session 路径 | `read` / `close` |
| ComposeIntent | `POST /terminal/intents` | `terminal_intent:compose` |
| BuildPreview | `POST /terminal/previews` | `terminal_preview:build` |
| RequestApproval | `POST .../approvals` | `terminal_approval:request` + Workflow start |
| PresentApproval | `GET .../approvals` | `terminal_approval:present`；读 Workflow |
| Commit | `POST .../commits` | `terminal_commit:execute` |

## 错误

`TERMINAL_CONTEXT_ELEVATION_DENIED`、`TERMINAL_DEVICE_UNTRUSTED`、`TERMINAL_STALE_PREVIEW`、`TERMINAL_APPROVAL_INVALID`、`TERMINAL_COMMIT_FORBIDDEN`、`TERMINAL_SECRET_DENIED`

## 关联

- [SMART_TERMINAL_STATE_MACHINES.md](SMART_TERMINAL_STATE_MACHINES.md)
- [../api/terminal.openapi.yaml](../api/terminal.openapi.yaml)
- [../decisions/ADR-0028-smart-terminal-boundary.md](../decisions/ADR-0028-smart-terminal-boundary.md)
- [../project/PHX-T13_ARCHITECTURE_GATE.md](../project/PHX-T13_ARCHITECTURE_GATE.md)
