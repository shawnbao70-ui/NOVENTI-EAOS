# ADR-0012 — Kernel 数据库、ORM 与迁移技术栈

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

PHX-004 的内存仓储已完成核心契约验证。下一阶段需要生产级持久化，同时保持 Kernel 接口、租户隔离与 fail-closed 语义。

## 决策

采用：

- **PostgreSQL**：Kernel 权威关系数据存储
- **SQLAlchemy 2.x**：显式映射、事务与 Repository 适配器
- **Alembic**：版本化、可审计的数据库迁移

### 约束

1. Domain Model 不依赖 SQLAlchemy
2. Service 仅依赖 Repository Protocol，不直接访问 Session
3. SQLAlchemy Model 位于基础设施适配器层
4. 所有租户数据表显式包含 `tenant_id`
5. Repository 查询必须将租户条件作为强制条件
6. 默认 UUID 主键、UTC 时间、审计字段与软删除规则遵循数据库标准
7. 禁止映射或复用 Legacy ERP 表
8. 迁移脚本必须可审查；生产环境禁止运行时自动建表
9. Outbox、事件存储与 DLQ 遵循 ADR-0011

## 事务边界

- 一个 Kernel command 对应一个显式 Unit of Work
- 业务状态与 outbox 写入在同一数据库事务中提交
- 审计记录不得因应用层异常被静默丢弃
- 跨 Kernel 分布式事务使用事件与补偿，不引入两阶段提交

## 实施顺序

1. 定义 Repository Protocol 与 Unit of Work Protocol
2. 保留内存适配器作为快速契约测试实现
3. 建立 SQLAlchemy metadata 与 Alembic baseline
4. 首先迁移 Shared Audit / Identity，再扩展其他 Kernel
5. 对内存与 PostgreSQL 适配器运行相同 Repository 契约测试

## 后果

- 获得成熟的事务、约束、索引与迁移能力
- 需要维护 Domain Model 与 Persistence Model 映射
- 集成测试需要可重复启动的 PostgreSQL 环境
- SQLAlchemy/Alembic 依赖在首个持久化适配器实施时引入

## 关联

- [ADR-0009-kernel-persistence-tenancy.md](ADR-0009-kernel-persistence-tenancy.md)
- [ADR-0010-inmemory-foundation-slice.md](ADR-0010-inmemory-foundation-slice.md)
- [ADR-0011-event-delivery-persistence.md](ADR-0011-event-delivery-persistence.md)
- [../standards/DATABASE_STANDARD.md](../standards/DATABASE_STANDARD.md)
