# Kernel 错误码总表

**文档 ID：** ERR-KERNEL-001  
**版本：** 0.1  
**阶段：** Interfaces / PHX-004  
**状态：** 基线  
**仓库：** `NOVENTI-EAOS`

---

## 标题

EAOS Kernel 错误码总表

## 目的

为 Identity / Organization / Permission / Workflow / 共享上下文提供稳定、机器可读的错误码，供 API、事件与契约测试统一使用。

## 范围

错误码命名与语义。不含 HTTP 状态到错误码的最终映射表（实现期可增补）。

## 当前状态

**已发布基线**

## 未来扩展

Event / AI Runtime 错误码继续分册深化；Knowledge（KNOWLEDGE_）已在 PHX-K10 发布。

---

## 1. 约定

| 规则 | 说明 |
|------|------|
| 格式 | `DOMAIN_REASON` 大写蛇形 |
| 稳定性 | 一经发布不得复用不同语义 |
| 默认安全 | 对外 message 不泄露跨租户存在性细节 |
| 关联 | 响应必须带 `correlation_id` |

### 建议 HTTP 映射（非强制终局）

| 类别 | HTTP |
|------|------|
| 校验/参数 | 400 |
| 未认证 | 401 |
| 无权限/跨租户 | 403 |
| 不存在（同租户可见范围） | 404 |
| 冲突/重复 | 409 |
| 预置条件失败（如缺批准） | 412 或 409（实现期锁定） |
| 内部 | 500 |

---

## 2. 共享 / 上下文（CTX / COMMON）

| 错误码 | 语义 |
|--------|------|
| `CTX_MISSING_TENANT` | 缺少 tenant_id |
| `CTX_MISSING_SUBJECT` | 缺少 subject_id |
| `CTX_MISSING_CORRELATION` | 缺少 correlation_id |
| `CTX_INVALID` | 上下文非法或过期 |
| `RT_PROPAGATION_VIOLATION` | Runtime 传播试图更换或提升安全上下文 |
| `RT_SNAPSHOT_INVALID` | Runtime 上下文快照版本或字段非法 |
| `COMMON_VALIDATION_FAILED` | 通用校验失败 |
| `COMMON_CONFLICT` | 通用冲突 |
| `COMMON_NOT_FOUND` | 通用未找到（同租户） |
| `COMMON_INTERNAL` | 内部错误 |
| `COMMON_NOT_IMPLEMENTED` | 尚未实现 |

---

## 3. Identity（IDENTITY_）

| 错误码 | 语义 |
|--------|------|
| `IDENTITY_DUPLICATE` | 主体或外部引用重复 |
| `IDENTITY_INVALID_TYPE` | subject_type 非法 |
| `IDENTITY_NOT_FOUND` | 主体不存在（可见范围） |
| `IDENTITY_CROSS_TENANT_FORBIDDEN` | Identity 写入越出租户绑定范围 |
| `IDENTITY_CREDENTIAL_INVALID` | 凭证无效 |
| `IDENTITY_CREDENTIAL_REVOKED` | 凭证已撤销 |
| `IDENTITY_SESSION_EXPIRED` | 会话过期 |
| `IDENTITY_SESSION_REVOKED` | 会话已撤销 |
| `IDENTITY_SESSION_NOT_FOUND` | 会话不存在或不属于当前租户/主体 |
| `IDENTITY_AI_NOT_ASSIGNABLE` | AI 不可派驻（状态不允许） |
| `IDENTITY_AI_ASSIGNMENT_CONFLICT` | 派驻冲突 |
| `IDENTITY_SECRET_LEAK_FORBIDDEN` | 试图回传/记录明文秘密（防护） |
| `IDENTITY_GOVERNOR_CONFLICT` | 主体已有 active Governor 授权 |
| `IDENTITY_GOVERNOR_NOT_FOUND` | active Governor 不存在 |
| `IDENTITY_GOVERNOR_LAST_ACTIVE` | 禁止撤销最后一个 active Governor |
| `IDENTITY_AI_PROFILE_NOT_FOUND` | AI Profile 不存在 |
| `IDENTITY_AI_PROFILE_CONFLICT` | AI Profile 乐观锁版本冲突 |

---

## 4. Organization（ORG_）

