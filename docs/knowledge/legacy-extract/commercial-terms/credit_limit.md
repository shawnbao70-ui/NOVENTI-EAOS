# 信用额度与放账控制

## Scope与证据强度

本页覆盖客户信用额度、已用额度、AR 余额、超额警告/阻断、审批、客户状态、多租户及多币种。

- **强证据：** 客户与财务查询、Quote/SO Approve、转 SO、收款、DDL 和页面提示。
- **中证据：** 客户/分销商额度字段和协作流水线声明存在，但未接入商业链。
- **明确缺失：** 没有 `credit_used` 数据模型，也没有“现有敞口 + 新单 > 信用额度”的服务端阻断。
- **核心结论：** 当前是“余额启发式警告 + 双轨 AR”，不是完整放账控制。

## 业务规则

1. **CL-R01** 客户未结余额按全部 SO 总额减全部收款计算。
2. **CL-R02** 客户 `credit_limit` 是后加升级列，未证明有业务回填或维护入口。
3. **CL-R03** 运行查询与审批未读取或比较 `credit_limit`。
4. **CL-R04** 系统不存在 `credit_used` 字段或函数；最接近概念是计算余额。
5. **CL-R05** AR360 按余额绝对阈值分为 High、Medium、Low 风险带。
6. **CL-R06** 客户详情按余额展示 Alert 和 A/B/C/D 档，并明确不是征信评分。
7. **CL-R07** Quote Approve 校验行项、价格、库存提示和人工确认，不校验信用。
8. **CL-R08** Quote 转 SO 不检查客户余额或额度。
9. **CL-R09** SO Approve 校验阶段、行项和人工确认，不校验信用。
10. **CL-R10** 收款按 SO 余额写入，币种固定为 USD；余额已清时只更新状态。
11. **CL-R11** DO 形成 `ar_records` 后产生另一套应收分录，初始为 Unpaid。
12. **CL-R12** 财务总览和客户 AR360 主要使用 SO 减收款算法。
13. **CL-R13** Treasury/Receivable Center 的部分 KPI 使用 `ar_records.balance`，与 SO 减收款可能不一致。
14. **CL-R14** 分销商也有独立 credit limit 和 balance 字段，但未与客户 SO 链联动。
15. **CL-R15** 客户状态描述 CRM 跟进阶段，不是信用冻结或止付状态。
16. **CL-R16** V15 协作字典虽声明 `validate_credit_and_pricing`，未发现对应执行函数。
17. **CL-R17** 余额汇总未做币种折算，不能作为可靠的跨币种已用额度。
18. **CL-R18** AR 查询未证明按 tenant_id 过滤，不能视为多租户安全的信用敞口。

## 流程

1. 客户记录可拥有额度、等级和付款天数字段，但报价创建不读取额度。
2. Quote 经人工确认成为 Sent；库存可提示，但信用不参与门控。
3. Quote 转 SO、SO Approve 到 Open 均不执行放账比较。
4. 发货后可形成 `ar_records`；同时 AR360 继续按 SO 减收款计算余额。
5. 收款冲减 SO 余额并更新付款状态。
6. 客户页和 AR 页按余额阈值显示软警告。
7. 用户可对有余额客户人工确认生成催收提醒。

整个链路没有信用例外申请、超额审批、冻结/解冻或可用额度重算节点。

## 校验

1. **CL-V01** Quote Approve 数量必须大于零。
2. **CL-V02** Quote Approve 价格不得小于零。
3. **CL-V03** 只有 Draft Quote 可 Approve。
4. **CL-V04** Quote Approve 前必须有行项。
5. **CL-V05** Quote Approve 必须人工确认。
6. **CL-V06** SO Approve 只允许 pending stage。
7. **CL-V07** SO Approve 必须有行项并人工确认。
8. **CL-V08** SO 已无余额时不新增收款。
9. **CL-V09** 财务金额不得为负。
10. **CL-V10** AR 催收要求余额大于零。
11. **CL-V11** AR 催收要求人工确认。
12. **CL-V12** `credit_limit` 超额校验缺失。

## 数据含义

