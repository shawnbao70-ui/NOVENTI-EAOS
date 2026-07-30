# 需求（Business Requirement）— Legacy Knowledge

**Evidence strength:** Strong（实体、商机 1:N、追溯字段、需求转报价）/ Medium（跨表一致性）/ Missing（完整状态转换与客户反馈持久化）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 `business_requirements` 业务需求实体、它与客户/商机/样品/报价/销售订单的追溯，以及 Requirement360 装配。它不覆盖 `sample_requirements`；后者只是某个样品的应用与商业参数记录。

强证据来自 schema、repository、routes、workflow 与 Requirement360。状态词汇存在强证据，但除创建默认状态外，未找到受控的逐状态转换入口，因此状态机实现强度为弱。Customer feedback 在 Requirement360 中固定为空列表，持久化规则为 `UNKNOWN`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| REQUIREMENT-RULE-001 | 需求是客户具体需要的主记录，可选归属客户和商机 | 创建表单只强制 title | Strong |
| REQUIREMENT-RULE-002 | 一个商机可关联多个需求；需求以 `opportunity_id` 指向父商机 | 可创建无商机需求 | Strong |
| REQUIREMENT-RULE-003 | 创建关联商机的需求时，父商机 `requirement_count` 加 1 | 未见删除、改挂或重算时的减计数 | Strong/Weak consistency |
| REQUIREMENT-RULE-004 | 需求编号默认 `REQ-YYYYMMDD-NNNN`；序号来自表行数 + 1 | 可由调用方提供编号；并发/删除后的唯一性风险未处理 | Strong |
| REQUIREMENT-RULE-005 | 创建默认来源 `manual_entry`、类型 `general_product_inquiry`、状态 `new`、优先级 `normal`、AI 分析状态 `pending` | 调用方可覆盖 | Strong |
| REQUIREMENT-RULE-006 | 创建者当前用户名写入 `salesperson` | 未见后续重新分配流程 | Strong |
| REQUIREMENT-RULE-007 | Requirement Center/detail 受 `Quotes.view`，创建受 `Quotes.add` | 与商机使用 Customers 权限不一致 | Strong |
| REQUIREMENT-RULE-008 | 需求可保存样品、报价、销售订单快捷指针 | `sample_id`、`quote_id`、`sales_order_id` 均可为空 | Strong |
| REQUIREMENT-RULE-009 | `requirement_links` 用 `entity_type + entity_id + link_role` 保存扩展追溯 | 未见唯一约束，可能重复 | Strong |
| REQUIREMENT-RULE-010 | 从需求创建报价时，报价写 `requirement_id`；需求有商机时，报价同时写 `opportunity_id` | 需求不存在则链接函数不动作 | Strong |
| REQUIREMENT-RULE-011 | 报价链接成功后回写需求 `quote_id`，并新增 role=`direct` 的 quote link | 表/列缺失或异常会静默跳过 link | Medium |
| REQUIREMENT-RULE-012 | 从样品创建报价时，可通过样品携带的需求/商机建立 role=`from_sample` 的 quote link | 依赖可选追溯列 | Medium |
| REQUIREMENT-RULE-013 | 报价转销售订单后，需求/商机追溯复制到订单，需求回写 `sales_order_id` 并新增 role=`from_quote` 链接 | 异常静默降级 | Medium |
| REQUIREMENT-RULE-014 | Requirement360 同时按快捷指针和反向外键装配样品、报价、订单，并继续装配交付单 | 样品查询可能重复同一记录；未见去重 | Strong |
| REQUIREMENT-RULE-015 | 需求可以有多个产品匹配候选，按 confidence 降序展示 | `match_type`、confidence 服务端约束有限 | Strong |
| REQUIREMENT-RULE-016 | 产品匹配持久化成功后，若当前状态不在 `matched`、`quoted`、`closed`、`cancelled`，需求自动改为 `matched` | 这是除创建默认 `new` 外找到的明确状态推进 | Strong |
| REQUIREMENT-RULE-017 | 代码定义了 Sample→Requirement 双向绑定 helper，但全库未找到调用点 | 不得把 helper 的存在写成已接线流程 | Weak |
| REQUIREMENT-RULE-018 | Lifecycle 声明需求位于商机之后、分析/匹配/推荐/样品之前 | 声明链不等于已实现状态机 | Medium |
| REQUIREMENT-RULE-019 | 客户反馈持久化与需求关闭条件为 `UNKNOWN` | Requirement360 的 `customer_feedback` 固定为空 | Missing |

## 3. 流程

### 3.1 商机下创建需求

1. 进入商机详情。
2. 创建需求并继承/提交商机与客户引用。
3. 系统生成需求编号，写默认来源、类型、状态、优先级、AI 状态和当前用户。
4. 若有商机，商机的需求缓存计数递增。
5. Requirement360 装配客户、商机、匹配、样品、报价、订单、交付和时间线。

### 3.2 需求到报价及订单追溯

