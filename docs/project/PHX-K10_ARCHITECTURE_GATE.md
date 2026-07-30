# PHX-K10 Knowledge Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Shared Platform Capability / Knowledge  
**规范源：** BOOK14、BOOK19、BOOK22、BOOK23、ADR-0021、ADR-0025

## 1. 门禁目标

交付可声明「知识主权与来源完整」的最小 Knowledge 垂直切片：Entity / Link / Provenance / Retention / 授权检索，同时保持 Shared 所有权与 Core 治理端口边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Shared Platform Capability；实现于 `eaos_platform.knowledge` |
| Core role | Permission/Tenant/Provenance 治理端口，不拥有服务 |
| Entity layers | canonical / operational / documentary / derived |
| Provenance | 每次写入 append-only，决策可读 |
| Derived | 强制标注；不可原地伪装为 canonical |
| Retention | active → archived；可选 retain_until |
| Query path | 强制 Permission.Evaluate + tenant fail-closed |
| Search | 关键词匹配；向量引擎延后 |
| Share | 租户内授权共享最小语义 |
| Events | 目录在 K10；投递归 P11 |

## 3. Action / Resource Contract

- `knowledge.entity.upsert`
- `knowledge.entity.read`
- `knowledge.entity.archive`
- `knowledge.link.create`
- `knowledge.link.read`
- `knowledge.query`
- `knowledge.search`
- `knowledge.provenance.read`
- `knowledge.share`

资源：

- `knowledge_entity:{entity_id}`
- `knowledge_link:{link_id}`
- `knowledge_graph:{tenant_id}`

## 4. 实现切片

### Slice A — Domain + 内存服务

- Entity / Link / Provenance 模型
- Upsert / Link / Get / Query / GetProvenance
- derived 强制与跨租户拒绝

### Slice B — Retention + Share + Search

- archive / retain_until
- 租户内 Share
- 关键词 Search

### Slice C — Persistence

- SQLAlchemy ORM、Transactional facade、Alembic `0014`

### Slice D — Contracts

- OpenAPI / 状态机 / 事件目录
- PostgreSQL 验收与七步自审

## 5. Exit Criteria

1. 租户知识隔离与默认拒绝检索成立。
2. 每次写入可追溯 provenance。
3. derived 不得伪装为 canonical。
4. archived / expired 读取 fail-closed。
5. OpenAPI / Data Model / Migration / Code 一致。
6. PostgreSQL 与完整回归通过。
7. 文档明确 Shared 所有权，无 Core 抢占。

## 6. Explicit Defer

- 向量检索、摄入管线、Twin 同步
- Enterprise Brain、AI Memory、Marketplace 知识包
- 可靠 outbox、物理删除合规流程
