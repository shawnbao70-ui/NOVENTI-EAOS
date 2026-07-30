# PHX-004 Kernel Foundation 验收

**状态：** 完成（人工批准）  
**日期：** 2026-07-18  
**范围：** Shared、Identity、Organization、Permission、Workflow、Event Bus Foundation

## 退出标准

| 验收项 | 状态 | 证据 |
|--------|------|------|
| Constitution / Blueprint / Standards / Interfaces 先于实现 | 通过 | PHX-001～003 与 Architecture 文档 |
| ExecutionContext、稳定错误码、Audit、fail-closed | 通过 | `kernel/shared` 与负面契约 |
| 各域 Repository Protocol 与内存适配器 | 通过 | `test_persistence_ports.py` |
| SQLAlchemy ORM 与 Alembic 线性迁移 | 通过 | `0001`～`0006`，离线 PostgreSQL DDL 编译 |
| Unit of Work 显式提交、默认回滚、Session 关闭 | 通过 | `test_sqlalchemy_unit_of_work.py` |
| Identity / Organization / Permission / Workflow / Event 事务接线 | 通过 | `test_transactional_*.py` |
| Repository 查询层租户隔离 | 通过 | SQL adapter 与跨租户契约 |
| Permission 默认拒绝且决策可审计 | 通过 | 内存及事务型 Permission 契约 |
| ADR-0008 AI 审批主体/动作/资源绑定 | 通过 | 内存及事务型 Workflow W-04/W-05 |
| Organization 角色不隐式产生 Permission | 通过 | 内存及事务型 L2 跨域契约 |
| Event 不可变、幂等、失败可重放 | 通过 | 内存及事务型 Event 契约 |
| 无 Legacy 代码依赖或写入 | 通过 | 仓库边界与实现检查 |
| 真实 PostgreSQL upgrade / repository / downgrade | 通过 | 专用便携 PostgreSQL 17；4 项集成契约 |

## 当前验证

- `123 passed`
- PostgreSQL `base → 0006 → base` 迁移链通过
- 零 IDE lint 错误
- PostgreSQL 集成套件通过 Identity、Organization、Permission、Workflow、Event 往返及 partial unique index 验证

## Foundation 明确边界

以下能力属于后续完整 Kernel 或 PHX-P11，不阻塞 PHX-004 Foundation：

- Event 异步 worker、租约、退避重试与 DLQ 运维接口
- 持久化 Policy 文档与完整策略引擎
- Knowledge Kernel、Runtime、API/FastAPI 与业务包
- 物理多租户数据库隔离

## 最终退出动作

在专用 PostgreSQL 上执行：

```bash
python -m pytest -m postgresql -v -p no:cacheprovider
```

迁移链、五域与 Event 往返、PostgreSQL 特有约束已全部通过。2026-07-18 已获人工批准，PHX-004 正式完成。

## 依据

- [../architecture/KERNEL_CONTRACT_TEST_PLAN.md](../architecture/KERNEL_CONTRACT_TEST_PLAN.md)
- [../architecture/PERSISTENCE_PORTS.md](../architecture/PERSISTENCE_PORTS.md)
- [../decisions/ADR-0012-kernel-database-orm.md](../decisions/ADR-0012-kernel-database-orm.md)
- [TASKS.md](TASKS.md)
