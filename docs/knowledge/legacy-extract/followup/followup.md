# 跟进（Follow-up）与 Customer360 装配 — Legacy Knowledge

**Evidence strength:** Strong（记录结构、客户聚合、计数与展示）/ Weak（校验与权限）/ Missing（状态、分派、提醒、完成闭环）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖客户附属表 `followups`、新增跟进、Customer detail/Customer360 的装配与时间线展示。

已确认的持久字段只有客户、跟进日期、内容、下一计划。以下能力均为 `UNKNOWN`：跟进状态、负责人、渠道、联系人、提醒时间、到期规则、完成时间、结果分类、附件、商机/需求/报价关联、修改/单条删除、审计字段。已查：`apps/customer/`、`templates/customer_detail.html`、`runtime/v14/legacy_support.py`、`docs/customer/`、`docs/runtime/Customer360_*`、`v15/business_lifecycle/requirement360.py`、`v15/business_lifecycle/context360.py`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| FOLLOWUP-RULE-001 | 跟进必须归属于一个 `customer_id`，记录日期、内容和下一计划 | 路由路径提供 customer id；数据库未见外键约束 | Strong |
| FOLLOWUP-RULE-002 | 输入字符串在持久化前去除首尾空白 | 空字符串仍可保存 | Strong |
| FOLLOWUP-RULE-003 | 新增后跳回该客户详情 | 无独立跟进中心 | Strong |
| FOLLOWUP-RULE-004 | 客户详情按 id 倒序读取全部跟进，并单独计算跟进总数 | 未设置分页/limit | Strong |
| FOLLOWUP-RULE-005 | Customer360 基础信息区显示 `followup_count`，Followups tab 显示日期、内容、下一计划 | 无记录时显示空态 | Strong |
| FOLLOWUP-RULE-006 | Customer360 时间线先列跟进，再列报价，再列销售订单 | 各集合内部沿各自查询顺序；没有全局时间归并排序 | Strong |
| FOLLOWUP-RULE-007 | 客户详情同时装配报价数/额、订单、收款、交付和余额；余额 = 销售订单总额 − 收款总额 | 这些是客户视图上下文，不是跟进字段 | Strong |
| FOLLOWUP-RULE-008 | Lifecycle 扩展把客户的商机和需求加入 Customer360 的 Demand tab | 跟进本身不链接商机/需求 | Strong |
| FOLLOWUP-RULE-009 | 简化 `customer_360()` helper 装配 customer、followups、quotes、sales_orders、receipts、samples | 主详情服务装配集合与此 helper 不完全相同 | Strong |
| FOLLOWUP-RULE-010 | 删除客户时，repository 先删除该客户全部跟进 | 属于级联删除实现；未见软删除/保留策略 | Strong |
| FOLLOWUP-RULE-011 | AI 可推荐 follow-up，但页面明确 AI 不静默创建报价、订单或修改客户主数据 | 未找到 AI 自动插入 followups 的证据 | Medium |
| FOLLOWUP-RULE-012 | AR Reminder 在首选 collection task 写入失败时，会回退新增一条带 Human Approved 标记的跟进 | 这是 Finance 的降级写入，不是通用跟进审批 | Strong |
| FOLLOWUP-RULE-013 | 跟进读取存在租户范围不一致：utility 路径追加 tenant filter，客户详情 repository 路径不追加；新增也不写 tenant_id | 不得推导为可靠租户隔离 | Strong |
| FOLLOWUP-RULE-014 | 跟进状态与完成转换为 `UNKNOWN` | 表无 status 字段 | Missing |
| FOLLOWUP-RULE-015 | 下一计划的提醒、到期和任务生成规则为 `UNKNOWN` | `next_plan` 仅自由文本；overdue 指标为占位 0 | Missing |
| FOLLOWUP-RULE-016 | 跟进与商机、需求、报价的直接关联规则为 `UNKNOWN` | 表无对应追溯字段 | Missing |

## 3. 流程

### 3.1 已实现流程

1. 打开客户详情 / Customer360。
2. 服务读取客户；客户不存在时返回 not found。
3. 服务按客户装配跟进、报价、订单、收款、交付、余额，以及可选的商机/需求生命周期扩展。
4. 用户在 Followups tab 输入日期、内容、下一计划并提交。
5. 系统保存后重定向回客户详情。
6. 新记录出现在跟进列表、跟进计数及 timeline 的跟进分组中。

