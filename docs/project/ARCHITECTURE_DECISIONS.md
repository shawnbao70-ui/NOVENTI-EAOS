# Architecture Decisions

**Program:** Project Phoenix  
**Repository:** `NOVENTI-EAOS`

---

## Title

Architecture Decision Log

## Purpose

Record approved architecture decisions that bind subsequent design and implementation.

## Scope

Platform-level decisions. Detailed ADR files may also live under `docs/decisions/`.

## Current Status

Active.

## Decisions

### ADR-0001 — Sole Writable Repository

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-18 |
| Context | Phoenix work began inside Legacy CRM repository paths |
| Decision | `NOVENTI-EAOS` is the only writable development repository. Legacy is permanently read-only |
| Consequences | All new docs, code, tests, and tools are created only under `H:\Workspace\NOVENTI-EAOS`. Legacy may be read for business knowledge only |

### ADR-0002 — New Platform, Not Legacy Modernization

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-18 |
| Context | Risk of inheriting ERP architecture and technical debt |
| Decision | EAOS is a completely new platform. Legacy architecture, folder structure, and framework design are not inherited |
| Consequences | Development follows BOOK22: Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization |

### ADR-0003 — Source of Truth Priority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-18 |
| Decision | Constitution > Blueprint > Standards > Approved Decisions > Project Docs > Legacy Assets |
| Consequences | Conflicts resolve upward; Legacy never overrides Constitution or Blueprint |

### ADR-0004 — 架构与标准先于接口与实现

| 字段 | 值 |
|------|-----|
| 状态 | 已接受 |
| 日期 | 2026-07-18 |
| 决策 | PHX-002 / PHX-003 完成后，下一工作为接口定义与数据模型，禁止跳过直接实现业务代码 |
| 后果 | Kernel Foundation 之前不得引入 FastAPI 业务路由或数据库表实现 |

### ADR-0005 — Kernel 接口大纲作为 PHX-004 前置产物

| 字段 | 值 |
|------|-----|
| 状态 | 已接受 |
| 日期 | 2026-07-18 |
| 决策 | 以 `docs/architecture/KERNEL_INTERFACES.md` 作为 Kernel 实现前的接口大纲与进入门槛 |
| 后果 | 无接口大纲与宪法核心书目时，不得启动 Kernel 代码实现 |

### ADR-0006 / 0007 / 0008 / 0009

详见独立文件：

- [../decisions/ADR-0006-event-envelope.md](../decisions/ADR-0006-event-envelope.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
- [../decisions/ADR-0008-ai-human-approval.md](../decisions/ADR-0008-ai-human-approval.md)
- [../decisions/ADR-0009-kernel-persistence-tenancy.md](../decisions/ADR-0009-kernel-persistence-tenancy.md)

## 未来扩展

补充：DB/ORM 技术选型、策略语言选型、事件投递保证。

## Related Documents

- [../decisions/README.md](../decisions/README.md)
- [MASTER_PLAN.md](MASTER_PLAN.md)
