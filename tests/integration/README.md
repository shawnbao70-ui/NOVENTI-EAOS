# PostgreSQL Integration Contracts

这些测试会执行迁移、清空表并在结束时 downgrade，具有破坏性。

## 安全门

- 只读取 `EAOS_TEST_DATABASE_URL`
- 驱动必须为 `postgresql+psycopg`
- 数据库名必须以 `eaos_test` 开头
- 禁止对开发、预生产或生产数据库运行

## 运行

先创建专用空数据库并通过安全方式设置连接变量，然后执行：

```bash
python -m pytest -m postgresql -v -p no:cacheprovider
```

未配置连接时，该测试模块自动跳过，不会回退到 SQLite 冒充 PostgreSQL 验证。

## Critical subset（PHX-G414）

Shard `integration_critical` in `tests/contracts/shards.yaml`:

- `test_postgresql_persistence.py`
- `test_crm_c1_postgresql.py` / `test_crm_z1_postgresql.py`
- `test_finance_f1_postgresql.py` / `test_finance_n1_postgresql.py`
- `test_inventory_i1_postgresql.py`

```bash
python scripts/run_contract_shard.py integration_critical --pytest-arg=-m --pytest-arg=postgresql
```

Requires `EAOS_TEST_DATABASE_URL` pointing at a dedicated `eaos_test*` database. Host PostgreSQL install is out of scope without separate PO auth.

## 覆盖范围

- Alembic `base → 0010 head → base`
- `kernel` schema 与修订版本
- Transactional Identity + Audit 原子写入
- PostgreSQL partial unique index 的 AI 改派历史
- Organization / Permission / Workflow / Knowledge / Event 真实事务往返
- Event JSONB、订阅与 Delivery 状态持久化
- Credential → Session 绑定与撤销后新会话拒绝
- Platform Identity Governor 持久化授权
