# 联系人、角色与决策人（Contacts & Roles）— Legacy Knowledge

**Evidence strength:** Strong for one denormalized contact per customer; strong negative for multi-contact roles and decision maps  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 客户主记录直接保存一组 `contact_person / phone / whatsapp / email` 字段。Customer360 的 Contacts 标签只展示这组字段，未发现活动 `customer_contacts`/`contacts` 明细表、主联系人标志、岗位、采购角色、决策权、有效期或隐私同意模型。

Customer Graph 把 `contact` 列为可关联对象，但该词汇不等于联系人主数据；Customer360 运行时也只是把主表联系人文本用于摘要和搜索。供应商、GFIP 等模块里的联系人字段属于各自对象，不能自动并入客户联系人。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CT-R1 | 每个客户主记录只有一组联系人字段 | 无多联系人明细关系 |
| CT-R2 | 联系人姓名、电话、WhatsApp、邮箱可为空 | 服务端没有完整性校验 |
| CT-R3 | 更新客户会覆盖原联系人字段 | 不保留联系人历史或失效原因 |
| CT-R4 | Customer360 Contacts 标签展示主表字段 | 不是独立联系人列表 |
| CT-R5 | 客户搜索可按联系人、电话和 WhatsApp 模糊匹配 | 不按邮箱或角色搜索 |
| CT-R6 | WhatsApp 按保存值直接构造外部聊天链接 | 未观察到号码标准化或同意校验 |
| CT-R7 | `contact_person` 进入 Object360 标题摘要和搜索词 | 仍是客户字段，不是联系人对象 |
| CT-R8 | Customer Graph 的 `contact` 只是图类型目录 | 未找到由客户主表生成联系人节点的活动写入 |
| CT-R9 | 未区分决策人、采购人、技术人、财务人和收货人 | 所有角色语义只能落在自由文本之外，当前无字段 |
| CT-R10 | 未定义主联系人/备用联系人 | 单字段存在不等于经过主联系人确认 |
| CT-R11 | 报价、订单和收款不引用 contact ID | 单据只能通过客户间接取得联系人文本 |
| CT-R12 | 文档或门户中的收件人字段不形成客户联系人主档 | 跨模块文本不可反向推定 |
| CT-R13 | 客户详情路由未见 `Customers.view` gate | 联系信息存在对象级可见性风险 |
| CT-R14 | 客户负责人 `owner` 是内部归属 | 不等于客户侧联系人或决策人 |
| CT-R15 | 客户跟进记录保存内容和下步计划 | 不结构化记录“与谁沟通” |
| CT-R16 | EAOS 不得根据邮件域、电话号码或备注自动判定决策人 | 缺少授权与角色证据 |
| CT-R17 | V18 Zero Duplicate 从客户主表复用联系人、电话和邮箱到报价 party 预览 | 这是避免重复录入，不是联系人合并 |
| CT-R18 | NDE 文档联系人块从客户主表映射联系人、电话和邮箱 | 不包含联系人角色，也不冻结历史快照 |
| CT-R19 | 客户重复告警只按规范化公司名识别 | 不按联系人、电话或邮箱去重 |
| CT-R20 | 客户模块未观察到联系人字段脱敏、同意或访问审计 | 宪法隐私条款不等于运行实现 |

---

## 3. Process

### 3.1 当前联系人维护

1. 新建客户时可输入一组联系人姓名和通信字段。
2. 系统把字段直接保存到客户行。
3. Customer360 展示同一组字段。
4. 编辑客户时直接覆盖这些值。
5. 未观察到新增第二联系人、设主联系人、停用或合并流程。

### 3.2 当前业务使用

1. 客户列表搜索会匹配联系人姓名、电话或 WhatsApp。
2. Customer360 可从 WhatsApp 字段打开外部聊天。
3. Object360 运行时将联系人姓名作为对象摘要和搜索关键词。
4. Zero Duplicate 在报价界面复用当前客户 party 字段；NDE 打印也读取当前客户联系人。
5. 报价/订单仍只引用 customer ID，不冻结联系人快照。

### 3.3 缺失的角色流程

