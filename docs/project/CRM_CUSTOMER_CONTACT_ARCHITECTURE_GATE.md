# CRM Customer + Contact Product Architecture Gate

**日期：** 2026-07-24  
**状态：** Gate Accepted（design boundary only；coding authorization = None）— Phase G **Reaffirm** 2026-07-26  
**规范源：** ADR-0320  
**里程碑：** 设计表面未分配；C1 实现里程碑见独立 [Coding Authorization](CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)（PHX-G294 Affirmed）  
**Gate 类型：** Product / Architecture（design-only）  
**授权源：** [Approved Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)  
**生成物：** [Acceptance](CRM_CUSTOMER_CONTACT_ACCEPTANCE.md)  
**历史证据：** [Retired Phase G Review Pack](CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md)（非活跃审批入口）

## Gate 目的

本文件由系统根据 Product Owner 批准的 Authorization Summary 生成，固定 Customer + Contact 的 design-only Product Gate。它不接受实现，不授权 CRUD。

## In

- 租户内商业客户主体 Customer 的语义、身份与生命周期边界
- Customer 下 Contact 的语义、个人数据边界与主联系人关系
- `noventi.crm` Business Package ownership；资源类型候选 `pkg.crm.customer`、`pkg.crm.contact`
- 对 Tenant、Permission、Audit、Event Outbox 的消费契约
- 未来权限、审计和领域事件所需的最小评审点
- Accepted knowledge、Gate Accept、可编码三种状态的分离

## Out

- Opportunity、Requirement、Quote/Quotation、Convert、Sales Order
- 财税、AR/AP、收款、信用、余额、发票、会计、PSP
- Brain execute、Twin authorize、AI Customer 360、自动授权、Cap→grant
- Follow-up/客户互动记录、keyword 搜索、导入、去重/合并、Customer360/Object360/Graph 联系节点
- 联系人岗位/部门、业务角色、决策权、备用/升级联络策略及自动推断；optional primary-contact 边界已接受，唯一性/移动/切换规则仍待独立设计
- Quote/SO/NDE 联系人引用或快照、Zero Duplicate party 与文档收件人映射
- Legacy 双轨状态/等级、Dashboard bucket 与 mining `Active/Inactive`
- Legacy 架构/源码/SQL/表/路由/菜单/角色模型继承
- SQL、API、服务、Repository、数据库模型、Alembic、UI、CRUD 与任何业务写路径
- Package 注册、发布、安装，或自行建立实现里程碑
- 通过 DAL Usage、PROJECT_STATUS、Eng tip、CHANGELOG、Release Manifest、运行包版本或 migration head 暗示实现授权

## Accepted architecture boundary

| Decision item | Accepted ruling |
|---|---|
| Aggregate boundary | Customer 是 CRM aggregate root；Contact 是 Customer 边界内、可独立识别的子实体，不是新的 Kernel domain |
| Organization boundary | Customer 不是 Tenant、Enterprise、Org Unit 或 Membership；CRM 不调用 `Org.*` 建模 Customer |
| Legacy contact shape | 单组 `contact_person/phone/whatsapp/email` 仅为知识证据；不得固定为 EAOS 产品存储形态，也不得被虚构为多联系人已存在 |
| Identity | Customer ID 与 Contact ID 是租户内不透明业务标识；Legacy row ID、邮箱、电话和 Identity Subject ID 均不是产品身份 |
| Relationship | Contact 必须属于一个同租户 Customer；跨 Customer 移动、合并和主联系人切换在规则接受前保持关闭 |
| Responsibility | Customer owner 是业务责任引用；territory 因无 Legacy 证据而 Defer；二者均不等于 Permission 的对象所有权求值 |
| Lifecycle | Customer relationship lifecycle 与 Contact reachability/lifecycle 分离；状态词汇须后续接受，不继承 Legacy 中英双轨 |
| Deletion | 默认采用归档/失效和保留策略；硬删除及跨域级联不是首个产品能力 |
| Surface | Proposed manifest 只描述可发现的 read intent；不承诺查询、DTO、路由、存储或 Terminal 投影 |
| Events | ADR 中的事件名只是待评审目录；manifest 保持空 `declared_events`，直到 producer、schema、payload 与受信 Outbox 发射入口单独接受 |

