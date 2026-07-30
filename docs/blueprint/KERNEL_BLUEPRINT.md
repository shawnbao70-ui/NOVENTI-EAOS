# 内核蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-KERNEL  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS 内核蓝图

## 目的

定义 EAOS Core Kernel：身份、组织、权限、工作流基础，以及其对 Constitutional Kernel 基本法的技术承接。

## 范围

**范围内：** Core Kernel 域边界、平台不变量、与 Runtime / Event / Knowledge / AI / Smart Terminal 的关系、与业务包及遗留 ERP 的隔离。  
**范围外：** 包级业务规则、UI 呈现细节、遗留目录/框架继承。

## 当前状态

**基线已建立 — PHX-002**  
Identity 与 Organization 完整门禁已完成；Permission / Workflow / Knowledge 按 PHX-K08–K10 深化。实施状态以项目验收文档为准。

## 未来扩展

Identity / Organization / Permission / Workflow 的正式契约、Knowledge 治理端口；反模式清单（禁止从遗留 ERP 继承的结构）。

---

## 内核原则

1. **Kernel First** — 平台能力优先于重复业务逻辑  
2. **Constitution First** — 内核意图服从宪法（尤其 Kernel 相关书目）  
3. **多租户隔离** 是内核关切  
4. **权限与可审计性** 是内核关切  
5. **不继承** 遗留架构；可抽取业务知识  
6. **双层解释** — BOOK19 的 Constitutional Kernel 是能力集合；本蓝图描述可部署 Core Kernel  

## Core Kernel 域与治理端口

| 域 | 里程碑 | 主要关切 |
|----|--------|----------|
| Identity | PHX-006 | 主体、凭证、会话边界 |
| Organization | PHX-K07 | 租户、组织单元、成员关系 |
| Permission | PHX-K08 | 授权模型与策略求值 |
| Workflow | PHX-K09 | 流程编排原语 |
| Knowledge Governance Port（非 Core 域） | PHX-K10 | Shared Knowledge 的授权、租户与 provenance 契约 |

## 不变量（摘要）

- 一切副作用操作必须可关联到租户与身份上下文  
- 业务包不得绕过权限求值  
- 内核公共契约版本化；破坏性变更需 ADR  
- 遗留系统不得成为内核依赖  

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md)
- [EVENT_BLUEPRINT.md](EVENT_BLUEPRINT.md)
- [KNOWLEDGE_BLUEPRINT.md](KNOWLEDGE_BLUEPRINT.md)
- [AI_BLUEPRINT.md](AI_BLUEPRINT.md)
- [../architecture/EAOS_ARCHITECTURE.md](../architecture/EAOS_ARCHITECTURE.md)
- [../architecture/SYSTEM_PRINCIPLES.md](../architecture/SYSTEM_PRINCIPLES.md)
- [SMART_TERMINAL_BLUEPRINT.md](SMART_TERMINAL_BLUEPRINT.md)
- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [../decisions/ADR-0021-constitutional-platform-layering.md](../decisions/ADR-0021-constitutional-platform-layering.md)
