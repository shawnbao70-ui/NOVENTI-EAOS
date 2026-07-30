# Kernel 接口定义大纲

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** IF-KERNEL-OUTLINE  
**阶段：** Interfaces（PHX-001 后 / PHX-004 前）  
**版本：** 0.1  
**状态：** 大纲（非实现）

---

## 标题

EAOS Kernel 接口定义大纲

## 目的

在实现之前定义 Kernel 公共接口边界、上下文契约与域接口清单，确保 PHX-004+ 不突破宪法与蓝图。

## 范围

**范围内：** 接口名称意图、输入/输出概念、错误与审计要求、版本策略。  
**范围外：** Python/FastAPI 代码、数据库表、具体序列化格式定稿（后续 ADR）。

## 当前状态

**大纲已发布** — 可供 PHX-004 细化。

## 未来扩展

每域独立 Interface Spec；OpenAPI/IDL 产物位置；兼容性测试清单。

---

## 1. 全局执行上下文（所有 Kernel 调用必携）

| 字段 | 必填 | 说明 |
|------|------|------|
| `tenant_id` | 是 | 租户边界 |
| `subject_id` | 是 | 人类或 AI 主体 |
| `subject_type` | 是 | `human` / `ai` / `service` |
| `correlation_id` | 是 | 全链路关联 |
| `locale` | 否 | 语言区域 |
| `request_time` | 是 | UTC |

**规则：** 缺少租户或主体上下文的调用必须失败关闭。

---

## 2. 公共结果契约（概念）

| 字段 | 说明 |
|------|------|
| `ok` | 是否成功 |
| `data` | 成功载荷 |
| `error.code` | 稳定错误码 |
| `error.message` | 可读说明 |
| `audit_id` | 若产生副作用则必有 |

---

## 3. Identity Kernel 接口大纲

| 接口 | 意图 |
|------|------|
| `Identity.RegisterSubject` | 注册人类/服务/设备主体 |
| `Identity.RegisterAIEmployee` | 注册 AI 员工身份（永久 ID） |
| `Identity.ResolveSubject` | 解析主体 |
| `Identity.BindCredential` | 绑定凭证（不回传密钥） |
| `Identity.CreateSession` | 建立会话边界 |
| `Identity.RevokeSession` | 撤销会话 |
| `Identity.AssignAIToTenant` | AI 派驻租户 |
| `Identity.ReassignAI` | AI 改派/继承 |

**约束：** 身份全球唯一；禁止重复身份。

---

## 4. Organization Kernel 接口大纲

| 接口 | 意图 |
|------|------|
| `Org.CreateTenant` | 创建租户 |
| `Org.GetTenant` | 读取租户 |
| `Org.SuspendTenant / ReactivateTenant` | 平台治理租户状态 |
| `Org.GetEnterprise / ListEnterprises` | Tenant 内法人/组织主体 |
| `Org.UpsertUnit` | 组织单元 |
| `Org.GetUnitTree` | 查询同 Enterprise 无环层级 |
| `Org.AddMembership` | 成员关系 |
| `Org.RemoveMembership` | 移除成员 |
| `Org.ListMembership` | 查询成员 |
| `Org.TransferMembershipUnit` | 同 Enterprise 单元转移 |

**约束：** Tenant 是隔离边界，Enterprise 是边界内主体；跨租户关系默认禁止；更新必须使用 expected_version；角色标签不授予权限。

---

## 5. Permission Kernel 接口大纲

| 接口 | 意图 |
|------|------|
| `Permission.Grant` | 授予 |
| `Permission.Revoke` | 撤销 |
| `Permission.Evaluate` | 统一求值（allow/deny + 理由码） |
| `Permission.Explain` | 解释决策（审计/调试） |
| `Permission.ListEffective` | 有效权限集 |

**约束：** 权限统一计算；决策可审计；包内不得私建平行授权真相源。

---

## 6. Workflow Kernel 接口大纲

| 接口 | 意图 |
|------|------|
| `Workflow.Start` | 启动流程实例 |
| `Workflow.Signal` | 信号/推进 |
| `Workflow.Approve` | 审批通过 |
| `Workflow.Reject` | 审批拒绝 |
| `Workflow.Escalate` | 升级 |
| `Workflow.GetInstance` | 查询实例 |
| `Workflow.Cancel` | 取消 |

**约束：** 业务模块调用内核，不平行实现审批引擎。

---

## 7. Knowledge Kernel 接口大纲

| 接口 | 意图 |
|------|------|
| `Knowledge.UpsertEntity` | 规范实体写入 |
| `Knowledge.Link` | 建立关系 |
| `Knowledge.Query` | 受权查询 |
| `Knowledge.Search` | 语义/关键词检索 |
| `Knowledge.GetProvenance` | 出处 |
| `Knowledge.Share` | 受权共享 |

**约束：** 知识仅通过授权共享；查询必带租户与权限求值。

---

## 8. Event / Message 接口大纲

| 接口 | 意图 |
|------|------|
| `Event.Publish` | 发布不可变事件 |
| `Event.Subscribe` | 注册订阅（声明式） |
| `Event.Replay` | 受控回放（需授权+审计） |
| `Message.Send` | 异步消息 |
| `Message.GetDeliveryStatus` | 送达状态 |

**约束：** 事件不可修改；重放必须审计。

---

## 9. AI Runtime 接口大纲（与 Runtime 协同）

| 接口 | 意图 |
|------|------|
| `AI.CreateAgentRun` | 创建一次受控运行 |
| `AI.InvokeTool` | 工具调用（经权限） |
| `AI.RequestApproval` | 请求人工批准 |
| `AI.CommitAction` | 在批准后提交副作用 |
| `AI.ReadMemory` / `AI.WriteMemory` | 记忆读写 |
| `AI.AccessKnowledge` | 受权知识访问 |

**约束：** 所有 AI 必须经 AI Runtime；高影响动作默认人工批准。

---

## 10. 版本与兼容

1. 接口以 `major.minor` 版本化。  
2. 破坏性变更递增 major，并需 ADR。  
3. 弃用期不少于一个发布周期（细则后续 ADR）。  

---

## 11. PHX-004 进入门槛（验收）

- [x] BOOK00 / BOOK01 / BOOK19 生效基线已存在  
- [x] BOOK00–BOOK23 EAOS Charter v2.1 规范正文已生效
- [x] 本大纲已发布  
- [x] Identity / Permission 细化规格已发布  
- [x] ADR（租户隔离、事件信封、AI 审批）已接受  
- [x] 开发标准 PHX-003 已就绪  
- [x] **仍无**业务包实现抢跑  
- [x] Kernel 数据模型草案  
- [x] 契约测试计划  
- [x] Organization / Workflow 接口细化  
- [x] Kernel Foundation 内存垂直切片
- [x] Repository / AuditLog / Unit of Work 持久化端口

## 关联文档

- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [../blueprint/KERNEL_BLUEPRINT.md](../blueprint/KERNEL_BLUEPRINT.md)
- [../blueprint/EVENT_BLUEPRINT.md](../blueprint/EVENT_BLUEPRINT.md)
- [../blueprint/AI_BLUEPRINT.md](../blueprint/AI_BLUEPRINT.md)
- [EAOS_ARCHITECTURE.md](EAOS_ARCHITECTURE.md)
- [PERSISTENCE_PORTS.md](PERSISTENCE_PORTS.md)
- [../standards/API_STANDARD.md](../standards/API_STANDARD.md)
- [../project/PROJECT_STATUS.md](../project/PROJECT_STATUS.md)