## Architecture invariants

1. CRM 是 Package 业务域，不是 Kernel；不得向 Kernel 塞 Customer/Contact 实体或复制平台真相源。
2. Customer 与 Contact 均属于且只属于一个可信 Tenant；缺失或冲突的 Tenant context 一律 fail closed。
3. Contact 不是 Identity Subject；业务 owner 引用也不直接产生 Membership、Role 或 Permission Grant。
4. Permission Kernel 是授权唯一入口；默认拒绝，禁止 Legacy 角色字符串和 owner 等值绕过。
5. 所有未来写意图与结果必须可审计；敏感 Contact 数据遵循最小披露。
6. 未来领域事件必须与业务写同事务入 Outbox；本 Gate 不批准事件 schema 或发布路径。
7. Customer 归档不得硬级联删除 Contact 或下游跨域记录；保留、匿名化与法务删除需另行设计。
8. Package resolve、Permission allow、Workflow approval 与业务执行是不同阶段，任何一项都不能替代其他项。

## Constitutional alignment

| Source | Gate interpretation |
|---|---|
| BOOK02 企业主权 | Customer 资源与 Contact 数据归租户侧企业所有；“归企业所有”不表示 Customer 是 Organization Enterprise 实体 |
| BOOK06 合规 | Contact 必须保留数据主体权利、法务删除/披露例外、驻留与跨境配置的决策位；本 Gate 不自行裁定法域规则 |
| BOOK11 行业/包边界 | CRM 以 Business Package 扩展，声明权限与合规影响，不把 Legacy ERP 架构上升为 Kernel |
| BOOK19 Kernel 基本法 | 多租户隔离与审计不可关闭；无身份/权限则无副作用；授权/租户错误 fail closed |
| BOOK23 Terminal/Package surfaces | manifest 仅为声明式 surface/action 草案；Terminal、Surface 或用户输入不得覆盖安全上下文或成为业务真相 |
| Package Blueprint | 业务知识可来自 Legacy，产品架构不得来自 Legacy；Package 消费平台能力且不分叉 Kernel |

## Product boundary

### Customer

- 表示租户内的商业客户/账户，而非登录身份、Organization Tenant/Enterprise/Org Unit/Membership 或财务科目。
- 最小语义候选：稳定 ID、租户内业务编号、名称、生命周期状态、分群、责任主体引用和版本。
- “余额、信用、报价数、订单数、赢率”均为跨域投影或策略结果，不属于 Customer 核心写模型。

### Contact

- 表示 Customer 下的自然人联系人及最小必要沟通渠道。
- Accepted Legacy knowledge 仅观察到 Customer 行上的联系人字段，没有独立 Contact ID；本 Gate 接受独立 Contact 子实体作为 Product 设计，仍不能由知识接受状态直接推出。
- 接受的最小边界：稳定 ID、Customer 关系、姓名/称谓、渠道、optional primary-contact 与状态；用途词汇和历史细节 Defer。
- 渠道可见性、同意/合法依据、保留、导出与删除必须在实现 Gate 前明确。
- 主联系人唯一性、Contact 跨 Customer 移动及重复合并仍为待决事项，不得由实现自行猜测。

## Cross-cutting contract

| Concern | Accepted boundary | Governance consequence |
|---|---|---|
| Ownership | `noventi.crm` Business Package；非 Kernel | Package/Kernel 边界评审 |
| Tenant | trusted ExecutionContext；所有资源同租户 | 跨租户拒绝与上下文来源设计 |
| Permission | Kernel Evaluate；覆盖 ADR-0313 的主体、动作、对象所有权、租户、状态、高影响、幂等/命令身份与审计 | 动作矩阵、scope level、ScopeResolver、deny 行为 |
| Audit | 写意图、允许/拒绝、结果、关联 ID；敏感值最小化 | 审计字段与读取权限 |
| Event | 同事务 Outbox；schema/version 后置接受 | 事件目录、payload 最小化、消费者边界 |
| Privacy | Contact 字段级可见性、保留/删除/导出；PII read 可能需遮蔽/审计 | 数据分类、read 审计与隐私决策 |
| Concurrency | 状态/关系变更需版本条件 | 冲突语义与幂等策略 |

