# kernel/organization/

Organization Kernel 模块边界。

## 职责

租户、组织单元、成员关系。

## 状态

PHX-004 垂直切片已实现：

- 租户创建、查询、暂停与恢复
- 组织单元新增/更新与树查询
- 成员关系新增、移除、查询与同租户转移
- 跨租户失败关闭与副作用审计
- SQLAlchemy 映射与 Alembic `0003_organization`
- 租户绑定 Repository 与 TransactionalOrganizationService
- 租户复合外键、活跃 Membership 唯一约束
- Identity Membership Eligibility Port：主体 active 与同租户资格
- AI active assignment 资格与跨租户改派共享事务协调器

PHX-K07 已 Fully Accepted：

- Tenant 隔离边界与独立 Enterprise 法人/组织主体
- CreateTenant 原子创建 primary Enterprise
- Unit 同 Enterprise 无环层级与暂停租户写阻断
- Membership active / suspended / ended 生命周期
- Tenant、Unit、Membership `expected_version` 乐观锁
- Organization OpenAPI 3.1 与状态机规范

CloseTenant 执行、primary-admin Permission 引导、跨 Tenant federation 与可靠事件 outbox 按 PHX-K07 Gate 明确延后。

## 测试

```bash
python -m pytest tests/contracts/test_organization_service.py tests/contracts/test_organization_openapi.py -p no:cacheprovider
```

## 规格

- [../../docs/architecture/ORGANIZATION_INTERFACE.md](../../docs/architecture/ORGANIZATION_INTERFACE.md)
- [../../docs/architecture/KERNEL_DATA_MODEL.md](../../docs/architecture/KERNEL_DATA_MODEL.md)
- [../../docs/architecture/ORGANIZATION_STATE_MACHINES.md](../../docs/architecture/ORGANIZATION_STATE_MACHINES.md)
- [../../docs/api/organization.openapi.yaml](../../docs/api/organization.openapi.yaml)
- [../../docs/project/PHX-K07_ARCHITECTURE_GATE.md](../../docs/project/PHX-K07_ARCHITECTURE_GATE.md)
