# 共享执行上下文契约

**文档 ID：** IF-CTX-001  
**版本：** 0.2  
**阶段：** PHX-004 / PHX-005  
**状态：** Kernel 与 Runtime 传播切片已实现  
**仓库：** `NOVENTI-EAOS`  
**落位：** `kernel/shared/` 唯一定义；`runtime/` 负责构造与传播

---

## 标题

EAOS 执行上下文（Execution Context）契约

## 目的

定义所有 Kernel / Runtime / API 调用必须携带的执行上下文，确保租户隔离、身份绑定、关联追踪与审计一致。

## 范围

上下文字段、校验规则与传播规则。

## 当前状态

**Kernel 契约与 PHX-005 Runtime 传播实现已完成**

## 未来扩展

序列化格式（JSON/Header）、语言 SDK 辅助类型。

---

## 1. 上下文字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `tenant_id` | 条件必填* | 租户 UUID |
| `subject_id` | 是 | 调用主体 UUID |
| `subject_type` | 是 | `human` / `ai` / `service` / … |
| `correlation_id` | 是 | 全链路关联 ID |
| `session_id` | 否 | 人类会话 |
| `package_id` | 否 | 发起包 |
| `locale` | 否 | 语言区域 |
| `request_time` | 是 | UTC |
| `trace_id` | 否 | 分布式追踪 |
| `approval_ref` | 否 | 关联审批/流程实例 |

\*平台级治理动作可无租户，但必须显式标记 `platform_scope=true` 且强审计；租户数据面操作 **必须** 有 `tenant_id`。

---

## 2. 校验规则（失败关闭）

| 条件 | 错误码 |
|------|--------|
| 租户数据面缺少 `tenant_id` | `CTX_MISSING_TENANT` |
| 缺少 `subject_id` | `CTX_MISSING_SUBJECT` |
| 缺少 `correlation_id` | `CTX_MISSING_CORRELATION` |
| 上下文过期/被撤销会话 | `CTX_INVALID` |

**规则：** 校验失败不得继续产生业务副作用。

---

## 3. 传播规则

1. **入站 API** 负责构造/校验上下文，再调用 Kernel。  
2. **Kernel → Kernel** 必须原样传递 `correlation_id`，不得静默更换。  
3. **事件发布** 必须将 `tenant_id` / `correlation_id` 写入信封。  
4. **AI Runtime** 继承调用方上下文；工具调用不得提升租户或主体。  
5. **异步作业** 必须持久化上下文快照，唤醒时恢复。  
6. **Runtime 会话守卫**：携带 `session_id` 时必须经 `Identity.ValidateSession`；具体 Identity 错误在 Runtime 边界统一映射为 `CTX_INVALID`。

---

## 4. 与审计的关系

凡副作用操作成功，审计记录至少包含：

- `tenant_id`（若适用）
- `subject_id`
- `correlation_id`
- `action`
- `resource` 摘要
- `timestamp`
- `result`（ok/error code）

---

## 5. 与权限求值的关系

`Permission.Evaluate` 的输入上下文必须与执行上下文一致：

- 不得用 A 租户上下文去操作 B 租户资源  
- 不得用服务主体伪装人类主体而不留痕  

---

## 6. 伪类型（文档级，非代码）

```text
ExecutionContext {
  tenant_id?: UUID
  platform_scope?: boolean
  subject_id: UUID
  subject_type: enum
  correlation_id: UUID | string
  session_id?: UUID
  package_id?: string
  locale?: string
  request_time: datetime
  trace_id?: string
  approval_ref?: string
}
```

## 关联文档

- [KERNEL_INTERFACES.md](KERNEL_INTERFACES.md)
- [ERROR_CODES.md](ERROR_CODES.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
- [../decisions/ADR-0009-kernel-persistence-tenancy.md](../decisions/ADR-0009-kernel-persistence-tenancy.md)
- [../../kernel/shared/README.md](../../kernel/shared/README.md)
