# PHX-T13 Smart Terminal Foundation Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Smart Terminal（独立受治理交互层）  
**退出门禁：** 不持有业务真相

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | Session / Intent / Preview 内存服务 |
| B | RequestApproval / PresentApproval / Commit |
| C | SQLAlchemy + TransactionalSmartTerminalService + Alembic `0017` |
| D | OpenAPI / 状态机 / PostgreSQL / 七步自审 |

## 2. 核心不变量

- 客户端无法提升 Subject / Tenant → `TERMINAL_CONTEXT_ELEVATION_DENIED`
- Approval 以 Workflow 为准；本地仅 `approval_ref`
- 高影响 Commit 双闸门；陈旧预览 / 不可信设备失败关闭
- Intent / Preview / Receipt ≠ 业务实体真相
- 秘密字段拒绝写入工作区文本

## 3. 自动化证据

- 本地完整回归：`263 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`16 passed`（`tests/integration`）
- Alembic head：`0017_smart_terminal_t13`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0021/0028；落点 `smart_terminal/` |
| Constitution Review | 通过；BOOK12/19/22/23 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 阻断项关闭；完整 UI / Extension / Brain 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 完整前端 Shell / 浏览器客户端
- Extension Host / Marketplace 沙箱
- Accessibility / i18n 产品化矩阵
- Enterprise Brain / Digital Twin 呈现
- FastAPI Router、Business Package surfaces

## 6. 证据索引

- [PHX-T13 Architecture Gate](PHX-T13_ARCHITECTURE_GATE.md)
- [ADR-0028](../decisions/ADR-0028-smart-terminal-boundary.md)
- [Smart Terminal Interface](../architecture/SMART_TERMINAL_INTERFACE.md)
- [Smart Terminal State Machines](../architecture/SMART_TERMINAL_STATE_MACHINES.md)
- [Terminal OpenAPI](../api/terminal.openapi.yaml)
