# Platform Observations — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Module | File | Evidence strength |
|---|---|---|
| Platform / System 运营面 | [platform.md](platform.md) | Strong：manifest 挂载、页面/语言/工作区入口；Medium：模块边界规范；Missing：统一租户运营控制面 |
| Login / Permission / Tenant 表象 | [identity_obs.md](identity_obs.md) | Strong：legacy auth/session/RBAC；Medium：V15.1 registry；Weak：tenant bridge 一致性 |
| AI Employee Center | [ai_employee.md](ai_employee.md) | Strong：registry/schema/framework；Medium：独立 workforce API；Missing：中心自身执行闭环 |

## Interpretation rule

这些材料只说明 Legacy 用户看到什么、数据如何表面流转、模块如何被挂载。它们不定义 EAOS Kernel、Identity、Permission、Tenant 或 AI execution 架构。

## Explicit exclusions

- 未打开或分析 Brain/Twin。
- 不把 manifest 中的模块名称当作能力已落地。
- 不把默认 seed、health 或 metadata-only 条目当作运营数据。
