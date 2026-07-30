# ADR-0049 — Smart Terminal Operator Shell Foundation

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G35  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

PHX-T13 / G30 已交付 Terminal 能力与 HTTP。Blueprint 仍延后完整 UI Shell。需要最小 Operator Shell，证明客户端只消费 Gateway，不宿主业务真相。

## 决策

### 1. 落点

- 静态壳：`smart_terminal/ui/`（HTML / CSS / JS）
- 网关挂载：`GET /terminal/`（`StaticFiles`，`html=True`）
- API 仍仅 `/v1/terminal/*`；壳不引入第二套业务 API

### 2. 信任边界

- 安全上下文仅经受信头（开发态显式填写；生产由认证边界注入）
- 请求体禁止 `tenant_id` / `subject_id` / `platform_scope` / `session_id`
- 壳不评估 Permission / Workflow；仅呈现与转发

### 3. 本切片范围

Operator Workbench 命令生命周期：Open Session → Intent → Preview →（可选 Approval）→ Commit → Receipt

### 4. Explicit Defer

- 完整品牌/UX 产品化与设计令牌治理（需 UX 批准）
- Extension Host / Marketplace 沙箱
- Accessibility / i18n 产品矩阵
- JWT/OIDC 登录页；商业 Marketplace

## 关联

- [ADR-0028-smart-terminal-boundary.md](ADR-0028-smart-terminal-boundary.md)
- [ADR-0045-gateway-terminal-http-surface.md](ADR-0045-gateway-terminal-http-surface.md)
- [../blueprint/SMART_TERMINAL_BLUEPRINT.md](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [../project/PHX-G35_ARCHITECTURE_GATE.md](../project/PHX-G35_ARCHITECTURE_GATE.md)
