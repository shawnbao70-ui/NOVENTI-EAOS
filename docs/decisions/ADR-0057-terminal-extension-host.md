# ADR-0057 — Smart Terminal Extension Host (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G39  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

BOOK23 / Blueprint 要求 Extension 声明能力并在沙箱内运行，且不得隐藏审批或提升上下文。G35/G36 延后 Extension Host。

## 决策

1. 落点：`smart_terminal` 扩展注册与沙箱策略；Gateway `/v1/terminal/extensions*` 薄适配；UI 仅呈现。  
2. Foundation Host **不执行**任意扩展脚本/iframe runtime；仅登记清单、激活/撤销与声明动作的受治理 invoke 审计。  
3. 激活前必须具备非空 `signature_ref`。  
4. 禁止能力（fail-closed）：`hide_approval`、`elevate_context`、`bypass_audit`、`mutate_shell_controls`、`network.unrestricted`。  
5. Foundation 默认拒绝扩展网络出口（即使声明）。  
6. Extension 不得成为业务真相源；Commit/Approval 仍归既有 Terminal → Workflow 路径。

## Explicit Defer

- SharedWorker / ServiceWorker 与第三方包矩阵（Foundation iframe/Worker 见 ADR-0060/0061）  
- Marketplace 签名校验对接（Foundation 见 ADR-0062 / PHX-M18；本切片仅要求存在）  
- 跨进程热加载（SQL 持久化见 ADR-0059 / PHX-G41）  

## 关联

- [ADR-0028-smart-terminal-boundary.md](ADR-0028-smart-terminal-boundary.md)
- [ADR-0052-complete-terminal-ui.md](ADR-0052-complete-terminal-ui.md)
- [../blueprint/SMART_TERMINAL_BLUEPRINT.md](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [../constitution/BOOK23.md](../constitution/BOOK23.md)
