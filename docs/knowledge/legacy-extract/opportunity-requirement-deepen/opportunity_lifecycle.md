# 商机状态机声明与实现缺口

## Scope与证据强度

本页比较三类证据：企业链路阶段声明、商机记录的 `status` 字段、实际可调用的状态转换。`customer → business_opportunity → requirement` 的导航声明和新建默认 `open` 为强证据；商机从 open 到 qualified/converted/closed 的执行入口未找到。

因此，“处于生命周期链中”不等于“拥有可执行状态机”。需求有丰富状态常量及 repository 更新 primitive，也不能反推商机拥有同样能力。

## 业务规则（稳定ID）

1. **OL-R01** 声明式企业链把 `business_opportunity` 放在 customer 之后、requirement 之前。
2. **OL-R02** `LIFECYCLE_FLOW` 为每个阶段提供标签与导航 route；它是页面流程图，不执行状态转换。
3. **OL-R03** 新建商机默认状态固定为 `open`。
4. **OL-R04** 商机中心接受任意 `status` 查询参数并做数据库等值过滤。
5. **OL-R05** 中心 Open KPI 仅统计当前最多 100 条结果集中 `status == open` 的数量。
6. **OL-R06** 商机详情只显示状态 badge；未见状态选择器或更新表单。
7. **OL-R07** repository 未提供 `update_opportunity_status`，routes 也没有商机状态 POST/API。
8. **OL-R08** “qualified/converted/closed”可出现在架构说明或语义描述，但不是当前代码中的受控商机枚举。
9. **OL-R09** `REQUIREMENT_STATUSES` 是需求状态词汇，不能用于约束 `business_opportunities.status`。
10. **OL-R10** 创建需求只递增 `requirement_count` 与 `updated_at`，不把商机改为 qualified 或 converted。
11. **OL-R11** 从需求创建样品、报价或订单的 workflow 不更新商机 status。
12. **OL-R12** 商机没有赢单/丢单原因、关闭时间、概率或阶段历史表证据。
13. **OL-R13** status API 返回 lifecycle stages 和 schema readiness，不返回商机状态迁移图。
14. **OL-R14** schema 对 status 只有文本默认值，没有 CHECK 约束或外键词典。
15. **OL-R15** 商机列表可展示任意存量状态文本；中心只把 open 识别为 KPI。
16. **OL-R16** 下游对象可携带 `opportunity_id` 形成追溯，但这不代表商机已 converted。
17. **OL-R17** `requirement_count > 0` 不会自动推导或持久化商机阶段。
18. **OL-R18** 路由支持 status query filter，但商机中心模板没有状态筛选控件。
19. **OL-R19** lifecycle panel 有 opportunity 阶段映射，但商机详情未接 enrich/traceability include；公共 stage chip 的允许路由也排除了 `/business/opportunities`。
20. **OL-R20** 固定业务链导航从 Customers 直接到 Requirements，跳过 Opportunities，与声明链第二阶段不一致。
21. **OL-R21** won/lost/converted 等终态可在 Quote 语义层出现，不会回写 `business_opportunities.status`。

## 流程

### 声明流程

Customer → Business Opportunity → Requirement → Analysis → Matching → Sample → Feedback → Quotation → Sales Order → 后续履约。

### 实际商机流程

1. 人工创建，状态写 `open`。
2. 中心按文本 status 可选过滤，详情显示当前值。
3. 详情创建 0..N 条需求。
4. 后续需求可能关联样品、报价和订单。
5. 商机 status 不随这些动作自动变化。
6. 未找到 qualified、converted、closed、won、lost 的商机状态写入口。

## 校验（强/弱/缺失）

1. **OL-V01（强/默认）** 创建时缺省 status 统一落 `open`。
2. **OL-V02（缺失）** status 无服务端枚举校验。
3. **OL-V03（缺失）** schema 无 status CHECK。
4. **OL-V04（缺失）** 未定义合法转移矩阵或前置状态门禁。
5. **OL-V05（缺失）** 未验证关闭商机必须有原因、金额、结果或 owner。
6. **OL-V06（缺失）** 未阻止已关闭/任意自定义状态商机继续创建需求。
7. **OL-V07（弱/查询）** 列表 status 参数只做等值过滤，不检查合法词汇。
8. **OL-V08（缺失）** 下游报价/订单创建不校验商机处于 qualified/converted。
9. **OL-V09（缺失）** 未见 optimistic lock、版本号或更新时间冲突检查。
10. **OL-V10（强/权限但非状态）** 查看/创建受 Customers 权限控制；没有状态变更专属权限。
11. **OL-V11（缺失）** 未见状态变更审计日志或状态历史。
12. **OL-V12（弱/展示）** badge 如实显示存量文本，但颜色不表达合法迁移。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `business_opportunities.status` | 自由文本状态，默认 open |
| `open` | 唯一在创建和 KPI 中被明确消费的商机状态 |
| `qualified` | 架构/期望词汇；未找到商机写入口 |
| `converted` | 期望语义；创建需求/报价不会自动写 |
| `closed` | 可能的关闭词汇；无原因/时间/结果实现 |
| `won` / `lost` | 未在商机常量和 schema 中定义 |
| `LIFECYCLE_STAGES` | 企业对象/能力顺序，不是状态集合 |
| `LIFECYCLE_FLOW` | 阶段标签与导航路由 |
| `business_opportunity` | 生命周期阶段 ID |
| `requirement_count` | 子需求缓存数量，不是阶段 |
| `updated_at` | 创建需求时也会更新，不能单独解释为状态变更时间 |
| `opportunity_id` | 下游追溯字段，不是 converted 标志 |
| `REQUIREMENT_STATUSES` | 需求专用的 new…closed/cancelled 词汇 |
| `filter_status` | 页面当前过滤字符串 |
| `schema_ready` | 业务生命周期表能力探针 |
| `workflow_integrated` | status API 固定能力声明，不证明每条状态迁移可执行 |

