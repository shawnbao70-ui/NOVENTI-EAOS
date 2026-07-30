# 客户层级、集团与门店（Customer Hierarchy）— Legacy Knowledge

**Evidence strength:** Strong negative for customer parent/group/store hierarchy; strong for flat customer master and downstream customer references  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 的活动客户主数据是扁平的 `customers` 记录。每条记录独立保存公司名、国家、城市、类型、等级、状态、负责人及一个联系人；报价、订单、交付和收款直接引用单个 `customer_id`。

未发现客户父级、集团号、总部、子公司、门店、账单主体、收货主体或层级生效期字段。`organizations.parent_id` 属于组织/租户结构，`distributor_regions` 属于经销商区域，Customer Graph 的关系边属于通用图谱能力，均不能当成客户集团层级。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CH-R1 | 每条 `customers` 记录是独立客户主体 | 主表没有 parent/group/store 外键 |
| CH-R2 | 报价、销售订单和收款直接引用单个客户 ID | 不会自动汇总到集团客户 |
| CH-R3 | 交付通过销售订单取得客户归属 | 仍是单层引用 |
| CH-R4 | 客户详情只汇总该客户 ID 的报价、订单、交付和收款 | 不递归包含子公司或门店 |
| CH-R5 | 客户列表余额也是逐客户计算 | 同名、同集团记录不会合并 |
| CH-R6 | `company_name` 是客户显示名称，不是集团主键 | 可重复且未见唯一约束 |
| CH-R7 | `customer_code` 是人工客户代码 | 未见唯一约束或集团编码规则 |
| CH-R8 | `country`、`city` 是地址分类文本 | 不建立区域层级或门店关系 |
| CH-R9 | `customer_type` 与 `customer_level` 是分类属性 | 不代表母公司/子公司或总部/门店 |
| CH-R10 | Customer360 关系图只连接该客户的报价、订单、交付和收款 | 不产生 customer→customer 边 |
| CH-R11 | Enterprise Customer Relationship bridge 明示 defer to Legacy | 架构链名称不证明层级运行 |
| CH-R12 | Enterprise Business Graph 支持通用关系目录 | 当前客户链未证明集团归属写入来源 |
| CH-R13 | `organizations.parent_id` 管理平台组织层级 | 不得与客户集团层级混用 |
| CH-R14 | 经销商区域/客户关联属于 Distributor 子域 | 不得推导普通客户门店结构 |
| CH-R15 | 删除客户会直接删除该客户的报价、订单、收款和跟进 | 不检查集团子节点或共享主体 |
| CH-R16 | EAOS 迁移不得按同名、国家或负责人自动合并客户 | 缺少法律主体与层级证据 |
| CH-R17 | `tenant_id` 表达租户隔离，不表达客户集团父子关系 | 多租户维度不得冒充业务层级 |
| CH-R18 | 内部 `branches`/`companies` 与客户主表无可证 FK | 分支机构是组织域，不是客户门店 |
| CH-R19 | Customer Object360 的可选 `company_id` 未从客户记录填充 | 不能据此关联内部公司 |

---

## 3. Process

### 3.1 当前客户建立与引用

1. 用户创建一条扁平客户记录。
2. 人工填写客户代码、公司名、地点、分类、负责人等。
3. 报价选择该客户 ID。
4. 报价转订单后复制相同客户 ID。
5. 交付、收款和 Customer360 继续按该 ID 查询。

### 3.2 当前 Customer360 关系

1. Customer360 读取单个客户记录。
2. 按同一 `customer_id` 读取报价、订单、交付和收款。
3. 运行时关系视图生成 customer→quote/order/delivery/receipt 关联。
4. 未见 customer→parent customer、subsidiary、branch 或 store 关联。

### 3.3 缺失的集团流程

