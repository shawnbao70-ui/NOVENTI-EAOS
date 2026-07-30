# PHX-B14 Business Package Platform Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Shared Platform Capability / Package Platform  
**退出门禁：** 不分叉 Kernel

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | Manifest 注册 / 发布 / Kernel fork 防护 |
| B | 租户安装 / Surface 列表 / Action 解析 |
| C | SQLAlchemy + TransactionalPackageService + Alembic `0018` |
| D | OpenAPI / 状态机 / `packages/sample_ops` / PostgreSQL / 七步自审 |

## 2. 核心不变量

- `kernel.*` 包键与非 `pkg.*` / 保留资源类型 → `PACKAGE_KERNEL_FORK_DENIED`
- 未发布不可安装；未安装 / 已禁用不可解析
- ResolveAction 经 Permission，无业务副作用
- 样例行业包 `noventi.sample.ops` 声明式落在 `packages/sample_ops`

## 3. 自动化证据

- 本地完整回归：`274 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`17 passed`（`tests/integration`）
- Alembic head：`0018_package_platform_b14`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0021/0029；落点 `eaos_platform.package` |
| Constitution Review | 通过；BOOK08/11/19/22/23 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 阻断项关闭；Marketplace / 完整行业 ERP 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Marketplace 签名分发、计费、争议（PHX-M16）
- 完整行业业务实体与遗留 ERP 迁移
- Hot-upgrade / 多版本并存产品化
- FastAPI Router、Extension Host 沙箱

## 6. 证据索引

- [PHX-B14 Architecture Gate](PHX-B14_ARCHITECTURE_GATE.md)
- [ADR-0029](../decisions/ADR-0029-business-package-platform.md)
- [Package Interface](../architecture/PACKAGE_INTERFACE.md)
- [Package State Machines](../architecture/PACKAGE_STATE_MACHINES.md)
- [Package OpenAPI](../api/package.openapi.yaml)
