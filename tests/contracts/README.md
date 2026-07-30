# tests/contracts/

Kernel 契约测试。

## 当前覆盖

| 文件 | 覆盖 |
|------|------|
| `test_execution_context.py` | 上下文校验、N-01 缺租户失败关闭 |
| `test_identity_service.py` | I-01～I-06、跨租户隔离、凭证不回传明文 |
| `test_organization_service.py` | O-01～O-05、父子组织与成员跨租户隔离 |
| `test_permission_service.py` | P-01～P-06、默认拒绝、授权/撤销、决策审计、Slice A 安全闭合 |
| `test_permission_policy_delegation.py` | Policy deny-overrides、Delegation 父链与缩小约束 |
| `test_permission_openapi.py` | Permission OpenAPI 3.1 与状态机契约 |
| `test_org_permission_integration.py` | 组织角色不隐式授予权限 |
| `test_transactional_org_permission_integration.py` | 持久化组织角色不隐式授予权限 |
| `test_workflow_service.py` | W-01～W-05、状态机、Permission 集成、AI 审批闸门 |
| `test_workflow_k09.py` | 乐观锁、escalate/cancel、SLA、补偿、plan_version 绑定 |
| `test_workflow_openapi.py` | Workflow OpenAPI 3.1 与状态机契约 |
| `test_event_bus.py` | E-01～E-04、不可变信封、权限、租户隔离、幂等重放 |
| `test_transactional_event_bus.py` | Event ORM、事务发布、失败尝试与持久化重放 |
| `test_runtime_foundation.py` | Runtime 入站、传播、快照、执行守卫与可观测绑定 |

## 运行

```bash
pip install -e ".[dev,persistence]"
python -m pytest -p no:cacheprovider
```

当前完整结果：**215 passed（另有 12 项真实 PostgreSQL 集成契约）**。其中包含：

- 未授权 `platform_scope` 不得创建/治理租户
- 非 Grant 管理主体不得自助提权
- 审批不可被其他 AI、动作或资源复用
- Event payload 拒绝非 JSON 可变对象
- Event Read/Publish/Subscribe/Replay 均需显式权限
- Workflow Signal 幂等重试不重复执行
- 同一幂等键冲突重用被拒绝
- 各内存 Repository 满足对应 Protocol
- Unit of Work 显式提交、隐式回滚与异常回滚
- SQLAlchemy metadata 命名约定与空域模型边界
- Alembic 单一基线修订链
- 数据库 URL 缺失/非 PostgreSQL 驱动 fail-closed
- Shared Audit / Identity ORM 与 Domain Model 隔离
- 租户、状态、唯一性、外键与 JSONB schema 约束
- Alembic `0002` 可完整离线编译
- SQLAlchemy Unit of Work 显式提交与默认回滚
- 异常回滚、Session 边界关闭及嵌套进入拒绝
- Identity SQL Repository 端口兼容与 Domain 往返
- SQL 查询/写入租户隔离及全局 AI 只读边界
- SQL AuditLog 租户隔离与上下文绑定
- Identity command 与 Audit 的单事务原子提交
- 业务失败、提交冲突及非法持久化作用域回滚
- 跨租户 AI 改派仅允许平台上下文
- Platform Identity Governor 对 AI 注册与改派的显式授权
- `platform_scope` 无 Governor 时拒绝且事务无残留
- Organization ORM、`0003` 迁移与租户复合外键
- Transactional Organization 的原子提交、状态持久化与隔离
- Permission ORM、JSONB actions 与 `0004` 迁移
- Transactional Permission 默认拒绝、授权/撤销及决策审计原子性
- Workflow 五表、`0005` 迁移与租户复合外键
- Workflow/Permission 共享事务、持久化状态机与 Signal 幂等收据
- Workflow W-04/W-05 事务型 AI 审批闸门及批准绑定
- Organization ↔ Permission 事务型 L2 边界
- Event 三表、`0006` 迁移与 JSONB payload
- handler Registry 分离、事务发布、失败尝试持久化与成功重放
- Runtime R-01～R-10、上下文不可提升与 Kernel 集成探针
- Identity I-07/I-08 与 Runtime R-11 强制会话边界
- Credential Validate/Revoke、Session 强制绑定与 `0007` 迁移
- 持久化 Identity Governor、bootstrap 切换与最后 Governor 防锁死

## 计划文档

- [../../docs/architecture/KERNEL_CONTRACT_TEST_PLAN.md](../../docs/architecture/KERNEL_CONTRACT_TEST_PLAN.md)
