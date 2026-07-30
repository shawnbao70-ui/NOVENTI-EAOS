# Identity Kernel 接口规格（细化）

**文档 ID：** IF-IDENTITY-001  
**版本：** 0.2  
**阶段：** PHX-004 持久化切片  
**状态：** Foundation SQLAlchemy 实现  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Identity Kernel 接口规格

## 目的

细化身份主体、AI 员工、会话与派驻相关接口，作为 PHX-006 实现依据。

## 范围

接口契约意图与不变式。Foundation Service、ORM、Repository 与事务型 SQLAlchemy 接线已实现。

## 当前状态

**PHX-006 完整接口、L2、OpenAPI 3.1 与状态机已实现**

## 未来扩展

PHX-K07+ API adapter、OAuth/OIDC/JWT 与 SDK 生成。

---

## 不变式

1. 身份全球唯一，不得重复  
2. AI 身份永久；派驻对象可变，但全局最多一个 active assignment  
3. 所有调用携带全局执行上下文（见 KERNEL_INTERFACES）  
4. 凭证密钥永不通过接口回传  

---

## 主体类型

`human` | `ai_employee` | `service` | `device` | `application` | `plugin`

---

## 接口明细

### Identity.RegisterSubject

- **意图：** 注册非 AI 主体  
- **输入（概念）：** tenant_id（若租户作用域）、subject_type、display_name、external_refs[]  
- **输出：** subject_id  
- **错误：** `IDENTITY_DUPLICATE`、`IDENTITY_INVALID_TYPE`  
- **审计：** 是  

### Identity.RegisterAIEmployee

- **意图：** 注册 AI 员工（永久 ID）  
- **输入：** display_name、capabilities_profile、owner_policy  
- **输出：** ai_subject_id  
- **约束：** ID 一经创建不可复用给其他主体  
- **权限：** `platform_scope` 且调用主体属于 Platform Identity Governor
- **审计：** 是  

### Identity.GetAIProfile

- **意图：** 获取 AI 的受治理 Profile 引用
- **输入：** ai_subject_id
- **输出：** capabilities_profile_ref、owner_policy_ref、version
- **权限：** `platform_scope` 且调用主体属于 Platform Identity Governor
- **约束：** Profile 不包含授权声明、密钥、知识或记忆

### Identity.UpdateAIProfile

- **意图：** 更新 capability / owner policy 引用
- **输入：** ai_subject_id、expected_version、capabilities_profile、owner_policy
- **输出：** 更新后的 Profile
- **权限：** `platform_scope` 且调用主体属于 Platform Identity Governor
- **约束：** expected_version 不匹配时返回 `IDENTITY_AI_PROFILE_CONFLICT`；Identity 不依据 capability 引用授权
- **审计：** 是

### Identity.ResolveSubject

- **意图：** 解析主体  
- **输入：** subject_id 或 external_ref  
- **输出：** 主体描述（无密钥）  
- **审计：** 否（读）／可选  

### Identity.BindCredential

- **意图：** 绑定凭证哈希/句柄  
- **输入：** subject_id、credential_kind、secret_handle  
- **输出：** credential_id  
- **约束：** 不接受也不返回明文长期密钥  
- **审计：** 是  

### Identity.ValidateCredential

- **意图：** 验证凭证 active、未过期且绑定当前租户与主体
- **输出：** 不含 secret 的 credential view
- **错误：** `IDENTITY_CREDENTIAL_INVALID` / `IDENTITY_CREDENTIAL_REVOKED`

### Identity.RevokeCredential

- **意图：** 撤销凭证并阻止后续 Session 创建
- **输入：** credential_id、reason
- **约束：** 不级联撤销既有 Session
- **审计：** 是

### Identity.GrantPlatformGovernor

- **意图：** 创建平台 Identity Governor 持久化授权
- **约束：** 首条仅由 bootstrap UUID 授予；之后仅 active Governor 可授予
- **输出：** governor_grant_id
- **审计：** 是

### Identity.RevokePlatformGovernor

- **意图：** 撤销 Governor 并保留历史
- **约束：** 禁止撤销最后一个 active Governor
- **审计：** 是

### Identity.CreateSession

- **意图：** 建立会话边界  
- **输入：** credential_id、ttl_seconds  
- **输出：** session_id、expires_at  
- **约束：** Credential 必须有效并绑定当前 tenant/subject；拒绝裸 `auth_factors_ok` 布尔信任
- **审计：** 是  

### Identity.RevokeSession

- **意图：** 撤销会话  
- **输入：** session_id、reason  
- **输出：** ok  
- **审计：** 是  

### Identity.ValidateSession

- **意图：** 验证会话仍属于当前租户与主体且未过期/撤销
- **输入：** execution context、session_id
- **输出：** subject_id、tenant_id、expires_at
- **错误：** `IDENTITY_SESSION_NOT_FOUND`、`IDENTITY_SESSION_EXPIRED`、`IDENTITY_SESSION_REVOKED`
- **约束：** 跨租户或主体不匹配按 not found 处理；Runtime 对失败统一映射 `CTX_INVALID`
- **审计：** Foundation 读校验不逐次写审计

### Identity.AssignAIToTenant

- **意图：** AI 派驻租户  
- **输入：** ai_subject_id、tenant_id、management_policy  
- **输出：** assignment_id  
- **约束：** 派驻后租户可管理，但不可越权；AI 已有 active assignment 时失败关闭  
- **审计：** 是  

### Identity.ReassignAI

- **意图：** 改派/继承  
- **输入：** ai_subject_id、to_tenant_id（archive 可省略）、mode(`reassign`|`inherit`|`archive`)  
- **输出：** assignment_id  
- **约束：** reassign/inherit 要求恰好一个当前 active assignment；inherit 仅保存 predecessor 谱系，不复制权限、知识、记忆或会话；archive 不创建目标 assignment
- **权限：** 跨租户改派要求 `platform_scope` 且调用主体属于 Platform Identity Governor
- **L2：** application/API 层必须使用 Identity-Organization Coordinator，原子结束旧租户 active memberships
- **审计：** 是  

---

## 关联文档

- [KERNEL_INTERFACES.md](KERNEL_INTERFACES.md)
- [IDENTITY_STATE_MACHINES.md](IDENTITY_STATE_MACHINES.md)
- [../api/identity.openapi.yaml](../api/identity.openapi.yaml)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [../constitution/BOOK03.md](../constitution/BOOK03.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
