# EAOS 架构总览

**仓库：** `NOVENTI-EAOS`  
**版本：** 2.0  
**阶段：** PHX-002

---

## 标题

EAOS 架构总览

## 目的

提供 Constitutional Kernel、Core Kernel、Runtime、Shared Capabilities、Smart Terminal、Packages、Enterprise Brain、API/UI 的顶层架构地图，并与仓库目录对齐。

## 范围

系统架构文档。无实现代码。

## 当前状态

**已就绪 — PHX-002 基线**

## 分层地图

```text
Smart Terminal（受治理交互层；UI surfaces）
 ↓
API / SDK
 ↓
Packages（行业 / 业务 / AI / 集成）
 ↓
Enterprise Brain · Digital Twin（建议 / 洞察 / 模拟）
 ↓
AI Runtime · Knowledge · Shared Event/Message/Integration
 ↓
Platform Runtime（Context · Guard · Execution · Observability）
 ↓
Core Kernel（Identity · Organization · Permission · Workflow）
```

以上技术层共同实现 BOOK19 的 **Constitutional Kernel** 能力集合；Constitutional Kernel 不是单体部署层。

## 仓库对齐

| 层 | 目录 |
|----|------|
| Kernel | `kernel/` |
| Platform | `platform/` |
| Runtime | `runtime/` |
| Packages | `packages/` |
| API | `api/` |
| SDK | `sdk/` |
| UI | `ui/` |
| Smart Terminal | `smart_terminal/`（PHX-T13 Foundation；独立交互层） |
| Enterprise Brain · Digital Twin | `eaos_platform/brain` · `eaos_platform/twin`（PHX-E15） |
| Docs | `docs/` |
| Tests | `tests/` |
| Tools / Scripts | `tools/` · `scripts/` |

## 信任与隔离边界（概念）

1. **租户边界** — 默认强制隔离  
2. **权限边界** — Kernel 求值，Runtime 强制  
3. **包边界** — 声明式能力与事件契约  
4. **AI 边界** — 知识访问 + 人工审批 + 审计  
5. **遗留边界** — 只读知识，零架构依赖  
6. **终端边界** — 客户端不提供安全上下文、不持有业务真相、不绕过 Runtime/Kernel  

## 开发顺序（强制）

Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization

## 未来扩展

组件图、信任边界详图、多区域部署视图、性能与可扩展性约束。

## 关联文档

- [VISION.md](VISION.md)
- [SYSTEM_PRINCIPLES.md](SYSTEM_PRINCIPLES.md)
- [../blueprint/BLUEPRINT_INDEX.md](../blueprint/BLUEPRINT_INDEX.md)
- [../blueprint/SMART_TERMINAL_BLUEPRINT.md](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [../constitution/BOOK23.md](../constitution/BOOK23.md)
- [../decisions/ADR-0021-constitutional-platform-layering.md](../decisions/ADR-0021-constitutional-platform-layering.md)
- [../project/ARCHITECTURE_DECISIONS.md](../project/ARCHITECTURE_DECISIONS.md)
