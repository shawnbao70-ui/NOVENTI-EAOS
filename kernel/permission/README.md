# kernel/permission/

Permission Kernel 模块边界。

## 职责

策略、授予、委派、统一求值、解释与决策审计。

## 状态

PHX-K08 已完成并验收：

- Policy / Rule（DRAFT → ACTIVE → DEPRECATED）
- Scope：Tenant / Enterprise / Org Unit / Resource
- Grant / Revoke（expected_version）
- Delegation（父链、depth、只能缩小）
- Evaluate deny-overrides + 默认拒绝
- Explain / ListEffective（self-or-auditor）
- PrincipalEligibility / ConditionEvaluator / ScopeResolver ports
- SQLAlchemy + Alembic `0012_permission_policy_scope`
- OpenAPI 3.1、状态机与事件目录

## 测试

```bash
python -m pytest tests/contracts/test_permission_service.py tests/contracts/test_permission_policy_delegation.py tests/contracts/test_permission_openapi.py -p no:cacheprovider
```

## 规格

- [../../docs/architecture/PERMISSION_INTERFACE.md](../../docs/architecture/PERMISSION_INTERFACE.md)
- [../../docs/architecture/PERMISSION_STATE_MACHINES.md](../../docs/architecture/PERMISSION_STATE_MACHINES.md)
- [../../docs/api/permission.openapi.yaml](../../docs/api/permission.openapi.yaml)
- [../../docs/decisions/ADR-0023-permission-policy-scope-delegation.md](../../docs/decisions/ADR-0023-permission-policy-scope-delegation.md)
