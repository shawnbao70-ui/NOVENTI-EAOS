# ADR-0013 — Runtime Foundation 边界

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-005

## 上下文

PHX-004 已提供唯一 `ExecutionContext`、Kernel fail-closed 校验、Permission 求值、审计与事务边界。PHX-005 需要在执行入口传播并强制这些不变量，但不得复制 Kernel 权限逻辑或抢跑 API、AI Runtime 与异步 worker。

## 决策

1. `kernel.shared.ExecutionContext` 是唯一上下文类型；Runtime 不派生安全上下文。
2. Foundation 使用显式 `RuntimeExecutor.execute(ctx, operation)` 网关。
3. Runtime 负责入站构造、传播限制、JSON 快照/恢复和可观测字段绑定。
4. `correlation_id`、`tenant_id`、`subject_id`、`subject_type` 与 `platform_scope` 在传播中不可覆盖。
5. `package_id`、`locale`、`trace_id`、`approval_ref` 可受控补充，但不得清除已有值或改变安全主体。
6. Permission 继续由 Kernel 求值；Runtime Foundation 只阻止非法上下文到达操作。
7. ContextSnapshot 为内存/JSON-safe 值对象，不新增数据库迁移。
8. `capability_scope` 延后至 Permission/Runtime 深化，不加入 ExecutionContext。

## 明确排除

- FastAPI、HTTP Header 映射
- AI Runtime 与工具执行
- 异步 worker、job 表、租约及 DLQ
- 包沙箱
- OpenTelemetry SDK、health/metrics 端点

## 后果

- `runtime/` 只依赖 Kernel 公共类型与服务接口。
- Runtime observability binding 不替代 Kernel AuditLog。
- 后续 API、Package、AI 层必须经 Runtime 执行入口或等价适配器。

## 关联

- [../blueprint/RUNTIME_BLUEPRINT.md](../blueprint/RUNTIME_BLUEPRINT.md)
- [../architecture/EXECUTION_CONTEXT.md](../architecture/EXECUTION_CONTEXT.md)
- [../architecture/RUNTIME_INTERFACE.md](../architecture/RUNTIME_INTERFACE.md)
