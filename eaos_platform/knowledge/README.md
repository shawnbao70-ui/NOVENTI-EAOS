# Knowledge Shared Platform Capability

PHX-K10 最小垂直切片：Entity / Link / Provenance / Retention / 授权检索。

## Ownership

- 技术归属：Shared Platform Capability（ADR-0021 / ADR-0025）
- 导入包：`eaos_platform.knowledge`
- Core 仅提供 Permission / Tenant / Provenance 治理端口

## 能力

- UpsertEntity / Link / Get / Query / Search
- GetProvenance（append-only）
- Archive / Share（租户内）
- `layer=derived` 强制标注，禁止原地伪装为 canonical
- 关键词检索；向量引擎延后

## 持久化

ORM / Repository / `TransactionalKnowledgeService` 复用
`kernel.infrastructure.persistence` 的 Engine / UoW / metadata；
表位于 `kernel` schema，域语义仍属 Shared Knowledge。
