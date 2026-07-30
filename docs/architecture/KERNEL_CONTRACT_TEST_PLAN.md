# Kernel 契约测试计划

**文档 ID：** QA-KERNEL-CONTRACT-001  
**版本：** 0.1  
**阶段：** PHX-004 Foundation 验收  
**状态：** 已自动化执行  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Kernel 契约测试计划

## 目的

在实现 Kernel 之前定义必须通过的契约级验证，防止实现偏离宪法、ADR 与接口规格。

## 范围

契约、不变式与负面用例，以及对应自动化执行状态。

## 当前状态

**Foundation 自动化与真实 PostgreSQL 验收已通过**

## 未来扩展

映射到 CI 门禁与真实 PostgreSQL 必跑环境。

---

## 1. 测试层级

| 层级 | 目标 |
|------|------|
| L0 不变式 | 租户隔离、默认拒绝、审计必有 |
| L1 接口契约 | 各 Kernel 接口输入输出与错误码 |
| L2 集成契约 | Identity↔Org↔Permission↔Workflow |
| L3 事件契约 | 信封完整性、幂等、重放授权 |
| L4 AI 闸门 | 未批准不可 CommitAction |

---

## 2. 强制负面用例（必须失败）

| ID | 场景 | 期望 |
|----|------|------|
| N-01 | 无 tenant_id 执行写操作 | deny / fail closed |
| N-02 | 跨租户读取/写入 | deny |
| N-03 | 跨租户 AddMembership | `ORG_CROSS_TENANT_FORBIDDEN` |
| N-04 | 无权限 Evaluate → 业务写 | deny |
| N-05 | AI CommitAction 无批准 | deny |
| N-06 | 事件缺少 correlation_id/tenant_id | 拒绝入队 |
| N-07 | 包内“本地授权”绕过 Permission | 架构违规（评审失败） |
| N-08 | 路由内业务真相源 | 标准违规（评审失败） |

---

## 3. Identity 契约用例

| ID | 场景 | 期望 |
|----|------|------|
| I-01 | RegisterSubject 成功 | 返回唯一 subject_id |
| I-02 | 重复外部引用 | `IDENTITY_DUPLICATE` |
| I-03 | RegisterAIEmployee | 永久 ID，可归档不可复用 |
| I-04 | BindCredential 不回传明文 | 响应无 secret |
| I-05 | Create/Revoke Session | 会话边界生效 |
| I-06 | Assign/Reassign AI | 审计完整；知识不随人走丢失 |
| I-07 | ValidateSession 有效会话 | 返回绑定主体、租户与过期时间 |
| I-08 | 过期/撤销/跨租户/主体不匹配 | 具体 SESSION 错误且无副作用 |

---

## 4. Organization 契约用例

| ID | 场景 | 期望 |
|----|------|------|
| O-01 | CreateTenant | 租户创建 |
| O-02 | UpsertUnit 父子同租户 | 成功 |
| O-03 | UpsertUnit 父跨租户 | 失败 |
| O-04 | Add/Remove/List Membership | 状态正确 |
| O-05 | membership_role_label 不授予权限 | Evaluate 仍默认 deny |

---

## 5. Permission 契约用例

| ID | 场景 | 期望 |
|----|------|------|
| P-01 | 无 grant 时 Evaluate | deny |
| P-02 | Grant 后 Evaluate | allow + policy_version |
| P-03 | Revoke 后 Evaluate | deny |
| P-04 | Explain 返回原因码 | 无密钥泄漏 |
| P-05 | AI invoke_tool 无工具权限 | deny |
| P-06 | 决策审计记录存在 | permission_decisions 有条目（实现后） |

---

## 6. Workflow / AI 审批契约用例

| ID | 场景 | 期望 |
|----|------|------|
| W-01 | Start 实例 | instance 可查询 |
| W-02 | Approve/Reject 留痕 | 审计 + 状态迁移 |
| W-03 | Cancel 受控 | 无权限失败 |
| W-04 | AI 申请批准 → 人工批准 → Commit | 仅最后一步允许副作用 |
| W-05 | AI 申请批准 → 拒绝 | Commit 失败 |

---

## 7. 事件契约用例

| ID | 场景 | 期望 |
|----|------|------|
| E-01 | Publish 完整信封 | 成功 |
| E-02 | 缺字段信封 | 拒绝 |
| E-03 | Replay 无授权 | 拒绝 |
| E-04 | Replay 有授权 | 审计 + 订阅幂等 |

**Foundation 执行状态：** E-01～E-04 已自动化通过；另覆盖 JSON 安全 payload、读取权限、跨租户投递隔离与失败后重放。

---

## 8. 完成定义（Definition of Done）

某 Kernel 域实现“完成”当且仅当：

1. 对应接口规格已实现  
2. 本计划中该域用例全部自动化通过  
3. 负面用例 N-01～N-06 相关项通过  
4. 文档与 CHANGELOG 已更新  
5. 无遗留仓库依赖  

## 9. PHX-004 Foundation 执行结果

- L0/L1：内存与 SQLAlchemy 事务契约已自动化
- L2：Organization ↔ Permission 角色/授权边界已在内存和事务路径通过
- L2：Identity ↔ Organization 主体资格与 AI 改派 membership 原子收敛已通过 SQLite/PostgreSQL
- L3：Event 发布、订阅、读取、重放、失败尝试持久化已通过
- L4：W-04/W-05 及批准主体/动作/资源绑定已在内存和事务路径通过
- 当前：`123 passed`（包含真实 PostgreSQL）
- 最终状态与阻塞见 [../project/PHX-004_ACCEPTANCE.md](../project/PHX-004_ACCEPTANCE.md)

## 关联文档

- [KERNEL_DATA_MODEL.md](KERNEL_DATA_MODEL.md)
- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [ORGANIZATION_INTERFACE.md](ORGANIZATION_INTERFACE.md)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [WORKFLOW_INTERFACE.md](WORKFLOW_INTERFACE.md)
- [EVENT_INTERFACE.md](EVENT_INTERFACE.md)
- [../decisions/ADR-0006-event-envelope.md](../decisions/ADR-0006-event-envelope.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
- [../decisions/ADR-0008-ai-human-approval.md](../decisions/ADR-0008-ai-human-approval.md)