| 数据 | 含义 |
|---|---|
| `customers.credit_limit` | 设计上的客户信用额度，运行主链未使用 |
| `customers.credit_level` | 信用等级标签，不是硬门控 |
| `customers.payment_days` | 账期天数预留 |
| `customers.customer_status` | CRM 跟进阶段，不是信用状态 |
| 计算 `balance` | SO 总额减收款，是当前敞口代理指标 |
| `sales_orders.total_amount` | 余额计算分子 |
| `receipts.amount` | 余额计算扣减项 |
| `ar_records.amount` / `balance` | DO/来源级应收分录 |
| `ar_records.status` | 应收分录开放程度 |
| `distributors.credit_limit` / `balance` | 渠道商独立额度和余额 |
| `quotes.currency` | 报价币种，不参与额度折算 |
| `receipts.currency` | 收款币种，当前创建路径固定 USD |
| `collection_tasks.balance` | 催收时余额快照 |
| `credit_score` | AI 页面占位/演示分，不是放账计算 |
| `tenant_id` | 租户列；AR 聚合未证明使用 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Credit Watch` / `risk` | 高余额启发式警告 |
| `Needs Follow-up` / `watch` | 中余额启发式警告 |
| `Healthy Customer` | 低余额启发式标签 |
| `High` / `Medium` / `Low` | AR 页面风险带 |
| `Unpaid` / `Closed` | AR 分录状态 |
| `Paid` / `Partial` | SO 收款状态 |
| `clear` / `partial` / `unpaid` | 客户信用页回款展示状态 |
| `Human Approved` | 人工确认动作，不等于信用批准 |
| `开发中` / `跟进中` / `已成交` / `长期客户` | CRM 生命周期，不是信用冻结状态 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | 客户余额按 SO 减收款计算 | 强 | `apps/customer/repository.py` |
| E2 | Finance AR 列表使用相同算法 | 强 | `apps/finance/repository.py` |
| E3 | 客户额度仅见于升级 DDL | 强 | `runtime/v14/legacy_support.py` |
| E4 | 全库未见额度比较运算 | 强（缺失证据） | `apps/`、`runtime/`、`templates/` |
| E5 | Quote Approve 无信用门 | 强 | `apps/quotation/services.py` |
| E6 | 转 SO 无信用门 | 强 | `apps/sales/services.py` |
| E7 | AR 页面明确非征信/非日龄 | 强 | `templates/ar.html`、`locales/zh_CN.json` |
| E8 | `ar_records` 是并行应收模型 | 强 | `runtime/v14/legacy_support.py`、`apps/finance/services.py` |
| E9 | 客户编辑页没有额度输入 | 强 | `templates/edit_customer.html` |
| E10 | Customs Center 无信用规则 | 强（缺失证据） | `apps/customs_center/` |
| E11 | 分销商额度只在独立详情展示 | 中 | `templates/distributor_detail.html` |
| E12 | 协作流水线仅声明校验步骤 | 中 | `v15/workforce/collaboration.py` |

## UNKNOWN

1. **生产客户额度是否有非零数据 UNKNOWN。** 已查 DDL、客户编辑模板、Customer repository 写入。
2. **部分环境是否存在 `customers.balance` 实列 UNKNOWN。** 已查 base/upgrade DDL；Legacy 风险 SQL 与主模型不一致。
3. **两套 AR 是否应定期对账 UNKNOWN。** 已查 Finance 服务、Receivable Center，未见 reconcile 作业。
4. **payment days 是否驱动账龄 UNKNOWN。** 已查 DDL、Finance 与文档组件规范。
5. **`validate_credit_and_pricing` 的隐藏实现 UNKNOWN。** 已查协作字典及全库函数引用。
6. **横向审批是否支持信用例外 UNKNOWN。** 已查 `business_modules/approval.md` 与 approval capability。
7. **多租户 AR 的目标隔离规则 UNKNOWN。** 已查租户 schema 与 Finance SQL。
8. **多币种余额折算规则 UNKNOWN。** 已查 Quote、Receipt 和余额聚合路径。
9. **催收任务完整生产生成链 UNKNOWN。** 已查 DDL、Finance 服务和页面路径。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ui_center\domain_dashboards.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v41_tenant_column_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\workforce\collaboration.py`
- `H:\Workspace\EZAM_CRM - 9.0\locales\zh_CN.json`
