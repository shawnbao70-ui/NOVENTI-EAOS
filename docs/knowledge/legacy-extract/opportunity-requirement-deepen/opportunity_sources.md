# 商机来源类型、创建与编号

## Scope与证据强度

本页深化持久化 `business_opportunities` 的人工创建、来源词汇和编号，不重写 [`../crm/opportunity.md`](../crm/opportunity.md) 的商机总览。

创建主路径证据强；来源枚举在模板的约束为中等、在服务端为弱；Customer Opportunity Mining 与 Enterprise Opportunity Engine 自动落库证据缺失。Schema 对编号有唯一约束，但生成算法的并发安全证据缺失。

## 业务规则（稳定ID）

1. **OS-R01** 持久化销售商机以 `business_opportunities` 为主表；Customer Mining 的“opportunity”标签和 AI insight 不是该表记录。
2. **OS-R02** 人工创建入口是 `POST /business/opportunities/create`，成功后 303 跳转商机详情。
3. **OS-R03** HTTP 表单要求 `title`；repository 对非 HTTP 调用仍以 `Untitled Opportunity` 回退。
4. **OS-R04** `customer_id=0` 在路由转换成 `NULL`，因此商机可以不绑定客户。
5. **OS-R05** 未提交来源时，路由与 repository 都回退 `sales_opportunity`。
6. **OS-R06** 来源词汇包括 `customer_opportunity`、`sales_opportunity`、`ai_opportunity`、`website_inquiry`、`exhibition_lead`、`referral`、`existing_customer_expansion`。
7. **OS-R07** 来源下拉来自常量枚举，但服务端不重新检查 posted 值是否属于枚举。
8. **OS-R08** 未显式提供编号时，系统生成 `OPP-YYYYMMDD-NNNN`。
9. **OS-R09** `NNNN` 取整张商机表当前 `COUNT(*) + 1`，不是按日期分组的当日流水。
10. **OS-R10** schema 对 `opportunity_code` 设唯一约束；生成器没有重试或锁定逻辑。
11. **OS-R11** 创建默认状态是 `open`，优先级是 `normal`，`requirement_count` 为 0。
12. **OS-R12** `salesperson` 取当前 session username；session 无用户名时回退 `demo`。
13. **OS-R13** `category` 被持久化，但当前 quick-create 不提交它，因此通常为空字符串。
14. **OS-R14** 商机中心/详情要求 `Customers.view`，创建要求 `Customers.add`，没有独立 Opportunity 权限域。
15. **OS-R15** 商机列表最多读取 100 条，按 id 倒序；KPI 是当前结果集长度，不是全库总数。
16. **OS-R16** 表缺失时中心可退化为空列表；repository 在 cursor 与 conn 可用时尝试幂等建表。
17. **OS-R17** AI 机会来源是允许的分类词，但未见 AI Engine 自动调用 `create_opportunity`。
18. **OS-R18** 虽然路由/repository 的缺省来源是 `sales_opportunity`，模板下拉未标 `selected`，首项是 `customer_opportunity`；正常浏览器提交更可能写首项而非后端缺省。
19. **OS-R19** Customer Opportunity Mining 的统计和行数据来自 customers，`opportunity_count` 为占位 0；它不查询或写入 `business_opportunities`。
20. **OS-R20** 导航修复把旧 mining 入口指向 `/business/opportunities`，该跳转不是线索转换或自动建档。

## 流程

1. 用户以 `Customers.view` 打开商机中心。
2. 页面提供标题、数字型客户 ID、来源下拉和描述。
3. 提交时以 `Customers.add` 做权限门禁。
4. 路由把 0 客户转换为未绑定，把 session username 作为 salesperson。
5. repository 计算 OPP 编号，填充 open/normal/0 等默认值。
6. 插入商机并提交。
7. 重定向详情；详情页可再创建多条需求。
8. Customer Mining 或 AI Engine 若产生线索，当前未证实会自动进入以上路径。

## 校验（强/弱/缺失）

