# kernel/

EAOS Kernel 根目录。

## 目的

承载宪法级公共能力：Identity、Organization、Permission、Workflow 等。  
**提供公共能力，不提供业务功能。**

## 状态

**PHX-004 — Kernel Foundation 完成**

| 模块 | 状态 |
|------|------|
| `shared/` | **已实现** |
| `identity/` | **Foundation 已实现**（内存 + SQLAlchemy） |
| `organization/` | **Foundation 已实现**（内存 + SQLAlchemy） |
| `permission/` | **Foundation 已实现**（默认拒绝 + SQLAlchemy） |
| `workflow/` | **Foundation 已实现**（审批/幂等 + SQLAlchemy） |
| `event_bus/` | **Foundation 已实现**（不可变/重放 + SQLAlchemy） |
| `infrastructure/persistence/` | **已实现**（ORM / Repository / UoW / Transactional Facade） |

无 FastAPI、无业务路由、无遗留依赖。

## 模块布局

| 目录 | 域 | 对应里程碑 |
|------|----|------------|
| `identity/` | 身份 | PHX-006 |
| `organization/` | 组织 | PHX-K07 |
| `permission/` | 权限 | PHX-K08 |
| `workflow/` | 流程 | PHX-K09 |
| `event_bus/` | 事件总线兼容命名；技术归属 Shared Platform Capability | PHX-P11 |
| `shared/` | 跨域上下文/错误/类型占位 | PHX-004 |
| `infrastructure/` | SQLAlchemy / Alembic 持久化适配 | PHX-004 |

## 权威文档

- [../docs/constitution/BOOK19.md](../docs/constitution/BOOK19.md)
- [../docs/architecture/KERNEL_INTERFACES.md](../docs/architecture/KERNEL_INTERFACES.md)
- [../docs/architecture/KERNEL_DATA_MODEL.md](../docs/architecture/KERNEL_DATA_MODEL.md)
- [../docs/architecture/KERNEL_CONTRACT_TEST_PLAN.md](../docs/architecture/KERNEL_CONTRACT_TEST_PLAN.md)

## 规则

1. 业务包不得写入本目录  
2. 不得依赖遗留 ERP 仓库代码  
3. 实现前必须满足接口 + 数据模型 + 契约测试计划  
4. 开发顺序：Interfaces → Data Models → Implementation → Tests  
