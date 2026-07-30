# Runtime Foundation 接口规格

**文档 ID：** IF-RUNTIME-001  
**版本：** 0.1  
**阶段：** PHX-005  
**状态：** 已批准，待实现

## 目的

定义 Platform Runtime 的上下文构造、传播、快照、执行守卫与可观测绑定接口。

## 不变式

1. 复用 `kernel.shared.ExecutionContext`，不得创建平行安全上下文。
2. 非法上下文在 operation 调用前失败关闭，且 operation 零执行。
3. 传播不得更换租户、主体、主体类型、平台作用域或关联 ID。
4. 快照必须 JSON-safe、可版本化且恢复后字段等价。
5. Runtime 不复制 Permission 求值或 Kernel 审计。

## 接口

### `InboundContextBuilder.build`

- 输入：受信任适配器提供的原始字段
- 输出：已校验 `ExecutionContext`
- 参数：`tenant_data_plane` 指明租户数据面或平台治理面
- 错误：沿用 `CTX_*`

### `ContextPropagator.propagate`

- 输入：父上下文与可选非安全覆盖字段
- 输出：新的不可变 `ExecutionContext`
- 允许补充：`package_id`、`locale`、`trace_id`、`approval_ref`
- 禁止覆盖安全字段或已绑定值
- 错误：`RT_PROPAGATION_VIOLATION`

### `ContextSnapshot.capture / restore`

- 捕获全部上下文字段为版本化 JSON-safe 映射
- UUID 与 datetime 使用规范字符串
- 未知版本或无效字段恢复失败
- 错误：`RT_SNAPSHOT_INVALID`

### `RuntimeExecutor.execute`

- 先调用 Kernel `require_context`
- 上下文携带 `session_id` 时强制调用注入的 Identity SessionValidator
- 缺少校验器或校验失败统一 `CTX_INVALID`
- 校验通过后仅调用 operation 一次，并原样传入 ctx
- KernelError 与 operation 异常不吞噬、不转换

### `ObservabilityBinding.from_context`

- 输出：`correlation_id`、`tenant_id`、`subject_id`、`subject_type`、可选 `trace_id/package_id`
- 不包含凭证、payload、审批内容或其他敏感数据

## Foundation 边界

无 FastAPI、AI Runtime、异步 worker、数据库迁移、包沙箱或 OpenTelemetry SDK。

## 关联

- [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md)
- [RUNTIME_CONTRACT_TEST_PLAN.md](RUNTIME_CONTRACT_TEST_PLAN.md)
- [../decisions/ADR-0013-runtime-foundation-boundary.md](../decisions/ADR-0013-runtime-foundation-boundary.md)
