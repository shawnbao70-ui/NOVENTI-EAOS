# PHX-006 Identity Kernel 验收

**状态：** 完成（人工批准）  
**日期：** 2026-07-18

## 已完成切片：Session Boundary Closure

- [x] ADR-0014 会话校验与 Runtime 强制边界
- [x] `Identity.ValidateSession`
- [x] 有效、过期、撤销、跨租户与主体不匹配契约
- [x] SQLAlchemy TransactionalIdentity 暴露校验入口
- [x] Runtime 携带 session_id 时强制注入 SessionValidator
- [x] Runtime 统一映射 `CTX_INVALID` 且 operation 零执行
- [x] 真实 PostgreSQL Create → Validate → Revoke → Deny
- [x] 完整回归 `143 passed`

## 后续 Identity 深化

- [x] Credential revoke / validate 与 CreateSession 凭证绑定
- [x] Alembic `0007` Session → Credential 可追溯绑定
- [x] Platform Identity Governor 持久化决策与实现
- [x] Bootstrap 首条授权、持久真相源与最后 Governor 防锁死
- [x] Alembic `0008` Governor 授权历史
- [x] AI 多租户派驻与 INHERIT 语义 ADR
- [x] 全局单一 active assignment、INHERIT predecessor 与 ARCHIVE 可选目标
- [x] Alembic `0009` AI assignment 约束与谱系
- [x] AI profile / owner policy 独立持久化
- [x] Capability profile 引用与 Permission 授权边界
- [x] Governor-only 更新与 expected_version 乐观锁
- [x] Alembic `0010` AI Employee Profile
- [x] Identity ↔ Organization Membership Eligibility Port
- [x] AI 同租户 active assignment 资格
- [x] 跨租户改派原子结束旧 membership
- [x] SQLite 与真实 PostgreSQL L2 契约
- [x] OpenAPI 3.1 Identity HTTP IDL
- [x] 认证层派生 ExecutionContext 安全字段；客户端仅可提供 correlation ID
- [x] Subject / Credential / Session / Assignment / Governor / Profile 状态机
- [x] OpenAPI 引用、操作 ID 与安全边界自动契约
- [x] PHX-006 最终人工确认（2026-07-18）

## 当前验证

- Identity 当前切片完整回归：`160 passed`
- 包含真实 PostgreSQL `base → 0010 → base`
- 零 IDE lint 错误

## 明确非目标

FastAPI/OAuth/OIDC/JWT、AI Runtime、Knowledge 迁移、物理多租户与 Legacy 集成。

## 依据

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [../architecture/EXECUTION_CONTEXT.md](../architecture/EXECUTION_CONTEXT.md)
- [../decisions/ADR-0014-identity-session-validation.md](../decisions/ADR-0014-identity-session-validation.md)