1. 从 Requirement360 的 Create Quote 深链进入报价创建，携带 `requirement_id` 与可用的 `customer_id`。
2. 创建 Draft 报价。
3. 报价写需求 id，并从需求传播商机 id。
4. 需求回写 `quote_id`，链接表增加 `quote/direct`。
5. 报价转订单后，订单继承需求/商机 id；需求回写 `sales_order_id`，链接表增加 `sales_order/from_quote`。
6. 任一可选表/列或 hook 不可用时，Legacy 可能保留业务单据但丢失追溯。

### 3.3 声明式需求阶段

`new → analyzing → matched → sample_pending → sample_sent → feedback_received → quoted → ordered → closed / cancelled`

这是词汇集合。已确认创建写 `new`、产品匹配可推进到 `matched`；其余阶段未找到逐步转换守卫、前置条件或角色矩阵，因此不可视为完整已实现流程。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| REQUIREMENT-VAL-001 | 创建 title 必填 | 强 | HTTP Form 强制；repository 仍有 `Untitled Requirement` 回退 |
| REQUIREMENT-VAL-002 | 查看/创建分别要求 `Quotes.view` / `Quotes.add` | 强 | 权限模块命名与需求能力不一致 |
| REQUIREMENT-VAL-003 | schema 对 `title`、`source_type`、`requirement_type` 非空 | 强 | 客户、商机可空 |
| REQUIREMENT-VAL-004 | `opportunity_id` 有 schema 外键声明 | 中 | SQLite 外键是否启用、客户/下游字段外键均未确认 |
| REQUIREMENT-VAL-005 | 状态必须属于 `REQUIREMENT_STATUSES` | 弱/缺失 | UI提供词汇，但 repository update 不校验 |
| REQUIREMENT-VAL-006 | 来源、类型、匹配类型必须属于常量集合 | 弱 | 表单/展示使用常量，服务端持久层未见硬约束 |
| REQUIREMENT-VAL-007 | 商机与客户必须一致 | 缺失 | 可提交互不相干的 `customer_id` 与 `opportunity_id` |
| REQUIREMENT-VAL-008 | 商机 `requirement_count` 与实际子项一致 | 缺失 | 仅创建增量，未见对账 |
| REQUIREMENT-VAL-009 | 每个需求只能有一个报价/订单 | 缺失 | 快捷指针单值，但反向查询和 links 支持多记录 |
| REQUIREMENT-VAL-010 | 追溯链接唯一、事务性写入 | 缺失 | hook 多处吞异常，链接表无唯一约束 |

## 5. 数据含义

### 5.1 主体与关系

| 实体 | 含义 |
|---|---|
| `business_opportunities` | 客户销售机会；一侧父实体 |
| `business_requirements` | 某个具体客户需要；多侧子实体 |
| `requirement_product_matches` | 需求与产品候选的多条匹配 |
| `requirement_links` | 需求到任意下游/文档实体的扩展追溯 |
| `sample_requirements` | 样品附属参数，不是本需求实体 |

### 5.2 需求字段

| 字段 | 含义 |
|---|---|
| `requirement_code` | 可读需求编号 |
| `opportunity_id` | 可选父商机；形成商机 1:N |
| `customer_id` | 可选客户 |
| `title` / `description` | 需求摘要与描述 |
| `source_type` | 需求来源渠道 |
| `requirement_type` | 需求形态/问题类型 |
| `status` | 需求阶段词汇 |
| `salesperson` | 创建时当前用户名 |
| `priority` | 优先级；默认 normal |
| `sample_id` | 一个快捷样品指针；反向关系可能有多条样品 |
| `quote_id` | 一个快捷报价指针；反向关系可能有多条报价 |
| `sales_order_id` | 一个快捷订单指针；反向关系可能有多条订单 |
| `ai_analysis_status` | AI 分析状态，默认 pending；完整转换 `UNKNOWN` |
| `created_at` / `updated_at` | 创建与最近更新文本时间 |

### 5.3 来源与类型词汇

- 来源：`customer_sample`、`customer_description`、`customer_email`、`whatsapp`、`wechat`、`phone_call`、`meeting`、`website_inquiry`、`exhibition`、`sales_visit`、`ai_recommendation`、`sales_recommendation`、`manual_entry`
- 类型：`physical_sample`、`photo`、`drawing`、`specification`、`replacement_part`、`equivalent_product`、`technical_consultation`、`machine_upgrade`、`maintenance_request`、`general_product_inquiry`
- 匹配类型：`matched`、`alternative`、`compatible`、`equivalent`、`recommended`

## 6. 状态词汇

| 状态 | 语义 |
|---|---|
| `new` | 新需求 |
| `analyzing` | 分析中 |
| `matched` | 已产生产品匹配；有自动写入证据 |
| `sample_pending` | 等待样品 |
| `sample_sent` | 需求侧记录样品已发；发运实现 `UNKNOWN` |
| `feedback_received` | 已收到反馈；反馈存储实现 `UNKNOWN` |
| `quoted` | 已报价 |
| `ordered` | 已下单 |
| `closed` | 已关闭 |
| `cancelled` | 已取消 |
| `pending`（AI） | AI 分析待处理；后续词汇 `UNKNOWN` |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\product_matching.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\requirement_center.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\requirement360.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\opportunity_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
