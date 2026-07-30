# 样品（Sample）— Legacy Knowledge

**Evidence strength:** Strong（收样、分析、转报价、入库）/ Medium（需求与商机追溯）/ Missing（申请、审批、向客户发样）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 Legacy 样品记录的创建、分析资料、客户关联、需求/商机追溯及转报价交界。运行证据表明该模块主要表达“收到客户样品并分析”，且可把绑定产品作为 `Sample Receipt` 入库。

以下目标语义缺证据，必须保持 `UNKNOWN`：

- 样品申请单及申请人、申请数量、期望日期：`UNKNOWN`
- 样品审批人、审批意见、审批矩阵：`UNKNOWN`
- 向客户发样的承运、运单、发出/签收状态：`UNKNOWN`

上述缺口已查：`apps/sample/`、`apps/quotation/`、`v15/business_lifecycle/`、`runtime/v14/legacy_support.py`、`templates/samples.html`、`templates/sample_detail.html`、`templates/sample360.html`、`docs/reports/Business_Strong_A005_Sample_Quote_Report.md`、`docs/reports/Business_Strong_A017_Sample_Ops_Report.md`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| SAMPLE-RULE-001 | 新建样品必须选择客户；系统生成 `SP` + 时间戳编号、收样日期为当天、状态为 `New` | 创建入口只接收 `customer_id` | Strong |
| SAMPLE-RULE-002 | 样品列表按记录 id 倒序，并通过 `customer_id` 装配客户名称 | 无所有者过滤证据 | Strong |
| SAMPLE-RULE-003 | 样品可保存尺寸、重量、节距、齿数、材质、硬度；详情只取最新一条测量 | 多次保存形成历史，但默认展示最近记录 | Strong |
| SAMPLE-RULE-004 | Sample360 可分别记录样品需求、材料分析、质量评估、供应商匹配 | 这些是样品附属分析，不等同 `business_requirements` | Strong |
| SAMPLE-RULE-005 | 样品可与目录产品绑定；绑定产品且未入库时才具备物化条件 | `product_id <= 0` 阻断 | Strong |
| SAMPLE-RULE-006 | 入库物化同时更新库存、产品库存与库存台账；台账类型 `Sample Receipt`，备注 `SAMPLE-{id}` | 同样品已有对应台账时拒绝重复；数量必须大于 0 | Strong |
| SAMPLE-RULE-007 | 入库成功后样品状态写为 `Stocked` | 这表示收货入库，不表示发样 | Strong |
| SAMPLE-RULE-008 | 从样品创建报价时生成 Draft 报价，沿用样品客户、主数据商业默认值，并写 `sample_id` | 未找到样品不存在时的硬阻断；可能形成空客户报价 | Strong |
| SAMPLE-RULE-009 | 样品存在 `requirement_id` / `opportunity_id` 时，转报价会把追溯字段传到报价，并回写需求的 `quote_id` 与 link | 表或列缺失时静默降级 | Medium |
| SAMPLE-RULE-010 | 代码定义了样品与业务需求双向绑定 helper：样品写 `requirement_id`，需求可写 `sample_id` | 全库未找到该 helper 的调用点；属于未接线设计意图，不是已实现业务流程 | Weak |
| SAMPLE-RULE-011 | Lifecycle 把 Sample 放在推荐之后、客户反馈与报价之前 | 声明式链路不是完整状态机 | Medium |
| SAMPLE-RULE-012 | 样品图片上传接受经安全校验的图片类型；删除图片记录要求 `Samples.delete` | 固定槽位上传/删除未见同等权限校验 | Medium |
| SAMPLE-RULE-013 | 样品申请审批规则为 `UNKNOWN` | 已查路径未见 request/approve 实体或处理器 | Missing |
| SAMPLE-RULE-014 | 向客户发样及签收规则为 `UNKNOWN` | `sample_sent` 只出现在需求状态词汇，未见样品发运实现 | Missing |

## 3. 流程

### 3.1 有实现证据的收样/分析流程

