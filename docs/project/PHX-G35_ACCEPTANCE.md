# PHX-G35 Smart Terminal Operator Shell Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted（技术壳）  
**归属：** Smart Terminal  
**退出门禁：** 壳为 API 消费者；零业务规则宿主

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0049 + Architecture Gate |
| B | `smart_terminal/ui` Operator Shell（HTML/CSS/JS） |
| C | Gateway `GET /terminal/` 静态挂载 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 仅调用 `/v1/terminal/*`
- 安全上下文经受信头；`sanitizeBody` 剥离提升字段
- Permission / Workflow 真相不进壳
- 不宣称完整产品 UI / Extension Host / OIDC

## 3. 自动化证据

- 本地完整回归：`397 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0049 |
| Constitution Review | 通过；BOOK23 交互层、无业务真相 |
| Cross-reference Review | 通过；挂载与 G30 路径对齐 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G34 仍绿 |
| Gap Analysis | 品牌 UX / Extension / OIDC / 商业显式延后 |
| Second-pass Review | Fully Accepted（技术壳） |

## 5. Explicit Defer

- 完整品牌/UX 产品化与设计令牌治理
- Extension Host / Marketplace 沙箱
- Accessibility / i18n 产品矩阵
- JWT/OIDC；Marketplace 商业政策

## 6. 证据索引

- [PHX-G35 Architecture Gate](PHX-G35_ARCHITECTURE_GATE.md)
- [ADR-0049](../decisions/ADR-0049-terminal-operator-shell.md)
