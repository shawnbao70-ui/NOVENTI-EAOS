# kernel/identity/

Identity Kernel（PHX-006 已完成并人工批准）。

## 已实现

- `IdentityService`：Foundation 接口 + ValidateSession
- `InMemoryIdentityRepository`（ADR-0010）
- 失败关闭上下文校验、租户隔离、审计、凭证不回传
- Platform Identity Governor：平台注册 AI 与跨租户改派显式授权
- SQLAlchemy Repository / Unit of Work / TransactionalIdentityService
- Session Boundary Closure：过期/撤销/租户/主体绑定校验
- Runtime 强制 SessionValidator，失败统一映射 `CTX_INVALID`
- Credential Validate/Revoke 生命周期；CreateSession 强制 credential_id
- Alembic `0007` 新会话凭证来源绑定
- Platform Identity Governor 授权历史与 Alembic `0008`
- Bootstrap 仅引导首条授权；之后数据库为唯一真相源
- AI 全局单一 active assignment 与 Alembic `0009`
- INHERIT predecessor 谱系；不隐式迁移权限、知识、记忆或会话
- ARCHIVE 无需目标租户
- AI Employee Profile 独立一对一持久化与 Alembic `0010`
- Capability / owner policy 仅保存受治理引用；Permission 仍是授权真相源
- Governor-only Profile 更新与 expected_version 乐观锁
- OpenAPI 3.1 Identity HTTP 契约（仅规范，无 Router 实现）
- Subject / Credential / Session / Assignment / Governor / Profile 状态机

## 运行测试

```bash
pytest tests/contracts/test_identity_service.py
```

## 规格

- [../../docs/architecture/IDENTITY_INTERFACE.md](../../docs/architecture/IDENTITY_INTERFACE.md)
- [../../docs/decisions/ADR-0010-inmemory-foundation-slice.md](../../docs/decisions/ADR-0010-inmemory-foundation-slice.md)