1. 从样品中心选择客户并创建样品。
2. 系统生成样品编号、收样日期与 `New` 状态。
3. 在详情或 Sample360 上传图片、保存测量、需求描述、材料分析、质量评估及供应商匹配。
4. 可选：将样品绑定到业务需求/商机追溯。
5. 可选分支 A：从样品创建 Draft 报价，并传递客户及可用追溯字段。
6. 可选分支 B：绑定目录产品后，以正数量执行 `Sample Receipt` 入库，状态变为 `Stocked`。

### 3.2 申请/审批/发样流程

`申请 → 审批 → 备样 → 发出 → 客户签收`：`UNKNOWN`。Legacy 中没有找到足以确认这些步骤、角色、单据和转换条件的实现；不得用 `New`、`Stocked` 或需求状态 `sample_sent` 代替该流程。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| SAMPLE-VAL-001 | 新建样品的 `customer_id` 为必填表单字段 | 强 | 未确认数据库外键约束 |
| SAMPLE-VAL-001A | 新建样品的服务端权限门 | 缺失 | UI 按 `Samples.add` 隐藏按钮，但 POST 路由未调用权限检查 |
| SAMPLE-VAL-002 | 入库前样品存在、已绑定有效产品、数量 > 0 | 强 | 任一失败返回明确错误键 |
| SAMPLE-VAL-003 | 同一样品已有 `Sample Receipt` 台账时禁止再次物化 | 强 | 以台账类型 + 备注判重 |
| SAMPLE-VAL-004 | 绑定产品和物化要求 `Samples.edit` | 强 | 路由权限门 |
| SAMPLE-VAL-005 | 删除普通图片要求 `Samples.delete` | 强 | 固定槽位删除未见相同门禁 |
| SAMPLE-VAL-006 | 上传文件必须通过图片安全校验 | 强 | 扩展名不在白名单时回退为 jpg；内容校验由上传组件承担 |
| SAMPLE-VAL-007 | 测量、分析、评分、目标价、年需求等数值范围 | 弱/缺失 | 默认 0，未见业务区间校验 |
| SAMPLE-VAL-008 | 从样品创建报价前确认样品存在、已审批或已发样 | 缺失 | 未见服务端门禁 |
| SAMPLE-VAL-008A | 从样品创建报价的服务端权限门 | 缺失 | 路由未见 `Quotes.add` 或 `Samples.view` 检查 |
| SAMPLE-VAL-009 | 样品申请、审批、发样角色与状态转换 | 缺失 | `UNKNOWN` |

## 5. 数据含义

| 实体/字段 | 业务含义 |
|---|---|
| `samples` | 客户样品主记录；历史建表片段存在字段形态差异 |
| `sample_no` | `SP` + 创建时间戳的可读编号 |
| `customer_id` | 样品所属客户；创建时唯一明确的业务必填 |
| `receive_date` | 收到样品的日期 |
| `status` | 样品当前标签；确认值仅 `New`、`Stocked` |
| `product_id` | 后加的可选目录产品绑定，用于库存物化 |
| `requirement_id` / `opportunity_id` | 后加的上游追溯字段 |
| `sample_measurements` | 尺寸、重量和材质等测量历史 |
| `sample_requirements` | 样品层面的应用、环境、寿命、目标价、包装等描述；不是业务需求主表 |
| `sample_material_analysis` | 材料与风险分析 |
| `sample_quality_assessment` | 外观、精度、强度、耐久、包装评分及总等级 |
| `sample_supplier_matching` | 候选供应商、价格、MOQ、交期与质量评分 |
| `sample_images` | 样品图片附件 |
| `quotes.sample_id` | 报价对来源样品的追溯 |
| `inventory_ledger` | 样品入库的幂等与审计凭据 |

## 6. 状态词汇

| 词汇 | 证据位置 | 含义/限制 |
|---|---|---|
| `New` | 样品创建、列表 KPI | 新收样品 |
| `Stocked` | 样品物化服务、列表 KPI | 已作为库存收货 |
| `sample_pending` | 需求状态常量 | 需求等待样品；不是样品审批状态 |
| `sample_sent` | 需求状态常量 | 需求侧“样品已发”标签；未找到对应样品发运实现 |
| Draft | 样品转报价 | 新报价初始状态 |
| 其他样品状态 | — | `UNKNOWN`；列表会归入 other，但未定义正式词汇 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\samples.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A017_Sample_Ops_Report.md`