| 错误码 | 语义 |
|--------|------|
| `ORG_TENANT_INVALID` | 租户参数非法 |
| `ORG_TENANT_NOT_FOUND` | 租户不存在 |
| `ORG_TENANT_SUSPENDED` | 租户已暂停 |
| `ORG_TENANT_DUPLICATE_NAME` | 租户名冲突（若策略启用） |
| `ORG_TENANT_CLOSED` | 租户已关闭 |
| `ORG_ENTERPRISE_NOT_FOUND` | Enterprise 不存在或不属于 trusted tenant |
| `ORG_UNIT_NOT_FOUND` | 组织单元不存在 |
| `ORG_UNIT_PARENT_INVALID` | 父单元非法 |
| `ORG_UNIT_CROSS_TENANT` | 父/子跨租户 |
| `ORG_UNIT_ENTERPRISE_MISMATCH` | Unit / Membership 的 Enterprise 不一致 |
| `ORG_UNIT_CYCLE_DETECTED` | Unit 层级形成 self/cycle |
| `ORG_MEMBERSHIP_NOT_FOUND` | 成员关系不存在 |
| `ORG_CROSS_TENANT_FORBIDDEN` | 跨租户成员操作 |
| `ORG_MEMBERSHIP_DUPLICATE` | 重复成员关系 |
| `ORG_SUBJECT_INELIGIBLE` | 主体不存在、非 active 或不具备同租户 membership 资格 |
| `ORG_MEMBERSHIP_NOT_ACTIVE` | Membership 已结束或不允许当前修改 |
| `ORG_INVALID_STATE_TRANSITION` | Tenant / Enterprise / Unit / Membership 状态转换非法 |
| `ORG_VERSION_CONFLICT` | expected_version 与当前版本不一致 |
| `ORG_ACTIVE_DEPENDENCIES` | active 下级对象阻止关闭 |

---

## 5. Permission（PERMISSION_）

| 错误码 | 语义 |
|--------|------|
| `PERMISSION_DENIED` | 求值拒绝（通用） |
| `PERMISSION_GRANT_NOT_FOUND` | 授权记录不存在 |
| `PERMISSION_GRANT_EXPIRED` | 授权过期 |
| `PERMISSION_GRANT_CONFLICT` | 授权冲突 |
| `PERMISSION_GRANT_REVOKED` | 授权已撤销 |
| `PERMISSION_VERSION_CONFLICT` | Grant/Policy 乐观锁冲突 |
| `PERMISSION_PRINCIPAL_INELIGIBLE` | 主体不存在、非 active 或不具备同租户资格 |
| `PERMISSION_CONDITION_UNRESOLVED` | 条件引用无法解析、未知或求值错误 |
| `PERMISSION_POLICY_NOT_FOUND` | 策略不存在 |
| `PERMISSION_POLICY_DEPRECATED` | 策略已弃用不可用 |
| `PERMISSION_POLICY_CONFLICT` | 策略名称/版本冲突 |
| `PERMISSION_SCOPE_INVALID` | Scope 越界或 Organization 关系无效 |
| `PERMISSION_DELEGATION_FORBIDDEN` | 委派扩大、循环或 depth 耗尽 |
| `PERMISSION_CROSS_TENANT_FORBIDDEN` | 跨租户授权/求值 |
| `PERMISSION_EXPLAIN_UNAVAILABLE` | 无法生成解释 |

说明：`Evaluate` 正常返回 `effect=deny` **不一定**抛错；仅在调用方强依赖 allow 的命令路径上上送 `PERMISSION_DENIED`。

---

## 6. Workflow（WORKFLOW_）

