# ADR-0320 — CRM Customer + Contact Product Boundary

**状态：** Accepted（design boundary only；coding authorization = None）— Phase G Reaffirm 2026-07-26  
**日期：** 2026-07-24（Reaffirm 2026-07-26）  
**里程碑：** 设计表面未分配；C1 见独立 Coding Auth PHX-G294（Affirmed）  
**归属：** Business Package / CRM（非 Kernel）  
**授权源：** [Approved Decision Summary](../project/CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)  
**历史证据：** [Retired Phase G Review Pack](../project/CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md)（非活跃审批入口）

## 背景

ADR-0309 / PHX-G290 已接受 Legacy CRM 知识抽取，但知识被接受只表示它可作为产品设计输入。它不等于本 Product Gate 已接受，也不授予实现 Customer / Contact CRUD、API、SQL、服务或迁移的权限。

首个 CRM Product Gate 只需固定最小业务边界：商业客户主体 Customer，以及隶属于 Customer 的联系人 Contact。该边界必须消费现有 Tenant、Identity、Permission、Audit/Event 等平台能力，不得把 CRM 业务塞入或复制到 Kernel，也不得继承 Legacy 的模块、表、路由、角色字符串或级联删除架构。

## 决策

### 1. 产品范围

- **Customer**：租户内的商业客户/账户主数据，承载稳定业务身份、展示名称、生命周期状态、分群和责任归属引用。
- **Contact**：Customer 下的自然人联系人及经最小化处理的沟通渠道；Contact 不自动成为 Identity Subject、Organization Membership 或 Permission Principal。
- Customer 不是 Organization Kernel 的 Tenant、Enterprise、Org Unit 或 Membership；不得通过 `Org.*` 命令创建或维护 CRM Customer。
- Legacy knowledge 只证明 Customer 行上存在联系人字段，并未证明独立 Contact 实体；Product Owner 已接受把 Contact 设计为可独立识别的 Customer 子实体，仍不得把它表述为 Legacy 已有事实。
- Customer 与 Contact 的关系属于 CRM Package。一个 Customer 可有多个 Contact；主联系人是受约束关系，不是 Customer 表中的重复字段模型。
- Customer/Contact 使用 Package-owned、tenant-scoped 的不透明业务标识；Legacy row ID、名称、邮箱、电话及 Identity Subject ID 均不得充当产品身份。
- Customer owner 只表达业务责任引用；territory 因无 Legacy 证据而明确 Defer。二者都不直接产生数据可见性、Membership、Role 或 Permission Grant，也不等于 ADR-0313 要求 Permission 独立求值的“对象所有权”维度。
- 生命周期采用可保留历史的状态变更；硬删除、跨域级联删除和由 CRM 直接改写下游业务对象不在边界内。
- Legacy hard delete 缺少 open-AR/关联对象 guard；该缺口只证明默认硬删除不可继承，不把 Finance 校验纳入本 Gate。
- Customer 360、搜索、重复识别与导入只可作为后续独立 Gate 候选；本 Gate 不把聚合读模型或自动合并定义为已接受能力。

### 2. Package ownership

- 产品能力归属 `noventi.crm` Business Package，声明制品位于 `packages/`；不属于 Core Kernel。
- CRM 只消费可信 ExecutionContext、Organization Tenant scope、Permission Evaluate、审计能力与 Event Outbox 契约。
- CRM 不复制 Identity、Organization、Permission、Workflow、Event 或审计真相源，不新增 Kernel 业务实体或 Kernel 专用 CRM 分支。
- Package action 的资源类型保留为 `pkg.crm.customer` 与 `pkg.crm.contact`；动作词和写契约仍须后续 Gate 明确接受。

### 3. 租户与数据边界

- 每个 Customer、Contact、关系、查询投影及未来事件都必须绑定可信上下文中的单一 `tenant_id`。
- Customer/Contact 业务数据归租户侧企业主权主体所有；平台与 CRM Package 只提供受治理能力，不取得经营或数据所有权。
- API/命令不得信任客户端提供的 `tenant_id`、caller subject、session 或 platform scope。
- 跨租户读取、关联、搜索、更新、合并及事件投递默认拒绝；未解析 Tenant 或 Customer 归属时 fail closed。
- Customer 业务编号、重复检测键及 Contact 渠道唯一性策略只能在租户范围内定义；本 ADR 不提前固定具体数据库约束。
- Contact 渠道属于个人数据：后续设计必须给出数据最小化、字段级可见性、保留/删除、导出、驻留/跨境和审计策略，并保留按法域配置的数据主体权利与合规例外决策位。

### 4. 权限、审计与事件

