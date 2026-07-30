# ADR-0052 — Complete Smart Terminal UI Shell

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G36  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

PHX-G35 交付最小 Operator Shell。用户批准启动完整 Terminal UI；Blueprint 要求多表面壳与完整命令生命周期呈现，且 UI 不得宿主业务真相。

## 决策

### 1. 范围（本切片）

统一壳 `smart_terminal/ui`，表面切换：

| 表面 | 能力 |
|------|------|
| Operator | Session → Intent → Preview → Commit → Receipt |
| Approval | Request / Present Workflow 审批（高影响闸门） |
| Admin | 只读消费 `/v1/health` `/release` `/adapters` `/context` |
| AI Collaboration | 同一 Terminal 生命周期的协作呈现布局（无独立 Agent 旁路） |

### 2. 不变式

- 仅调用 Gateway；安全上下文经受信头
- `sanitizeBody` 剥离提升字段
- Approval 真相仍经 Terminal → Workflow；壳只呈现
- Extension Host / 包沙箱仍延后

### 3. 已批准、本切片不实现

- Marketplace 商业政策产品化（PHX-M17）
- JWT/OIDC 认证边界产品化（后续里程碑）

## 关联

- [ADR-0049-terminal-operator-shell.md](ADR-0049-terminal-operator-shell.md)
- [../blueprint/SMART_TERMINAL_BLUEPRINT.md](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [../project/PHX-G36_ARCHITECTURE_GATE.md](../project/PHX-G36_ARCHITECTURE_GATE.md)