| 错误码 | 语义 |
|--------|------|
| `WORKFLOW_DEFINITION_NOT_FOUND` | 定义不存在 |
| `WORKFLOW_DEFINITION_INVALID` | 定义非法 |
| `WORKFLOW_DEFINITION_CONFLICT` | 同租户范围内名称与版本冲突 |
| `WORKFLOW_INSTANCE_NOT_FOUND` | 实例不存在 |
| `WORKFLOW_INVALID_STATE` | 状态不允许该操作 |
| `WORKFLOW_TASK_NOT_FOUND` | 任务不存在 |
| `WORKFLOW_TASK_NOT_ASSIGNEE` | 非任务处理人 |
| `WORKFLOW_SIGNAL_UNKNOWN` | 未知信号 |
| `WORKFLOW_SIGNAL_CONFLICT` | 幂等键被不同请求复用 |
| `WORKFLOW_IDEMPOTENCY_REQUIRED` | 缺少幂等键 |
| `WORKFLOW_CANCEL_FORBIDDEN` | 无权取消 |
| `WORKFLOW_APPROVAL_REQUIRED` | 需要人工批准尚未完成 |
| `WORKFLOW_APPROVAL_REJECTED` | 审批已拒绝 |
| `WORKFLOW_APPROVAL_EXPIRED` | 批准绑定已过期 |
| `WORKFLOW_VERSION_CONFLICT` | Instance / Task 乐观锁版本冲突 |
| `WORKFLOW_BUSINESS_KEY_CONFLICT` | 同租户活跃 business_key 冲突 |
| `WORKFLOW_CROSS_TENANT_FORBIDDEN` | 跨租户流程操作 |

---

## 7. Knowledge（KNOWLEDGE_）

| 错误码 | 语义 |
|--------|------|
| `KNOWLEDGE_ENTITY_NOT_FOUND` | 实体不存在或跨租户不可见 |
| `KNOWLEDGE_LINK_NOT_FOUND` | 关系不存在或跨租户不可见 |
| `KNOWLEDGE_ENTITY_CONFLICT` | 活跃实体类型/名称冲突 |
| `KNOWLEDGE_LINK_INVALID` | 非法关系（如自环） |
| `KNOWLEDGE_PROVENANCE_REQUIRED` | 缺少 source_ref / reason |
| `KNOWLEDGE_DERIVED_MISLABELLED` | derived 伪装为非 derived / canonical |
| `KNOWLEDGE_ARCHIVED` | 实体已归档，不可读/写 |
| `KNOWLEDGE_RETENTION_EXPIRED` | retain_until 已到期 |
| `KNOWLEDGE_VERSION_CONFLICT` | Entity 乐观锁版本冲突 |
| `KNOWLEDGE_CROSS_TENANT_FORBIDDEN` | 跨租户知识操作 |
| `KNOWLEDGE_SECRET_FORBIDDEN` | attributes 含禁止的秘密字段 |

授权失败统一使用 `PERMISSION_DENIED`。

---

## 8. 事件（EVENT_）

| 错误码 | 语义 |
|--------|------|
| `EVENT_ENVELOPE_INVALID` | 信封不完整/非法 |
| `EVENT_NOT_FOUND` | 事件不存在或跨租户不可见 |
| `EVENT_SUBSCRIPTION_INVALID` | 订阅无效或重复 |
| `EVENT_DELIVERY_FAILED` | 投递失败（保留重放资格） |
| `EVENT_OUTBOX_NOT_FOUND` | Outbox 条目不存在 |
| `EVENT_DEAD_LETTER_NOT_FOUND` | DLQ 条目不存在或跨租户不可见 |
| `EVENT_LEASE_CONFLICT` | Worker 租约冲突 |

发布、入队、订阅、调度、读取、重放的授权失败统一使用 `PERMISSION_DENIED`。

---

## 9. AI Runtime（AI_）

| 错误码 | 语义 |
|--------|------|
| `AI_RUNTIME_REQUIRED` | 非 AI 主体或绕过 AI Runtime |
| `AI_TOOL_DENIED` | 工具未注册或无 invoke 权限 |
| `AI_APPROVAL_REQUIRED` | 高影响动作缺少批准 |
| `AI_COMMIT_FORBIDDEN` | 批准不匹配或不可提交 |
| `AI_MEMORY_DENIED` | 记忆访问拒绝或含秘密 |
| `AI_KNOWLEDGE_DENIED` | 知识访问拒绝 |

---

## 10. Smart Terminal（TERMINAL_）

| 错误码 | 语义 |
|--------|------|
| `TERMINAL_CONTEXT_ELEVATION_DENIED` | 客户端尝试提升 Subject / Tenant |
| `TERMINAL_DEVICE_UNTRUSTED` | 不可信设备尝试高影响 Commit |
| `TERMINAL_STALE_PREVIEW` | 预览已失效或不可提交 |
| `TERMINAL_APPROVAL_INVALID` | 缺少/无效批准或无法读取 Workflow |
| `TERMINAL_COMMIT_FORBIDDEN` | 批准不匹配或不可提交 |
| `TERMINAL_SECRET_DENIED` | 工作区文本含秘密字段 |