- 所有读取和未来写入均通过 Permission Kernel 单一求值入口；CRM 不使用 Legacy `Admin/Manager` 绕过、页面角色字符串或 owner 字段作为授权真相。
- 候选权限边界为 Customer/Contact 的 `read`、`create`、`update`、`archive` 与关系维护；这些名称仅用于 Gate 评审，不构成可编码或可注册授权。
- ADR-0313 的主体、动作、对象所有权、租户、资源状态、高影响意图、幂等/命令身份与审计是未来命令面的最低评审维度；菜单/Surface 可见性、owner 等值、GET 变异和 Admin 角色短路均不得替代求值。
- `manifest.proposed.json` 中的 `read` / `required_permissions` 仅是 discovery 命名草案，不注册 Permission、不预置 Grant、不接受 read API；候选写动作刻意不出现在 manifest。
- 责任归属、主联系人切换、状态变更、个人渠道变更、归档及拒绝结果必须可审计；审计需记录 actor、tenant、resource、action、decision、reason、correlation 与时间，不记录不必要的敏感值。
- 未来业务写与领域事件必须采用同事务 Outbox；候选目录为 `crm.customer.created`、`crm.customer.updated`、`crm.customer.archived`、`crm.contact.created`、`crm.contact.updated`、`crm.contact.archived`、`crm.contact.primary_changed`。事件名称、schema 和 payload 在独立契约接受前均为 Proposed，当前不得发布。
- 未来 producer 标识与受信域 Outbox 发射入口须单独接受；Gate Accept 不授权使用 HTTP Event.Publish。
- Permission allow 不替代高影响动作的 Workflow/人工批准；哪些动作属于高影响需后续 Gate 决定。

### 5. Gate 语义

以下状态严格分离：

1. **Accepted knowledge**：ADR-0309 等知识包可作为证据输入，不代表产品模型正确或完整。
2. **Gate Accept**：架构负责人/产品负责人明确接受 Product Gate 的范围、所有权和契约，且 Acceptance 条件有证据。
3. **可编码**：另有明确实现授权、里程碑和交付范围；即使 Gate Accept，也不会自动产生编码授权。

本 ADR 的设计边界已由 Product Owner 接受。该接受不产生编码授权；在另有明确编码授权与实现里程碑之前，不允许实现业务 CRUD、SQL/API/服务、Alembic、runtime manifest 或写路径。

## 后果

- 首个 CRM 切片保持 Customer + Contact 最小闭环，并作为 Business Package 演进。
- 现有 Kernel 继续只提供横切平台能力，不承载 CRM 业务模型。
- Legacy 抽取中的状态、字段、权限缺口和硬级联只作为问题证据，不成为默认设计。
- 后续实现若获授权，仍需分别接受数据模型、命令/API、权限矩阵、审计、事件 schema、迁移与验收计划。

## 非目标

- Opportunity、Requirement、Quotation/Quote、Quote Convert、Sales Order 或任何销售转化流程
- 财税、应收、收款、信用额度、余额计算、发票、会计或 PSP
- Brain execute、Twin authorize、Customer 360 AI、自动决策、自动授权或 Cap→grant
- Legacy 架构、源码、SQL、表结构、路由、菜单、角色绕过或级联删除的继承/复制
- Customer / Contact CRUD、API、服务、Repository、数据库表、Alembic、UI 或业务写路径
- Follow-up/客户互动记录、keyword 搜索投影、导入、去重/合并、Customer360/Object360/Graph 联系节点
- 联系人岗位/部门、采购/技术/财务/决策人角色、决策权、备用/升级联络策略及基于邮件域/电话/备注的自动推断；optional primary-contact 关系边界已接受，但唯一性、跨 Customer 移动与切换规则仍为独立设计待决项
- Quote/SO/NDE 的 Contact ID 或联系人快照、Zero Duplicate party 复用与文档收件人映射
- Legacy 双轨状态/等级词汇、Dashboard 统计桶与 mining `Active/Inactive` 的继承
- Proposed 阶段写入 DAL Usage、PROJECT_STATUS、Eng tip、CHANGELOG、Release Manifest、运行包版本或迁移基线，或以这些台账暗示 Gate 已接受
- 自行创建实现里程碑、把 Proposed manifest 注册/发布/安装，或把本 ADR解释为实现授权

## 关联

- [ADR-0321 — Phoenix Gate Framework](ADR-0321-phoenix-gate-framework.md)
- [ADR-0029 — Business Package Platform 边界](ADR-0029-business-package-platform.md)
- [ADR-0309 — Legacy Knowledge Extract CRM + Sales Packs](ADR-0309-legacy-knowledge-extract-crm-sales.md)
- [ADR-0313 — Command/Authz Rewrite Boundary](ADR-0313-command-authz-rewrite-boundary.md)
- [BOOK02 — 企业宪法](../constitution/BOOK02.md)
- [BOOK06 — 合规宪法](../constitution/BOOK06.md)
- [BOOK11 — 行业宪法](../constitution/BOOK11.md)
- [BOOK19 — Kernel 总宪章](../constitution/BOOK19.md)
- [BOOK23 — Smart Terminal 宪法](../constitution/BOOK23.md)
- [业务包蓝图](../blueprint/PACKAGE_BLUEPRINT.md)
- [Organization Interface](../architecture/ORGANIZATION_INTERFACE.md)
- [Permission Interface](../architecture/PERMISSION_INTERFACE.md)
- [Event Interface](../architecture/EVENT_INTERFACE.md)
- [Customer Legacy Knowledge](../knowledge/legacy-extract/crm/customer.md)
- [Contacts & Roles Legacy Knowledge](../knowledge/legacy-extract/customer-deepen/contacts_roles.md)
- [CRM Customer + Contact Product Architecture Gate](../project/CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md)
- [CRM Customer + Contact Product Gate Acceptance](../project/CRM_CUSTOMER_CONTACT_ACCEPTANCE.md)
- [Proposed package manifest (non-runtime)](../../packages/crm/manifest.proposed.json)
- [Authorization Summary](../project/CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)
- [Retired Phase G Review Pack（historical evidence only）](../project/CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md)
- [Coding Authorization Summary（C1 / PHX-G294 Affirmed）](../project/CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)