## 状态词汇

| 词汇 | 实现判断 |
|---|---|
| open | 已实现默认、过滤和 KPI |
| qualified | 声明/文档层；写路径缺失 |
| converted | 声明/文档层；不由 requirement_count 或 quote link 驱动 |
| closed | 自由文本可能可存；受控关闭流程缺失 |
| won/lost | 未见商机领域定义 |
| new…cancelled | 需求状态，不属于商机 |
| business_opportunity | 企业链阶段，不是行状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| OL-E01 | 企业阶段顺序与导航 route | 强（声明） | `v15/business_lifecycle/constants.py` |
| OL-E02 | 中心状态过滤、创建和 status API | 强 | `v15/business_lifecycle/routes.py` |
| OL-E03 | 创建默认 open、列表等值过滤、无商机更新方法 | 强 | `v15/business_lifecycle/repository.py` |
| OL-E04 | status 是无 CHECK 的 TEXT DEFAULT open | 强 | `database/business_lifecycle_schema.py` |
| OL-E05 | 中心只统计 Open 并原样展示 badge | 强 | `templates/business/opportunity_center.html` |
| OL-E06 | 详情只读显示 status，创建需求不改状态 | 强 | `templates/business/opportunity_detail.html` |
| OL-E07 | workflow 只传播 requirement/opportunity id，不写商机状态 | 强（负证据） | `v15/business_lifecycle/workflow.py` |
| OL-E08 | Requirement360 使用独立需求状态词汇 | 强（边界） | `v15/business_lifecycle/requirement360.py` |
| OL-E09 | 既有商机页已标注“doc-only state machine” | 强（交叉） | `docs/knowledge/legacy-extract/crm/opportunity.md` |
| OL-E10 | 生命周期/架构报告主要证明平台链路声明 | 中 | `docs/reports/V15_BUSINESS_ARCHITECTURE_REPORT.md`、`V15_ENTERPRISE_READINESS_REPORT.md` |
| OL-E11 | stage chip 与固定链导航未纳入商机 | 强（UI偏差） | `templates/includes/business/lifecycle_traceability.html`、`templates/includes/nav_business_chain.html` |
| OL-E12 | context 有 stage map，但无 opportunity 分支；商机详情未注入 panel | 强（缺口） | `v15/business_lifecycle/context360.py`、`enrich.py`、`templates/business/opportunity_detail.html` |

## UNKNOWN + 已查路径

1. **生产数据库中除 open 外实际出现哪些商机状态 UNKNOWN。** 已查路径：schema、routes、repository、templates；未读取生产数据。
2. **qualified/converted/closed 是否由外部集成直接更新数据库 UNKNOWN。** 已查路径：v15 lifecycle、apps/customer、apps/quotation、business_modules、reports。
3. **商机赢单/丢单业务词汇和关闭原因 UNKNOWN。** 已查路径：constants、schema、templates、docs/reports。
4. **`requirement_count` 达到何值应触发状态变化 UNKNOWN。** 已查路径：create_requirement、商机详情和生命周期报告。
5. **报价或订单成功后商机应 converted 还是 closed UNKNOWN。** 已查路径：workflow、quotation、sales order 与 lifecycle constants。
6. **status filter 是否有隐藏 UI 控件 UNKNOWN。** 已查路径：opportunity_center、公共 center layout、导航 includes。
7. **状态变更是否写通用审计日志 UNKNOWN。** 已查路径：workflow、repository、logging/audit 调用。
8. **删除/取消需求后商机状态是否需回退 UNKNOWN。** 已查路径：需求 routes/repository、商机计数和模板。
9. **多租户下状态词典是否可配置 UNKNOWN。** 已查路径：schema、platform settings、business_modules 和报告。
10. **声明链为何在公共导航和 stage chip 中跳过商机 UNKNOWN。** 已查路径：constants、context360、enrich、两个 include 模板和导航报告。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
