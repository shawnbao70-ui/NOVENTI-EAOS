# PHX-K10 Knowledge Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Shared Platform Capability / Knowledge  
**退出门禁：** Provenance / Derived / Retention / 授权检索 + PostgreSQL

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | Entity / Link / Provenance 内存服务；derived 强制；跨租户拒绝 |
| B | Archive / retain_until / Share / 关键词 Search |
| C | SQLAlchemy ORM、TransactionalKnowledgeService、Alembic `0014` |
| D | OpenAPI 3.1、状态机、事件目录、PostgreSQL 与七步自审 |

## 2. 核心不变量

- Knowledge 技术归属 Shared（`eaos_platform.knowledge`）；Core 不抢占。
- Permission.Evaluate + tenant fail-closed 为检索与写入唯一授权路径。
- 每次写入 append provenance（source_ref + reason）。
- derived 不得原地伪装为 canonical。
- Entity 更新使用 `expected_version`。
- archived / retain_until 到期读取 fail-closed。
- secrets 不得进入 attributes。

## 3. 自动化证据

- 本地完整回归：`229 passed`
- 专用 PostgreSQL 17：`13 passed`
- Alembic head：`0014_knowledge_k10`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0025 / Gate 边界成立 |
| Constitution Review | 通过；BOOK14/19/22/23 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；OpenAPI / Data Model / Migration / Code 一致 |
| Gap Analysis | 阻断项关闭；向量/Twin/Brain/Memory/outbox 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 向量检索与摄入管线
- Digital Twin 同步
- Enterprise Brain（PHX-E15）
- AI Memory（PHX-A12）
- Marketplace 知识包（PHX-M16）
- 可靠 outbox（PHX-P11）
- 物理删除合规流程

## 6. 证据索引

- [PHX-K10 Architecture Gate](PHX-K10_ARCHITECTURE_GATE.md)
- [ADR-0025](../decisions/ADR-0025-knowledge-shared-capability.md)
- [Knowledge Interface](../architecture/KNOWLEDGE_INTERFACE.md)
- [Knowledge State Machines](../architecture/KNOWLEDGE_STATE_MACHINES.md)
- [Knowledge Events](../architecture/KNOWLEDGE_EVENTS.md)
- [Knowledge OpenAPI](../api/knowledge.openapi.yaml)