未观察到：新增联系人 → 去重 → 绑定岗位/部门 → 指定采购角色与决策权 → 记录偏好/同意 → 设主联系人 → 失效/离职 → 保留历史与单据快照。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CT-V1 | 联系人姓名必填 | Missing | 表单和服务允许空值 |
| CT-V2 | 邮箱格式合法 | Missing | 未见服务端验证 |
| CT-V3 | 电话/WhatsApp 应规范化国家码 | Missing | 原样保存和拼接 |
| CT-V4 | 同一客户联系人邮箱应唯一 | Not modeled | 无联系人明细 |
| CT-V5 | 全局重复联系人应提示 | Missing | 无去重服务 |
| CT-V6 | 只能有一个当前主联系人 | Not modeled | 无 `is_primary` |
| CT-V7 | 角色必须来自受控词汇 | Not modeled | 无 role 字段 |
| CT-V8 | 决策权必须有来源和确认时间 | Not modeled | 无 decision maker 模型 |
| CT-V9 | 离职/停用联系人不得继续用于沟通 | Missing | 无状态/有效期 |
| CT-V10 | 营销与 WhatsApp 联系需记录同意 | Missing | 无 consent 字段 |
| CT-V11 | 客户详情联系人需对象级查看权限 | Weak / missing | 详情入口未见 view gate |
| CT-V12 | 内部 owner 不得映射为客户联系人 | Semantic guard | 数据主体不同 |
| CT-V13 | 重复联系人应按邮箱/电话检测 | Missing | 现有重复告警只看 company_name |
| CT-V14 | 联系字段应按角色和隐私级别脱敏 | Missing | 未见字段级控制 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `customers.contact_person` | 客户行上的单一联系人姓名文本 |
| `customers.phone` | 客户主电话文本 |
| `customers.whatsapp` | WhatsApp 号码/标识文本 |
| `customers.email` | 客户主邮箱文本 |
| `customers.owner` | 内部客户负责人 |
| `followups.content` | 非结构化沟通内容 |
| `followups.next_plan` | 非结构化下一步 |
| Customer360 Contacts tab | 对客户行四个通信字段的展示 |
| Object360 `summary` | 使用 contact_person 的对象摘要 |
| Object360 search terms | 包含联系人姓名的派生搜索词 |
| Customer Graph `contact` | 通用图谱对象类型 |
| `has_contact` | 图谱关系词汇，非活动联系人外键 |
| Zero Duplicate `party.contact_person` | 报价预览复用的当前客户联系人 |
| `nde.customer.contact` | 打印上下文中由客户主表映射的联系人 |
| supplier contact fields | 供应商对象联系人，不属于客户 |
| document recipient | 文档上下文文本，不是联系人主数据 |
| primary/role/department/title | UNKNOWN / 未建模 |
| consent/preference/status | UNKNOWN / 未建模 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Contact | 当前客户行上的联系人展示 |
| `has_contact` | Business Graph 关系目录词 |
| `center` | Customer360 客户节点角色 |
| Primary / Secondary | 期待联系人优先级；UNKNOWN |
| Active / Inactive | 期待联系人状态；UNKNOWN |
| Decision Maker / Buyer / Influencer / Technical / Finance | 期待业务角色；UNKNOWN |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 多联系人主表或明细表 | customer DDL、`apps/customer/**`, full-repo contacts/customer_contacts search |
| 主联系人及备用联系人规则 | customer templates、repository、Object360 customer |
| 联系人岗位、部门和业务角色 | customer schema/forms、Graph registry、docs/reports |
| 决策人、影响人和采购委员会 | customer/quotation/sales/marketing paths, decision-maker keywords |
| 联系人停用、离职和历史版本 | customer history、followups、runtime DDL |
| 邮件/电话/WhatsApp 同意与偏好 | customer/marketing/communication paths, consent/preference search |
| 单据是否冻结联系人快照 | quotation/sales/document templates and schemas |
| Customer Graph contact 节点的真实生产者 | `v15/enterprise_business_graph/**`, Object360 relationship runtime |
| 客户联系人字段级隐私、脱敏和访问审计 | customer router/templates、security/privacy paths、constitution；未见运行实现 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `runtime/v14/legacy_support.py` | 客户仅有一组联系人字段，无联系人明细表证据 |
| `apps/customer/services.py` | 联系人随客户整体新增/覆盖 |
| `apps/customer/repository.py` | 搜索联系人/电话/WhatsApp，业务查询无 contact ID |
| `apps/customer/router.py` | 表单字段与客户详情权限缺口 |
| `templates/customer_detail.html` | Contacts 标签只显示单组字段 |
| `templates/edit_customer.html` | 直接编辑单组联系人数据 |
| `apps/customer/history.py` | Customer360 聚合无联系人集合 |
| `core/object360/customer/customer_object.py` | contact_person 只是客户适配属性 |
| `core/object360/customer/runtime.py` | 联系人进入摘要/搜索，不生成联系人实体 |
| `v15/enterprise_business_graph/registry.py` | contact 是 Customer Graph 类型词汇 |
| `v15/enterprise_business_graph/relationships.py` | `has_contact` 是通用关系目录 |
| `v15/ux/master_defaults.py` | Zero Duplicate 从客户主表解析 party 联系字段 |
| `document/nde_engine.py` | NDE 文档联系人映射 |
| `business_modules/crm.md` | CRM 权威表未列 contacts |
| `docs/reports/V151E_Volume007_Customer_Business_Chain_Extraction_Report.md` | Customer 提取只涵盖 customers/followups |
| `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` | Customer360 运行诚实性边界 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
