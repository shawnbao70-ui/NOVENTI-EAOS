# Legacy Knowledge Extract — Platform Observations

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** 业务平台表象抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/platform-obs/**`  
**Verified:** 2026-07-23

## Purpose

记录 Legacy 的平台运营入口、模块挂载、登录/权限/租户中心和 AI Employee Center 的可见业务表象。此包不是 EAOS Kernel 设计输入，也不授权复用旧平台、身份或执行架构。

## Hard boundaries

- Legacy Platform/System 观察 ≠ EAOS Kernel。
- EAOS Identity/Permission Kernel 必须另建，不继承旧 session、RBAC、tenant bridge。
- AI Employee Center 是 registry/framework 表象，≠ Brain execute。
- 本包未打开或分析 Brain/Twin 实现。
- 缺失证据写 `UNKNOWN` 并列已查路径。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 模块入口和证据强度 |
| [platform.md](platform.md) | 租户运营入口与模块挂载观察 |
| [identity_obs.md](identity_obs.md) | 登录、权限、租户的业务身份表象 |
| [ai_employee.md](ai_employee.md) | AI Employee Center 能力边界与缺口 |
