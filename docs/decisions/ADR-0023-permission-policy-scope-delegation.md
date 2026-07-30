# ADR-0023 — Permission Policy, Scope, Delegation and Explain

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-K08  
**归属：** Core Kernel / Permission

## 背景

PHX-004 Foundation 已实现 positive Grant、Revoke、默认拒绝、Evaluate、Explain 与决策持久化，但固定 `policy_version`、未执行的 `conditions_ref`、无 Scope 层级、无显式 deny、无 Delegation 与无乐观锁，不足以作为 EAOS 的唯一授权真相源。

## 决策

### 1. 唯一求值入口

- `Permission.Evaluate` 是运行时授权决策唯一入口。
- 无有效 Identity、Tenant、Scope、Policy、Condition 或证据时默认 deny。
- Membership role label、Workflow approval、AI assignment 与 Smart Terminal 表现均不直接产生 Permission。

### 2. 类型化策略

- Policy 是可版本化、不可变发布的规则集合。
- Policy 生命周期：`DRAFT → ACTIVE → DEPRECATED`；ACTIVE 版本不可原地修改。
- Rule 使用类型化字段表达 principal、action、resource type、scope、effect 与 condition reference。
- 禁止在 Kernel 中执行任意脚本、SQL、模板或动态代码作为策略。

### 3. Effect 合并

1. 任一匹配的显式 `DENY` 优先。
2. 无 deny 且存在匹配 `ALLOW` 时允许。
3. 无匹配规则或 Grant 时默认拒绝。
4. Human approval 不改变 Permission effect；高影响动作在 `ALLOW` 后仍须独立通过 Workflow。

### 4. Scope 模型

Scope 由窄到宽：

```text
RESOURCE < ORG_UNIT < ENTERPRISE < TENANT
```

- Tenant 是隔离边界，任何 Scope 不得跨 Tenant。
- Enterprise / Org Unit 必须引用 PHX-K07 Organization 真相源。
- Org Unit scope 可覆盖其后代，但必须通过受信 Scope Resolver 验证 ancestry。
- Resource scope 精确匹配 `resource_type + resource_id`。
- Scope 不由客户端任意声明为可信；API/Runtime 负责构造受信 Resource Descriptor。

### 5. Direct Grant

- Direct Grant 是管理员签发的显式 ALLOW entitlement。
- Grant 必须绑定 Tenant、Principal、Resource Type、Scope 与 Actions。
- `conditions_ref` 存在但无法解析或返回 false 时，Grant 不生效。
- Principal 必须由 Identity 证明 active 且具备同 Tenant 资格。

### 6. Delegation

- Delegation 产生带 `parent_grant_id` 的新 Grant，不修改父 Grant。
- Delegator 必须是父 Grant 的 Principal，且父 Grant 显式允许 delegation。
- Delegated Actions、Scope、expiry 与 remaining depth 只能等于或窄于父 Grant。
- delegation depth 每次减一；为零时不可继续委派。
- 父链任一 Grant revoked、expired、condition false 或 Principal 失效时，子 Grant 立即不生效。
- 禁止循环 delegation；链路必须可解释、可审计。

### 7. 生命周期与并发

- Grant：`ACTIVE → REVOKED`，REVOKED 终态。
- Revoke 必须提供 reason 与 `expected_version`。
- Repository 使用数据库原子乐观锁；stale 更新返回 `PERMISSION_VERSION_CONFLICT`。
- Policy activation、deprecation 与 Grant delegation/revocation必须在单一 Unit of Work 中提交审计。

### 8. Explain 与可见性

PermissionDecision 必须保存：

- effect、reason code、policy version
- matched policy/rule/grant references
- evaluated scope 与 condition outcome 摘要
- correlation、principal、resource 与 decision time

Explain 不得暴露秘密、策略原文、跨 Tenant 资源存在性或未经授权的 Principal 权限。Principal 可读取自己的决策；审计员/受信运行时代理可读取其授权范围内的决策。

### 9. 查询与代理

- `ListEffective` 仅返回已验证父链、expiry、condition 与 Scope 后的有效权限。
- 调用方只能查询自己，除非被配置为受信 evaluation proxy / permission auditor。
- API 不接受客户端声明 `tenant_id`、`platform_scope` 或任意代理身份。

## Explicit Defer

- 通用脚本策略语言与第三方 Policy Engine
- 平台跨 Tenant Policy 与 break-glass
- Role/Group 自动展开
- 法律/商业策略内容
- 高影响动作分类器（由 Workflow / Governance 协作）
- 可靠 Permission domain event outbox（PHX-P11）

## 后果

- 新增 Policy / PolicyRule 模型与迁移。
- 扩展 Grant 的 Scope、Delegation 与乐观锁字段。
- 扩展 PermissionDecision 的 Explain evidence。
- 引入 Identity Principal Eligibility、Organization Scope Resolver 与 Condition Evaluator ports。
- Foundation `conditions_ref` 不再被忽略；无 resolver 时 fail closed。

## 关联

- [BOOK05](../constitution/BOOK05.md)
- [BOOK10](../constitution/BOOK10.md)
- [BOOK19](../constitution/BOOK19.md)
- [BOOK23](../constitution/BOOK23.md)
- [Permission Interface](../architecture/PERMISSION_INTERFACE.md)
- [ADR-0008](ADR-0008-ai-human-approval.md)
- [ADR-0022](ADR-0022-organization-lifecycle-hierarchy.md)
