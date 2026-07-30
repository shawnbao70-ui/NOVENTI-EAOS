# ADR-0025 — Knowledge Shared Platform Capability 边界

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-K10  
**归属：** Shared Platform Capability / Knowledge

## 背景

宪政称“Knowledge Kernel”，ADR-0021 与 BOOK19 已裁决其技术归属为 Shared Platform Capability。PHX-K10 需要固定代码落点、治理端口、Provenance/Derived/Retention 与授权检索边界，避免误实现为 Core Kernel 域。

## 决策

### 1. 所有权

- 技术唯一归属：Shared Platform Capability。
- 实现包：`eaos_platform.knowledge`（目录 `eaos_platform/knowledge/`；避免与 Python 标准库 `platform` 冲突）。
- 仓库 `platform/` 目录保留为 Shared 层说明占位，不作为 Python 导入根。
- Core Kernel 仅通过 Permission / Tenant / Provenance 治理契约约束访问；不得将 Knowledge 服务实现宣称为 Core 所有权。
- 持久化适配器可复用 `kernel/infrastructure/persistence` 的 Engine/UoW/metadata，但表与域语义仍属 Shared Knowledge。

### 2. 最小实体模型

- **Entity（Node）：** 租户作用域规范实体；`layer` ∈ {canonical, operational, documentary, derived}。
- **Link（Edge）：** 同租户有向关系；禁止自环。
- **Provenance：** 每次写入 append-only；含 actor、source_ref、reason、derived 标记、时间。

### 3. Derived

- `layer=derived` 必须在创建时标注；不得伪装为 canonical 原始事实。
- Derived 可引用上游 entity/link；晋升为 canonical 需显式新写入 + provenance，不原地改层。

### 4. Retention

- Entity/Link 使用 terminal status：`active → archived`（软归档）。
- 不提供物理删除；合法强制删除例外延后合规里程碑。
- `retain_until` 可选；到期后读取 fail-closed（视为不可用）。

### 5. 授权检索

- `Query` / `Get` / `GetProvenance` / `Link` / `Upsert` 均须 `Permission.Evaluate`。
- 缺租户或缺权限默认拒绝。
- 跨租户默认拒绝；Share 仅租户内授权可见性扩展（本里程碑最小实现）。

### 6. Search

- K10 交付关键词 `Search`（名称/标签匹配）。
- 向量/语义检索引擎 Explicit Defer。

### 7. 事件

- K10 定义 Knowledge 事件目录。
- 可靠 outbox/delivery 归 PHX-P11。

### 8. 与邻域边界

| 邻域 | 边界 |
|------|------|
| Permission | 唯一授权真相；Knowledge 不自建 ACL |
| Workflow | 高影响知识变更可另挂审批；本切片不强制 |
| AI Memory | ≠ Enterprise Knowledge；提升必须经 Knowledge 写入 |
| Enterprise Brain | 只读授权知识；不拥有知识 |

## Explicit Defer

- 向量检索引擎与摄入管线
- Digital Twin 同步
- Enterprise Brain（PHX-E15）
- AI Memory 实现（PHX-A12）
- Marketplace 知识包（PHX-M16）
- 可靠 event outbox（PHX-P11）
- 物理删除合规流程

## 关联

- [ADR-0021-constitutional-platform-layering.md](ADR-0021-constitutional-platform-layering.md)
- [../constitution/BOOK14.md](../constitution/BOOK14.md)
- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [../blueprint/KNOWLEDGE_BLUEPRINT.md](../blueprint/KNOWLEDGE_BLUEPRINT.md)
- [../project/PHX-K10_ARCHITECTURE_GATE.md](../project/PHX-K10_ARCHITECTURE_GATE.md)
