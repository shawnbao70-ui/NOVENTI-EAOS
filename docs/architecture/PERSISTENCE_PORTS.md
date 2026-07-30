# Kernel Persistence Ports

**状态：** PHX-004 Foundation 已实现  
**日期：** 2026-07-18

## 目的

在 Domain/Service 与内存、SQLAlchemy 等基础设施适配器之间建立稳定边界。

## Repository Ports

每个 Kernel 域拥有独立 Protocol：

- `IdentityRepository`
- `OrganizationRepository`
- `PermissionRepository`
- `WorkflowRepository`
- `EventRepository`
- `AuditLog`

Service 构造函数依赖 Protocol，内存 Repository 仅作为默认 Foundation 适配器。Domain Model 不依赖 ORM。

## Unit of Work Port

共享 `UnitOfWork` 定义：

- `__enter__` / `__exit__`
- `commit`
- `rollback`

无显式 `commit` 或上下文中发生异常时必须回滚。`InMemoryUnitOfWork` 用于验证生命周期契约，不提供数据库原子性。

## 租户约束

- SQL Repository 必须在查询层强制租户范围
- Service 层保留租户校验作为纵深防御
- 平台级数据访问必须使用显式 platform scope
- 禁止使用先全局读取、后仅靠调用方过滤的生产实现

## 当前边界

已完成：

- Repository Protocol
- Service 对具体 Repository 解耦
- Unit of Work 生命周期契约
- 内存适配器结构契约测试

后续阶段：

- PHX-P11 异步 worker、租约、重试退避与 DLQ 运维接口

已建立基础设施：

- SQLAlchemy 2 统一 metadata 与确定性约束命名
- Alembic `0001_kernel_baseline` 空基线
- PostgreSQL psycopg 驱动白名单与环境变量 fail-closed
- SQLAlchemy Engine / Session Factory 与 Unit of Work
- 显式提交、未提交回滚、异常回滚、资源关闭与禁止嵌套契约
- Shared Audit / Identity 租户绑定 SQLAlchemy Repository
- 数据库时间统一恢复为 UTC，跨租户写入 fail-closed
- Identity command 的 Repository / AuditLog / Unit of Work 原子接线
- 业务失败、数据库冲突与 SQL 错误均回滚
- Organization ORM / Repository / Transactional Service
- OrganizationUnit 与 Membership 的数据库级租户复合外键
- Permission Grant / Decision ORM、租户 Repository 与事务型 Service
- 默认拒绝决策与 Audit 原子提交；Grant actions 使用 JSONB
- Workflow Definition / Instance / Task / History / Signal Receipt 持久化
- Workflow 与 Permission 求值共享事务；拒绝决策保留审计但不创建流程副作用
- Event / Subscription metadata / Delivery Attempt 持久化与 Alembic `0006`
- Python handler 与订阅元数据分离，由进程内 `EventHandlerRegistry` 管理
- Event、Permission Decision 与 Audit 共享事务；失败投递保持可重放
- 真实 PostgreSQL 17 迁移、partial index 与五域 + Event 往返契约

Event Foundation 当前仍为调用内直接 handler 投递，提供 at-least-once 语义；handler 必须幂等。跨进程异步分发与 DLQ worker 属于 PHX-P11，不在本切片伪装实现。

## 关联

- [../decisions/ADR-0009-kernel-persistence-tenancy.md](../decisions/ADR-0009-kernel-persistence-tenancy.md)
- [../decisions/ADR-0012-kernel-database-orm.md](../decisions/ADR-0012-kernel-database-orm.md)
- [KERNEL_INTERFACES.md](KERNEL_INTERFACES.md)
