# docs/decisions/

架构决策记录（ADR）。

## ADR 索引

| ID | 文档 | 标题 | 状态 |
|----|------|------|------|
| ADR-0001～0005 | [../project/ARCHITECTURE_DECISIONS.md](../project/ARCHITECTURE_DECISIONS.md) | 仓库/平台/顺序等总册 | 已接受 |
| ADR-0006 | [ADR-0006-event-envelope.md](ADR-0006-event-envelope.md) | 事件信封 | 已接受 |
| ADR-0007 | [ADR-0007-tenant-isolation.md](ADR-0007-tenant-isolation.md) | 多租户隔离 | 已接受 |
| ADR-0008 | [ADR-0008-ai-human-approval.md](ADR-0008-ai-human-approval.md) | AI 人工审批边界 | 已接受 |
| ADR-0009 | [ADR-0009-kernel-persistence-tenancy.md](ADR-0009-kernel-persistence-tenancy.md) | 持久化与逻辑多租户 | 已接受 |
| ADR-0010 | [ADR-0010-inmemory-foundation-slice.md](ADR-0010-inmemory-foundation-slice.md) | Foundation 内存仓储切片 | 已接受 |
| ADR-0011 | [ADR-0011-event-delivery-persistence.md](ADR-0011-event-delivery-persistence.md) | Event 持久化、投递保证与死信 | 已接受 |
| ADR-0012 | [ADR-0012-kernel-database-orm.md](ADR-0012-kernel-database-orm.md) | PostgreSQL / SQLAlchemy / Alembic | 已接受 |
| ADR-0013 | [ADR-0013-runtime-foundation-boundary.md](ADR-0013-runtime-foundation-boundary.md) | Runtime Foundation 边界 | 已接受 |
| ADR-0014 | [ADR-0014-identity-session-validation.md](ADR-0014-identity-session-validation.md) | Identity 会话校验与 Runtime 强制 | 已接受 |
| ADR-0015 | [ADR-0015-identity-credential-lifecycle.md](ADR-0015-identity-credential-lifecycle.md) | Credential 生命周期与 Session 绑定 | 已接受 |
| ADR-0016 | [ADR-0016-platform-identity-governor-persistence.md](ADR-0016-platform-identity-governor-persistence.md) | Platform Identity Governor 持久化 | 已接受 |
| ADR-0017 | [ADR-0017-ai-assignment-semantics.md](ADR-0017-ai-assignment-semantics.md) | AI Employee 派驻与 INHERIT 语义 | 已接受 |
| ADR-0018 | [ADR-0018-ai-profile-persistence.md](ADR-0018-ai-profile-persistence.md) | AI Employee Profile 持久化 | 已接受 |
| ADR-0019 | [ADR-0019-identity-organization-l2.md](ADR-0019-identity-organization-l2.md) | Identity ↔ Organization L2 一致性边界 | 已接受 |
| ADR-0020 | [ADR-0020-identity-api-contract.md](ADR-0020-identity-api-contract.md) | Identity HTTP API 契约边界 | 已接受 |
| ADR-0021 | [ADR-0021-constitutional-platform-layering.md](ADR-0021-constitutional-platform-layering.md) | Constitutional Kernel 与技术分层 | 已接受（人工批准） |
| ADR-0022 | [ADR-0022-organization-lifecycle-hierarchy.md](ADR-0022-organization-lifecycle-hierarchy.md) | Organization 生命周期、层级与并发 | 已接受 |
| ADR-0023 | [ADR-0023-permission-policy-scope-delegation.md](ADR-0023-permission-policy-scope-delegation.md) | Permission Policy、Scope、Delegation 与 Explain | 已接受 |
| ADR-0024 | [ADR-0024-workflow-approval-truth.md](ADR-0024-workflow-approval-truth.md) | Workflow 审批唯一真相源与并发边界 | 已接受 |
| ADR-0025 | [ADR-0025-knowledge-shared-capability.md](ADR-0025-knowledge-shared-capability.md) | Knowledge Shared Capability 边界 | 已接受 |
| ADR-0026 | [ADR-0026-event-outbox-worker-dlq.md](ADR-0026-event-outbox-worker-dlq.md) | Event Outbox、Worker Lease 与 DLQ | 已接受 |
| ADR-0027 | [ADR-0027-ai-runtime-boundary.md](ADR-0027-ai-runtime-boundary.md) | AI Runtime 边界与审批桥 | 已接受 |
| … | （中间 ADR 见 `docs/decisions/` 文件名） | … | … |
| ADR-0162 | [ADR-0162-dual-track-governance.md](ADR-0162-dual-track-governance.md) | Dual-Track Governance（Eng + NRI） | 已接受 |
| ADR-0163 | [ADR-0163-foundation-0-2-1-release-train.md](ADR-0163-foundation-0-2-1-release-train.md) | Foundation 0.2.1 Release Train | 已接受 |
| ADR-0321 | [ADR-0321-phoenix-gate-framework.md](ADR-0321-phoenix-gate-framework.md) | Phoenix Gate Framework（唯一 Gate Framework） | 正式标准 |

## 状态

活跃。所有 Business Package Gate 统一遵循
[Phoenix Gate Framework](../project/PHOENIX_GATE_FRAMEWORK.md)；Dual-Track
操作手册：[../project/DUAL_TRACK_GOVERNANCE.md](../project/DUAL_TRACK_GOVERNANCE.md)。
