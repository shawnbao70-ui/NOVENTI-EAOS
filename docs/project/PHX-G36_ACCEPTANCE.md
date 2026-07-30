# PHX-G36 Complete Terminal UI Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted  
**归属：** Smart Terminal  
**退出门禁：** 多表面壳；完整生命周期；零业务规则宿主

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0052 + Architecture Gate |
| B | 四表面：Operator / Approval / Admin / AI Collaboration |
| C | Session refresh/close、Preview refresh、Approval request/present、Receipt 呈现 |
| D | Admin 只读 health/release/adapters/context |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- 仅调用 Gateway；`sanitizeBody` 剥离提升字段
- Approval 真相仍经 Terminal → Workflow
- 不宿主 Extension Host / OIDC 登录 / 商业 Marketplace

## 3. 自动化证据

- 本地完整回归：`405 passed`（`tests/contracts`）
- PostgreSQL：本机实例未监听（connection timeout）；本切片无 schema 变更，head 仍为 `0021_event_webhook_e21`
- Alembic head：`0021_event_webhook_e21`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0052 |
| Constitution Review | 通过；BOOK23 交互层 |
| Cross-reference Review | 通过；G30 路径覆盖 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G35 仍绿 |
| Gap Analysis | Extension / OIDC / 商业 Marketplace 显式延后（已批准待启） |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer / Next Approved

- Extension Host / 完整 a11y·i18n 矩阵
- **已批准待启：** PHX-M17 Marketplace 商业政策；PHX-G37 JWT/OIDC

## 6. 证据索引

- [PHX-G36 Architecture Gate](PHX-G36_ARCHITECTURE_GATE.md)
- [ADR-0052](../decisions/ADR-0052-complete-terminal-ui.md)
- [PHX-M17 Gate](PHX-M17_ARCHITECTURE_GATE.md)
- [PHX-G37 Gate](PHX-G37_ARCHITECTURE_GATE.md)