### 3.2 Customer360 时间线装配

Legacy timeline 是展示拼接：

1. 所有跟进（查询按 id 倒序）。
2. 客户报价（按 id 倒序，有限条数）。
3. 客户销售订单（按 id 倒序，有限条数）。

它不是统一事件表，也没有跨类型按事件时间排序；跟进日期是用户文本，报价/订单展示状态但未统一事件时间语义。

### 3.3 后续计划闭环

`记录下一计划 → 提醒 → 执行 → 完成/取消 → 结果回写`：`UNKNOWN`。Legacy 只保存 `next_plan` 文本，未找到调度或状态转换。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| FOLLOWUP-VAL-001 | 路径中必须提供整数 `customer_id` | 强（HTTP 类型） | 未确认客户记录实际存在 |
| FOLLOWUP-VAL-002 | `followup_date`、`content`、`next_plan` 必填 | 缺失 | 三字段均默认空，页面也未标 required |
| FOLLOWUP-VAL-003 | 日期格式与不得早于/晚于某日 | 弱 | 浏览器使用 date input；服务端按文本保存 |
| FOLLOWUP-VAL-004 | 新增跟进权限 | 缺失 | 当前 POST 路由未调用 `has_permission`，也不接收 Request |
| FOLLOWUP-VAL-005 | 客户详情查看权限 | 缺失/不一致 | 列表有 `Customers.view`，详情路由未见相同门禁 |
| FOLLOWUP-VAL-006 | 当前用户只能为可见客户新增跟进 | 缺失 | 未见 owner 或 tenant 检查 |
| FOLLOWUP-VAL-007 | 跟进内容长度、空白、敏感数据规则 | 缺失 | 仅 trim |
| FOLLOWUP-VAL-008 | 下一计划到期、提醒、完成状态 | 缺失 | `UNKNOWN` |
| FOLLOWUP-VAL-009 | Customer360 timeline 全局时间排序 | 缺失 | 分组拼接 |
| FOLLOWUP-VAL-010 | 跟进读写租户范围一致 | 缺失 | utility 与详情 repository 的过滤策略不同，INSERT 不写 tenant_id |

## 5. 数据含义

| 实体/字段 | 业务含义 |
|---|---|
| `followups.id` | 跟进记录内部标识；同时决定倒序展示 |
| `followups.customer_id` | 所属客户 |
| `followups.followup_date` | 用户输入的跟进日期，文本存储 |
| `followups.content` | 本次沟通/跟进内容 |
| `followups.next_plan` | 后续计划自由文本；不是结构化任务 |
| `followup_count` | 按客户实时 count，用于 Customer360 摘要 |
| `customer_360()` | 简化历史装配 helper，返回客户及多类关联集合 |
| Customer detail context | 主页面装配结果：跟进、商业单据、余额、交付和生命周期扩展 |
| Timeline | 临时展示模型，不是持久化活动实体 |

未见字段：`status`、`owner_id`、`channel`、`contact_id`、`opportunity_id`、`requirement_id`、`quote_id`、`remind_at`、`completed_at`、`created_at`、`updated_at`。这些语义均为 `UNKNOWN`。

## 6. 状态词汇

跟进实体没有已确认的状态字段或枚举。

| 词汇 | 结论 |
|---|---|
| planned / due / completed / cancelled | `UNKNOWN`；未见持久化词汇 |
| overdue | `UNKNOWN`；未见到期计算 |
| next plan | 自由文本字段，不是状态 |
| customer `跟进中` | 客户状态词汇，不是跟进记录状态 |
| “Needs Follow-up” | Customer360 基于应收余额的健康标签，不是跟进状态 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\utils.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\facade.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_decision_center\ai_assistant_pages.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\database\tenant_scope.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v41_tenant_column_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\customer_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\includes\v18\customer360_first.html`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\customer\Customer360_Integration.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\customer\Customer360_Architecture.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\customer\Customer360_Object_Model.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\runtime\Customer360_Runtime_Context.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\runtime\Customer360_Runtime_Integration.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\runtime\Customer360_Runtime_Pipeline.md`
