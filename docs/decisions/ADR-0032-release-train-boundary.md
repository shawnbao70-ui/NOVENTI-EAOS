# ADR-0032 — EAOS Release Train 边界

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-R17  
**归属：** Release Engineering / SDK · API Contract Adapters

## 背景

Roadmap v3 要求 PHX-R17 交付 SDK、API adapters、兼容策略与运营手册，并以全系统合规与发布评审退出。此前里程碑已交付 Kernel / Runtime / Shared / Terminal / Package / Brain / Marketplace（技术）能力；本里程碑固定可发布基线，而不抢跑 FastAPI Router 或 Marketplace 商业政策。

## 决策

### 1. 发布基线标识

- 产品基线名称：`EAOS Phoenix Foundation`
- 包版本：`noventi-eaos==0.2.0`（与 PHX-R17 对齐）
- Alembic head 与 OpenAPI 目录必须列入 Release Manifest

### 2. SDK

- 落点：`sdk/eaos_sdk/`
- 提供：上下文构造辅助、`KernelResult` 解包、OpenAPI/兼容清单读取
- **不**直接暴露绕过 Permission / Workflow 的快捷执行路径

### 3. API Adapters

- 契约真相源保持 `docs/api/*.openapi.yaml`
- `api/adapters` 仅提供契约目录与适配器注册表（无 HTTP 路由、无 FastAPI）

### 4. 兼容策略

- OpenAPI 与错误码遵循可加不可破坏原则（additive-only 于次版本）
- 破坏性变更必须升主版本并写入兼容矩阵
- Marketplace 商业 API 保持失败关闭，不计入已发布商业能力

### 5. 运营手册

- `docs/release/OPERATIONS_RUNBOOK.md`：安装、迁移、测试、回滚、门禁
- 发布评审检查表必须可自动化抽检（契约测试）

## Explicit Defer

- FastAPI / 生产 HTTP 网关
- Marketplace 定价/账单/争议产品化
- 多区域部署与正式 CI 发布流水线 SaaS
- 对外公开包注册中心

## 关联

- [../project/PHX-R17_ARCHITECTURE_GATE.md](../project/PHX-R17_ARCHITECTURE_GATE.md)
- [../release/RELEASE_MANIFEST.yaml](../release/RELEASE_MANIFEST.yaml)
