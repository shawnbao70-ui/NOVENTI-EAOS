# kernel/shared/

跨 Kernel 域共享实现。

## 已实现

| 模块 | 说明 |
|------|------|
| `context.py` | `ExecutionContext` + `require_context` |
| `errors.py` | `ErrorCode` + `KernelError` |
| `results.py` | `KernelResult` 包络 |
| `audit.py` | `InMemoryAuditLog` |

## 契约

- [../../docs/architecture/EXECUTION_CONTEXT.md](../../docs/architecture/EXECUTION_CONTEXT.md)
- [../../docs/architecture/ERROR_CODES.md](../../docs/architecture/ERROR_CODES.md)
