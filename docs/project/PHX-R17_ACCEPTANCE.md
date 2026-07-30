# PHX-R17 EAOS Release Train Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**基线：** EAOS Phoenix Foundation `0.2.0`  
**退出门禁：** 全系统合规与发布评审

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | Release Manifest / Compatibility / Ops Runbook / Checklist |
| B | `eaos_sdk` + `api.adapters` 契约目录 |
| C | 发布契约测试 + 全量回归 |
| D | 七步自审与验收 |

## 2. 核心不变量

- Manifest 列齐 11 份 OpenAPI + Alembic head `0020_marketplace_m16`
- SDK 无特权旁路；次版本 additive-only
- API adapters 无 FastAPI 路由
- Marketplace 商业 API 仍失败关闭
- 包版本 `0.2.0` 与 Manifest / SDK 一致

## 3. 自动化证据

- 本地完整回归：`300 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`（`tests/integration`）
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0032 |
| Constitution Review | 通过；不抢跑商业 Marketplace / FastAPI |
| Cross-reference Review | 通过 |
| Documentation Review | 通过；Runbook/Compat/Manifest |
| Consistency Review | 通过；版本与 head 对齐 |
| Gap Analysis | 发布阻断项关闭；生产网关/商业政策显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- FastAPI / 生产 HTTP 网关
- Marketplace 定价/账单/争议产品化
- 多区域生产运维 SaaS
- 对外公开包注册中心

## 6. 证据索引

- [PHX-R17 Architecture Gate](PHX-R17_ARCHITECTURE_GATE.md)
- [ADR-0032](../decisions/ADR-0032-release-train-boundary.md)
- [Release Manifest](../release/RELEASE_MANIFEST.yaml)
- [Compatibility](../release/COMPATIBILITY.md)
- [Operations Runbook](../release/OPERATIONS_RUNBOOK.md)
