# PHX-R17 EAOS Release Train Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted；实现已验收（见 PHX-R17_ACCEPTANCE）  
**归属：** Release Engineering  
**规范源：** BOOK19、BOOK22、ADR-0032、Roadmap v3  
**退出门禁：** 全系统合规与发布评审

## 1. 门禁目标

固化 Phoenix Foundation 可发布基线：SDK 最小面、API 契约适配目录、兼容策略、运营手册与可自动化发布检查。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Baseline | EAOS Phoenix Foundation / `0.2.0` |
| SDK | `sdk/eaos_sdk` 辅助面；无特权旁路 |
| API adapters | 契约目录注册；无 FastAPI |
| Compat | 次版本 additive-only；破坏性升主版本 |
| Ops | Runbook + Checklist + Manifest |
| Commercial | Marketplace 商业能力不纳入本基线 |

## 3. 交付切片

### Slice A — Manifest / Compat / Ops docs

### Slice B — SDK + API adapter registry

### Slice C — Release contract tests + 全量回归

### Slice D — 七步自审与验收

## 4. Exit Criteria

1. Release Manifest 列出全部 OpenAPI、Alembic head、里程碑状态。  
2. SDK 可导入并提供上下文/结果辅助。  
3. API adapter 目录与 `docs/api` 契约一致。  
4. 兼容策略文档与机器检查通过。  
5. 完整契约 + PostgreSQL 回归通过。  
6. 七步自审通过；不宣称 FastAPI/商业 Marketplace 已发布。

## 5. Explicit Defer

FastAPI Router、商业 Marketplace、多区域生产运维 SaaS、公开包注册中心