## Proposed package contract

- 可选声明草案：`packages/crm/manifest.proposed.json`
- 草案只声明只读 discovery surfaces/actions，不包含 create/update/archive/delete/merge/convert 等写动作。
- 草案不可注册、发布、安装或被 runtime 发现；它不是 Package Platform manifest 交付。
- 仓库快照（2026-07-24）中 demo 只显式读取 `packages/sample_ops/manifest.json` 与 `packages/sample_product/manifest.json`，未发现通用 package JSON glob；`.proposed.json` 文件名是刻意的非运行时隔离，不是安全机制替代品。
- 草案中的 `permission_action: read` / `required_permissions` 只是评审用命名，不注册 Permission、不预置 Grant、不接受 read API；`high_impact: false` 也不表示 Contact PII 低敏感或免审计。
- `version: 0.1.0` 只是封闭 schema 所需的草案值，不表达发布、兼容性或生命周期承诺。
- `package_key` 保持 `noventi.crm`，resource type 保持 `pkg.crm.*`；action key 使用 `crm.*` namespace，避免未来租户内多包解析歧义。
- manifest 不声明或接受 `tenant_id`、subject、session、platform scope 或 execution context；安全上下文只能来自可信边界。
- 即使未来 ResolveAction 成功，也只表示“已安装 + 已声明 + Permission allow”的解析结果，不执行查询、变更或其他业务副作用。
- 只读 inspect 不声明领域事件；未来若需要访问审计，它与业务领域事件分开评审。
- 未来可执行 action、required permission 与事件 schema 必须在 Gate Accept 后另行评审。
- schema 校验只证明声明形状合法；重命名为 `manifest.json`、提交注册请求、发布或安装均需独立明确授权，Gate Accept 也不自动授权这些动作。

## Generated OD dispositions

| ID | Product Owner disposition |
|---|---|
| OD-01 | Accept proposed：单一 Customer lifecycle；archive 优先于 hard delete；具体状态词汇/restore guard 留作独立设计契约 |
| OD-02 | Amend：接受 opaque ID 与 tenant-scoped code/name 边界；分群/等级/来源/geography 与重复识别 Defer |
| OD-03 | Accept proposed：接受 Customer aggregate 内可独立识别 Contact 子实体与 optional primary-contact boundary；细化词汇 Defer |
| OD-04 | Defer out of gate：不接受渠道唯一性或联系人去重能力 |
| OD-05 | Defer out of gate：外联/外跳未获独立同意与合法依据前保持关闭 |
| OD-06 | Amend：owner 仅业务责任引用；territory Defer；不得短路 Permission |
| OD-07 | Amend：接受 resource-scoped、default-deny、fail-closed 边界；详细 action/scope/masking 矩阵为独立设计契约 |
| OD-08 | Amend：Contact PII 必须受 deny/mask/audit 治理；具体策略由后续控制契约接受 |
| OD-09 | Accept proposed：保留数据主体权利、驻留/跨境与法务例外责任路径；不在本 Gate 发明法域规则 |
| OD-10 | Defer out of gate：不接受 runtime event；manifest `declared_events` 保持空 |
| OD-11 | Defer out of gate：当前无业务写动作；高影响/Workflow 分类留给独立写能力 Gate |

## Knowledge traceability

