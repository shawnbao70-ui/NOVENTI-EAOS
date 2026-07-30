# ADR-0102 — Opt-in Context Roles Evaluate Grant Map Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G83  
**归属：** Permission Kernel / ExecutionContext

## 背景

G82 已将 JWT `eaos_roles` 灌入 `ExecutionContext.roles`。evaluate 仍只走仓库 grants/policies，角色无法贡献 allow。

## 决策

1. 可选 env `EAOS_PERMISSION_ROLE_GRANT_MAP`：`role=type:action|type:action,...`；空=关闭（行为与 G82 前一致）。  
2. evaluate 在 grant/policy 循环后，用 `ctx.roles` 与 map 求交；命中则 `allow_hit`，证据记 `matched_roles`。  
3. **Deny 仍优先**于 role allow。  
4. 仅 role 命中 → `reason_code=MATCHED_CONTEXT_ROLE`；grant/policy 亦命中 → 仍为 `MATCHED_ACTIVE_GRANT`。  
5. explain / HTTP explanation 暴露 `matched_roles`；evidence JSON 可持久化该字段（无 Alembic）。  
6. 不写 `kernel.grants`；不建 Role 表；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Role 目录 / 组成员展开 / 自动写 grant  
- Social login / MFA 注册 UX（多 provider 登录薄门禁见 ADR-0103 / PHX-G84）  
- 只读 roles catalog（见 ADR-0107 / PHX-G88）  
- 平台面 JWT 角色消费  

## 关联

- [ADR-0101-jwt-eaos-roles-execution-context.md](ADR-0101-jwt-eaos-roles-execution-context.md)
- [../project/PHX-G83_ARCHITECTURE_GATE.md](../project/PHX-G83_ARCHITECTURE_GATE.md)