未观察到：建立集团主体 → 添加法律实体/门店 → 定义总部和账单主体 → 继承条款/信用额度 → 汇总集团销售与应收 → 调整层级并保留历史。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CH-V1 | 客户代码必须唯一 | Missing | DDL 未见唯一约束，服务未查重 |
| CH-V2 | 公司名与国家组合去重 | Missing | 可建立重复客户 |
| CH-V3 | 父客户必须存在 | Not modeled | 无父级字段 |
| CH-V4 | 客户不能成为自己的祖先 | Not modeled | 无层级图 |
| CH-V5 | 层级不得形成循环 | Not modeled | 无 parent 关系 |
| CH-V6 | 门店必须引用一个有效法律主体 | Not modeled | 无门店实体 |
| CH-V7 | 集团账单主体必须唯一且有效 | Not modeled | 无 billing parent |
| CH-V8 | 子公司国家/税务身份应独立保存 | Partial | 国家可保存，税务/法人关系未建模 |
| CH-V9 | 层级变更必须记录生效日与历史 | Missing | 无历史表 |
| CH-V10 | 集团信用和子公司信用不得重复计算 | Missing | 只有单客户启发式余额 |
| CH-V11 | 删除父级前必须检查子级 | Missing | 删除逻辑不了解层级 |
| CH-V12 | 当前租户组织不得冒充客户集团 | Semantic guard | `organizations` 是平台组织 |
| CH-V13 | 客户页面查询应保持 tenant scope | Mixed | utils 有租户过滤，页面 repository 主查询未显式调用 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `customers.id` | 单个扁平客户记录标识 |
| `customer_code` | 人工客户代码，唯一性未证实 |
| `company_name` | 客户显示公司名 |
| `country` / `city` | 客户地点文本 |
| `customer_type` | 客户业务分类，不是层级角色 |
| `customer_level` | A/B/C/D 等价值等级，不是父子层级 |
| `owner` | 客户负责人用户名文本 |
| `quotes.customer_id` | 报价直接客户 |
| `sales_orders.customer_id` | 订单直接客户 |
| `receipts.customer_id` | 收款直接客户 |
| Delivery customer | 通过销售订单关联的客户 |
| Customer360 relationship nodes | 当前客户与其业务单据的运行时派生关系 |
| `organizations.parent_id` | 平台组织父级，非客户父级 |
| `companies` / `branches` | 内部法人和分支结构，与 customer 无已证映射 |
| `customers.tenant_id` | 多租户隔离维度，不是客户集团 ID |
| Object360 `company_id` | 可选适配槽位；当前客户记录未填充 |
| `distributor_regions` | 经销商区域主数据，非普通客户集团 |
| parent/head-office/store fields | UNKNOWN / 未发现 |
| consolidated group balance | UNKNOWN / 未实现 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| A/B/C/D | 客户等级，不是组织层级 |
| OEM / customer type values | 客户分类，不是总部/门店角色 |
| `center` | Customer360 图中心节点角色 |
| `association` | 单据关联边，不是股权或集团关系 |
| `CHILD` / `REFERENCE` | Object360 架构关系种类；bridge 仍 defer |
| Head Office / Subsidiary / Branch / Store | 期待词汇；活动客户模型 UNKNOWN |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 客户父级、集团号或集团主档 | `apps/customer/**`, `core/customer/**`, customer DDL, full-repo parent/group search |
| 总部、分公司、门店实体 | customer templates、Object360、business modules、head-office/branch/store search |
| 集团统一信用额度及分配 | `apps/finance/**`, customer credit fields, Customer360 credit tab |
| 集团统一报价条款或价格继承 | `apps/quotation/**`, master defaults, customer hierarchy searches |
| 集团级应收汇总与内部抵销 | `apps/finance/**`, Customer360 balance queries, AR reports |
| 客户层级生效期和变更历史 | customer history/utils/repository、runtime DDL |
| 客户图谱是否有真实 customer→customer 写入 | `v15/enterprise_business_graph/**`, Object360 relationship runtime |
| `organizations.parent_id` 是否曾映射客户 | organization/tenant schemas、customer services、manifest reports；未见映射 |
| Object360 `company_id` 的真实客户映射来源 | customer object adapter、customers DDL、company/organization schemas；未找到 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `runtime/v14/legacy_support.py` | 扁平 `customers` 字段；无客户父级/门店字段 |
| `apps/customer/services.py` | 单客户建立、详情汇总和删除流程 |
| `apps/customer/repository.py` | 所有下游查询按单一 `customer_id` |
| `apps/customer/history.py` | Customer360 历史只聚合直接业务对象 |
| `core/customer/customer.py` | Customer 域主表仅为 `customers` |
| `core/object360/customer/customer_object.py` | 企业适配字段仍是扁平客户属性 |
| `core/object360/customer/runtime.py` | 只生成客户到单据的关系边 |
| `core/object360/customer/relationship_bridge.py` | 架构 bridge defer to Legacy |
| `core/object360/relationship_engine.py` | 关系解析仍 defer，不建立客户 parent 边 |
| `v15/enterprise_business_graph/registry.py` | Customer Graph 类型目录 |
| `v15/enterprise_business_graph/relationships.py` | 通用客户关系词汇，非层级主数据 |
| `business_modules/crm.md` | CRM 权威表只有 customers/followups 等 |
| `docs/reports/V151E_Volume007_Customer_Business_Chain_Extraction_Report.md` | 提取范围和客户架构边界 |
| `database/v41_tenant_column_schema.py` | customers 的 tenant_id 属于租户隔离 |
| `templates/customer_detail.html` | 单客户业务链和无层级界面 |
| `templates/edit_customer.html` | 编辑字段无 parent/group/store |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
