# ADR-0029 — Business Package Platform 边界

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-B14  
**归属：** Shared Platform Capability / Package Platform

## 背景

BOOK11/BOOK23 要求行业与业务能力以 Package 扩展，且不得污染或分叉 Kernel。PHX-T13 已要求声明式 Package surfaces；PHX-B14 需固定 manifest、surface/action contract 与租户安装边界。

## 决策

### 1. Ownership 与落点

- Package Platform（注册表、安装、契约解析）属 Shared Platform Capability：`eaos_platform.package`。
- 包制品/行业包声明内容位于 `packages/<package_key>/`（声明式；本里程碑提供样例）。
- 不放入 Core Kernel 域包；不得在包内复制 Permission / Workflow / Identity 真相源。

### 2. Manifest 契约

- Manifest 绑定：`package_key` + `version` + `package_type`（industry / business / ai / integration）。
- 必须声明：surfaces、actions、required_permissions、declared_events。
- Actions 的 `resource_type` 必须以 `pkg.` 为前缀；禁止占用 Kernel/Terminal/AI 保留资源类型。
- `package_key` 不得以 `kernel.` / `eaos.kernel.` 开头。

### 3. 生命周期

```text
draft → published → (tenant) installed | disabled
```

- 仅 `published` 可安装。
- Surface / Action 解析仅对已安装包可见。
- `ResolveAction` 校验声明 + 安装状态 + Permission；不执行业务副作用。

### 4. 「不分叉 Kernel」

- 包消费平台能力，不平行实现授权、审批、身份或租户真相。
- 未声明 surface/action 不可解析。
- 审计记录注册、发布、安装、禁用与解析。

## Explicit Defer

- Marketplace 签名分发、计费、争议（PHX-M16）
- 完整行业包业务实现与遗留 ERP 迁移
- Hot-upgrade / 多版本并存产品化
- FastAPI Router、Extension Host 沙箱执行引擎

## 关联

- [ADR-0021-constitutional-platform-layering.md](ADR-0021-constitutional-platform-layering.md)
- [ADR-0028-smart-terminal-boundary.md](ADR-0028-smart-terminal-boundary.md)
- [../blueprint/PACKAGE_BLUEPRINT.md](../blueprint/PACKAGE_BLUEPRINT.md)
- [../project/PHX-B14_ARCHITECTURE_GATE.md](../project/PHX-B14_ARCHITECTURE_GATE.md)
