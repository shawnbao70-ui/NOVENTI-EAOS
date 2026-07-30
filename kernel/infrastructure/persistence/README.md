# Persistence Foundation

SQLAlchemy 2 / Alembic / PostgreSQL 基础设施层。

## 当前能力

- 统一 SQLAlchemy `Base` 与约束命名
- Alembic 基线 `0001` 与 Shared Audit / Identity schema `0002`
- 仅接受 `postgresql+psycopg` 数据库 URL
- 缺少 `EAOS_DATABASE_URL` 时 fail-closed
- Engine / Session Factory 与 SQLAlchemy Unit of Work
- 租户绑定的 Shared Audit / Identity Repository 适配器
- `TransactionalIdentityService`：每个调用一个 UoW，Domain 与 Audit 原子提交
- Organization ORM / Repository / TransactionalOrganizationService
- Permission ORM / Repository / TransactionalPermissionService
- Workflow ORM / Repository / TransactionalWorkflowService
- Knowledge ORM / Repository / TransactionalKnowledgeService（Shared Capability）
- Event ORM / Repository / TransactionalEventBus（含 Outbox / DLQ）
- AI Runtime ORM / Repository / TransactionalAIRuntimeService
- 持久化订阅元数据与进程内 `EventHandlerRegistry` 分离

## 安装

```bash
pip install -e ".[dev,persistence]"
```

## 迁移

通过安全的环境变量注入连接信息，然后执行：

```bash
python -m alembic upgrade head
```

禁止将真实凭据写入 `alembic.ini` 或仓库文件。

## 边界

当前 Shared Audit、Identity、Organization、Permission、Workflow、Knowledge、Event 已完成 ORM、Repository、Unit of Work 与事务型接线。Knowledge 域语义属 Shared Platform Capability，表复用 `kernel` schema。Event 已具备 Outbox / Lease / Retry / DLQ（PHX-P11）；外部 Broker 与多区域韧性延后。真实 PostgreSQL 17 集成契约已通过。

真实 PostgreSQL 契约位于 `tests/integration`，仅接受名称以 `eaos_test` 开头的专用数据库。未配置时明确跳过，不以 SQLite 结果替代 PostgreSQL 验证。