| Knowledge evidence | Observed fact | Generated response | Gate status |
|---|---|---|---|
| C-R1 | Legacy owner 等值控制部分列表可见性 | owner 仅业务引用；Permission 独立求值 | Accepted invariant |
| C-R3 | customer code 有用户输入与时间生成双轨 | opaque ID + tenant-scoped code/name；详细编号策略 Defer | Accepted boundary / detail deferred |
| C-R9 / C-V5 | hard cascade 且无 open-AR guard | archive 优先；关联 guard Defer | Accepted principle / detail deferred |
| C-R11 | Tenant filter 覆盖不一致 | 所有资源/投影/事件强制同租户 | Accepted invariant |
| C-R12 | 仅部分写路径有审计 | 审计不可关闭；粒度/留存 Defer | Accepted principle / detail deferred |
| C-R14 | Follow-up append 且权限不一致 | Follow-up 明确 Out | Closed by scope |
| CT-R1 / CT-R3 | 单组 Contact 字段且覆盖无历史 | 独立 Contact 子实体 accepted；历史策略 Defer | Accepted boundary / detail deferred |
| CT-R11 / CT-R18 | 下游无 Contact ID/稳定快照 | 下游 Contact 引用与快照明确 Out | Closed by scope |
| CT-R13 / CT-R20 | Detail read/PII 访问治理不足 | default-deny + PII governance；具体 masking/audit Defer | Accepted principle / detail deferred |
| CT-R16 | 无角色证据 | 禁止自动推断决策人或角色 | Accepted invariant |

## Generated RC attestations

| ID | Reject if true | System attestation |
|---|---|---|
| RC-01 | 将 Accepted knowledge 当作产品模型已接受 | False — knowledge/design distinction preserved |
| RC-02 | Tenant/Permission fail-closed 缺失 | False — explicit invariants present |
| RC-03 | owner、角色、resolve 或 UI 被当作授权 | False — Permission remains sole decision source |
| RC-04 | Legacy owner filter 短路对象所有权 | False — explicitly forbidden |
| RC-05 | Contact privacy/retention 无责任路径 | False — control path retained; detailed contract deferred |
| RC-06 | 继承 Legacy ID、覆盖、GET 变异、Admin 绕过或硬级联 | False — explicitly forbidden |
| RC-07 | Gate 携带实现、Alembic、runtime manifest 或安装 | False — design artifacts only |
| RC-08 | 台账/version/migration 更新被用来暗示 Accept | False — no such promotion performed |
| RC-09 | Gate Accept 被写成运行或编码授权 | False — coding authorization remains None |

## Gate decision rules

- **Accepted knowledge**：相关知识 ADR 已接受，只能证明设计输入存在。
- **Gate Accept**：Product Owner 对 Authorization Summary 一次性明确 Approve 后，系统生成 OD dispositions、RC attestations、Approval record 与 signature。控制细节可明确 Defer，但不得静默留给实现猜测。
- **可编码**：在 Gate Accept 之后，另有明确实现授权与里程碑。Gate Accept 本身仍不授权编码。

允许的治理状态迁移：

```text
Proposed design
  └─[Product Owner explicitly approves Authorization Summary]
     → Gate Accepted (design boundary only)
        └─[separate explicit authorization + assigned milestone]
           → Coding authorized for that stated slice
```

不得跳过中间状态，不得由 Accepted knowledge、manifest schema 校验或链接完整触发自动迁移。Product Owner 的单次 Approve 只接受 Summary 中的设计边界与显式 Defer；系统生成完整文档后仍不产生编码授权。

## Generated artifact exit

- Authorization Summary、ADR-0320、Architecture Gate、Acceptance 与 proposed manifest 互相链接
- 范围、Package ownership、权限/审计/事件/租户与非目标均显式
- 状态为 Gate Accepted（design boundary only）
- 无 SQL/API/服务/CRUD/Alembic/Kernel 业务改动

本文件为 Product Owner Approve 后由系统生成的治理 artifact；Product Owner 无需手工编辑。其 design-only Accepted 状态不授予编码权限。

## Evidence and draft index

- [ADR-0320 — CRM Customer + Contact Product Boundary](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)
- [Acceptance (Gate Accepted, design-only)](CRM_CUSTOMER_CONTACT_ACCEPTANCE.md)
- [Proposed manifest](../../packages/crm/manifest.proposed.json)
- [Customer Legacy Knowledge](../knowledge/legacy-extract/crm/customer.md)
- [Contacts & Roles Legacy Knowledge](../knowledge/legacy-extract/customer-deepen/contacts_roles.md)