---

## 11. Package Platform（PACKAGE_）

| 错误码 | 语义 |
|--------|------|
| `PACKAGE_KERNEL_FORK_DENIED` | 试图分叉 Kernel 或占用保留资源 |
| `PACKAGE_MANIFEST_INVALID` | Manifest 结构/内容非法 |
| `PACKAGE_NOT_FOUND` | Manifest 不存在或跨租户不可见 |
| `PACKAGE_NOT_PUBLISHED` | 未发布不可安装 |
| `PACKAGE_NOT_INSTALLED` | 未安装或已禁用 |
| `PACKAGE_ALREADY_INSTALLED` | 同 key 已安装 |
| `PACKAGE_ACTION_UNDECLARED` | Action 未声明或不可解析 |
| `PACKAGE_SURFACE_UNDECLARED` | Surface 未声明 |
| `PACKAGE_VERSION_CONFLICT` | 版本冲突 |

---

## 12. Enterprise Brain & Twin（TWIN_ / BRAIN_）

| 错误码 | 语义 |
|--------|------|
| `TWIN_NOT_FOUND` | 孪生快照不存在或跨租户不可见 |
| `TWIN_PROVENANCE_REQUIRED` | 缺少 source_ref / reason |
| `TWIN_CONFIDENCE_INVALID` | 置信度不在 [0,1] |
| `TWIN_SECRET_DENIED` | 孪生状态含秘密字段 |
| `TWIN_EXECUTION_FORBIDDEN` | 孪生不得授权执行 |
| `BRAIN_NOT_FOUND` | 洞察不存在或跨租户不可见 |
| `BRAIN_PROVENANCE_REQUIRED` | 缺少 source_ref / reason |
| `BRAIN_CONFIDENCE_INVALID` | 置信度不在 [0,1] |
| `BRAIN_SECRET_DENIED` | 洞察含秘密字段 |
| `BRAIN_EXECUTION_FORBIDDEN` | Brain 不得执行/授权副作用 |
| `BRAIN_ADVISORY_REQUIRED` | 输出必须保持 advisory |

---

## 13. Marketplace（MARKETPLACE_）

| 错误码 | 语义 |
|--------|------|
| `MARKETPLACE_NOT_FOUND` | Listing 不存在或跨租户不可见 |
| `MARKETPLACE_SIGNATURE_REQUIRED` | 缺少签名引用 |
| `MARKETPLACE_NOT_APPROVED` | 未批准不可发布 |
| `MARKETPLACE_NOT_PUBLISHED` | 未发布不可获取 |
| `MARKETPLACE_REVOKED` | 已撤销 |
| `MARKETPLACE_CAPABILITY_REQUIRED` | 缺少能力声明 |
| `MARKETPLACE_ALREADY_ACQUIRED` | 租户已获取 |
| `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED` | 商业政策未批准 |

---

## 关联文档

- [KERNEL_INTERFACES.md](KERNEL_INTERFACES.md)
- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [ORGANIZATION_INTERFACE.md](ORGANIZATION_INTERFACE.md)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [WORKFLOW_INTERFACE.md](WORKFLOW_INTERFACE.md)
- [KNOWLEDGE_INTERFACE.md](KNOWLEDGE_INTERFACE.md)
- [EVENT_INTERFACE.md](EVENT_INTERFACE.md)
- [AI_RUNTIME_INTERFACE.md](AI_RUNTIME_INTERFACE.md)
- [SMART_TERMINAL_INTERFACE.md](SMART_TERMINAL_INTERFACE.md)
- [PACKAGE_INTERFACE.md](PACKAGE_INTERFACE.md)
- [BRAIN_TWIN_INTERFACE.md](BRAIN_TWIN_INTERFACE.md)
- [MARKETPLACE_INTERFACE.md](MARKETPLACE_INTERFACE.md)
- [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md)
- [../standards/API_STANDARD.md](../standards/API_STANDARD.md)