1. **OS-V01（强/HTTP）** `title` 为 FastAPI 必填 Form，模板也有 HTML `required`。
2. **OS-V02（弱/UI）** `customer_id` 是 number 且 min=0；服务端只做整数解析。
3. **OS-V03（缺失）** 未验证非空 customer_id 指向真实、Active 或当前租户客户。
4. **OS-V04（弱/UI）** 来源下拉只展示常量词汇。
5. **OS-V05（缺失）** 服务端未校验 `source_type` 枚举，构造请求可写任意文本。
6. **OS-V06（强/DB）** `opportunity_code` 唯一约束可拒绝重复。
7. **OS-V07（缺失）** 编号计算无并发锁、碰撞重试或删除后空洞处理。
8. **OS-V08（强/权限）** 中心/详情受 Customers.view，创建受 Customers.add。
9. **OS-V09（缺失）** 未见 title 长度、纯空白、描述长度和字符清洗业务校验。
10. **OS-V10（缺失）** salesperson 不校验为有效销售员；可回退到 `demo`。
11. **OS-V11（缺失）** AI/mining insight 转持久商机没有人工确认或去重校验，因为转换路径未找到。
12. **OS-V12（弱/降级）** 表不存在时列表为空，但创建时 schema repair 是否成功没有面向用户的业务错误。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `business_opportunities.id` | 内部主键和详情路由参数 |
| `opportunity_code` | 人读编号；`OPP-日期-全表序号`，有唯一约束 |
| `customer_id` | 可空客户归属，不是创建硬门禁 |
| `title` | 商机短标题，HTTP 创建必填 |
| `description` | 自由文本背景 |
| `source_type` | 商机如何产生的分类词 |
| `category` | 可存分类；当前 quick-create 不暴露 |
| `status` | 创建默认 `open` |
| `salesperson` | 创建时 session username 快照 |
| `priority` | 创建默认 `normal` |
| `requirement_count` | 创建时为 0 的需求缓存计数 |
| `created_at` | UTC 字符串形式的创建时间 |
| `updated_at` | 创建或后续需求计数变化时间 |
| `customer_opportunity` | 客户场景识别的来源标签，不等于 mining 记录 |
| `sales_opportunity` | 默认人工销售来源 |
| `ai_opportunity` | 允许的来源词，不证明 AI 自动持久化 |
| `website_inquiry` | 网站询盘来源 |
| `exhibition_lead` | 展会线索来源 |
| `referral` | 转介绍来源 |
| `existing_customer_expansion` | 既有客户扩展来源 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| open | 人工创建默认状态，也是中心 KPI 唯一显式统计状态 |
| normal | 默认优先级，不是生命周期状态 |
| unlinked | 文档描述；数据库以 customer_id NULL 表示，不是持久状态 |
| insight | AI/Mining 推荐信息，不是 business_opportunities 状态 |
| persisted opportunity | 已写入 business_opportunities 的真实商机 |
| schema_ready | status API 只以业务需求表存在性判断的能力信号，不是单条商机状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| OS-E01 | 来源类型常量和生命周期位置 | 强（声明） | `v15/business_lifecycle/constants.py` |
| OS-E02 | 创建字段、权限、session owner 与重定向 | 强 | `v15/business_lifecycle/routes.py` |
| OS-E03 | 编号算法、默认值、插入和提交 | 强 | `v15/business_lifecycle/repository.py` |
| OS-E04 | 表字段、唯一编号和默认值 | 强 | `database/business_lifecycle_schema.py` |
| OS-E05 | quick-create 只暴露标题、客户、来源、描述 | 强 | `templates/business/opportunity_center.html` |
| OS-E06 | 详情显示来源、客户、状态与需求列表 | 强 | `templates/business/opportunity_detail.html` |
| OS-E07 | CRM 模块规格把 opportunity intelligence 放在 CRM 目的中，但未声明业务生命周期表所有权 | 中/边界 | `business_modules/crm.md` |
| OS-E08 | 既有商机知识页区分 persisted、mining 与 AI insight | 强（交叉） | `docs/knowledge/legacy-extract/crm/opportunity.md` |
| OS-E09 | Customer 模块未提供一等商机 CRUD repository | 强（缺失证据） | `apps/customer/` |
| OS-E10 | 报告把机会洞察描述为 intelligence/readiness 能力 | 中 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md`、`V15_ENTERPRISE_READINESS_REPORT.md` |
| OS-E11 | Mining 计数为占位且只取客户行 | 强 | `apps/customer/repository.py`、`apps/customer/services.py` |
| OS-E12 | 旧 mining 导航修复到持久化商机中心 | 强 | `v15/navigation/repairs.py` |

## UNKNOWN + 已查路径

1. **生产数据中是否存在自定义 `source_type` 值 UNKNOWN。** 已查路径：常量、创建路由、schema、模板；未读取生产数据库值。
2. **删除商机后 COUNT+1 是否曾与既有编号碰撞 UNKNOWN。** 已查路径：repository 编号、schema 唯一键、全局删除/归档路由。
3. **并发创建碰撞时用户看到何种错误 UNKNOWN。** 已查路径：create route、repository、异常处理和报告。
4. **未绑定客户的商机是否允许进入后续报价流程 UNKNOWN。** 已查路径：商机详情、需求创建、Quotation create 与 lifecycle workflow。
5. **`category` 的合法词汇及使用者 UNKNOWN。** 已查路径：schema、repository、商机模板、business_modules、docs/reports。
6. **AI Opportunity Engine 是否在某部署通过外部作业落库 UNKNOWN。** 已查路径：enterprise intelligence、apps/customer、business lifecycle 和报告。
7. **Customer Opportunity Mining 的 Review 动作是否应转成持久商机 UNKNOWN。** 已查路径：customer mining template/service/repository、business opportunity routes。
8. **salesperson 应绑定用户 ID、销售员 ID 还是用户名 UNKNOWN。** 已查路径：session helper、salespersons 参考、schema 与模板。
9. **商机编号是否应按租户/组织隔离 UNKNOWN。** 已查路径：schema、repository、tenant 相关字段与报告。
10. **UI 首项 `customer_opportunity` 是否是产品有意默认 UNKNOWN。** 已查路径：模板 select、routes Form default、repository default 与 i18n。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\opportunity_center.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\opportunity_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\customer_opportunity_mining.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\crm.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
