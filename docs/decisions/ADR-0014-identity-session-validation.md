# ADR-0014 — Identity 会话校验与 Runtime 强制边界

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. `Identity.ValidateSession` 是会话状态真相入口。
2. Identity 直接调用返回具体错误：不存在、过期、撤销。
3. 会话必须同时匹配执行上下文的 `tenant_id` 与 `subject_id`。
4. Runtime 遇到携带 `session_id` 的上下文时必须注入 SessionValidator；缺少校验器即失败关闭。
5. Runtime 将所有会话校验失败统一映射为 `CTX_INVALID`，不向执行层泄露会话存在性或状态。
6. 无 `session_id` 的服务/平台上下文继续使用 PHX-005 基础守卫。
7. 本切片复用现有 sessions 表，不新增迁移。

## 后果

- Identity 保留运维与受信任调用所需诊断能力。
- Runtime operation 在会话有效性确认前零执行。
- 凭证撤销/轮换和 AI 派驻策略留给后续 PHX-006 切片。

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [../architecture/RUNTIME_INTERFACE.md](../architecture/RUNTIME_INTERFACE.md)
- [../architecture/EXECUTION_CONTEXT.md](../architecture/EXECUTION_CONTEXT.md)
