# ADR-0101 — JWT eaos_roles → ExecutionContext Roles Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G82  
**归属：** Platform API Gateway / ExecutionContext

## 背景

G81 可将 IdP 角色映射进 EAOS JWT `eaos_roles`。Gateway 派生的 `ExecutionContext` 尚未承载该声明，`/v1/context` 也无法观测。

## 决策

1. `ExecutionContext.roles: tuple[str, ...] = ()`（默认空）。  
2. 租户面 `context_from_tenant_claims` 解析 JWT `eaos_roles`：缺失/null → `()`；须为字符串数组；strip、去空、排序去重。  
3. 类型非法 → `400` + `CTX_INVALID`（fail closed）。  
4. Dev header 路径恒 `roles=()`；无角色提升头。  
5. `serialize_context` / `GET /v1/context` 暴露 `roles: string[]`。  
6. body 不可覆盖 `roles`（echo 与 domain override 集合）。  
7. 不写 Permission grants；不改 OIDC mint；无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Permission Kernel 按 `roles` 自动授权 / 策略映射（薄 evaluate map 见 ADR-0102 / PHX-G83）  
- Social login / MFA 注册 UX  
- 平台面 JWT 角色消费  

## 关联

- [ADR-0100-oidc-claim-role-mint.md](ADR-0100-oidc-claim-role-mint.md)
- [../project/PHX-G82_ARCHITECTURE_GATE.md](../project/PHX-G82_ARCHITECTURE_GATE.md)
