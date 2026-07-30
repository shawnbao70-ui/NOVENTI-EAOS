# 付款条款与账期

## Scope与证据强度

本页区分报价付款条款文本、客户账期字段、标准条款库、SO 收款状态、AR 到期日、催收及供应商/PO 条款。

- **强证据：** 报价创建/复制、Zero Duplicate、DDL、SO 转换、收款、AR 和 NDE 打印路径。
- **中证据：** 客户 `payment_days`、备用 `receivables.due_date` 与供应侧字段存在，但未形成销售账期执行链。
- **弱证据：** 业务模块说明中的目标表名与独立 GFIP 分期计划，不是主商业链权威。
- **核心结论：** 报价付款文本可持久化和打印，但 Quote→SO→AR 没有形成由账期自动计算到期日的闭环。

## 业务规则

1. **PT-R01** 报价头 `payment_term` 是可空文本，是报价阶段的付款条款持久化事实。
2. **PT-R02** 无客户历史时，平台默认付款条款为 `TT 100%`。
3. **PT-R03** Zero Duplicate 按客户最近报价、品牌默认、平台默认的优先级解析商业头。
4. **PT-R04** Canonical 新建报价会将解析后的付款条款写入数据库，不只是页面预览。
5. **PT-R05** 复制报价和样品转报价会继承商业头；无来源时回退默认解析。
6. **PT-R06** 标准 `quote_terms` 条款库与报价头短文本彼此独立；默认 Payment 正文表达装运前全额 T/T。
7. **PT-R07** V18 Quote Approve 不编辑或重新解释付款条款。
8. **PT-R08** Quote 转 SO 不复制 `payment_term`；SO 只保留收款进度字段。
9. **PT-R09** SO 的 Paid/Partial/未付状态由收款记录汇总驱动。
10. **PT-R10** 运行主 AR 表 `ar_records` 没有 `due_date`，DO 形成 AR 时不按账期计算到期日。
11. **PT-R11** 客户 AR 页面余额由 SO 总额减收款总额得到，不使用 `payment_days` 推导逾期。
12. **PT-R12** 客户 `payment_days`、`credit_level`、`credit_limit` 存在于升级列，但默认解析器不读取这些字段。
13. **PT-R13** 供应商拥有付款条款和 credit days 字段；采购单也有付款条款字段。
14. **PT-R14** NDE 可把报价付款条款映射到打印文档，但到期日通常由额外上下文提供，默认空。
15. **PT-R15** 催收任务可由人工确认提醒动作生成，但不由报价账期自动触发。
16. **PT-R16** Legacy 报价新增残留路径可直接使用固定 `TT 100%`，与 canonical 历史继承链并存。

## 流程

1. 用户选择客户，前端调用默认值 API 展示最近报价或平台默认条款；该展示本身不写库。
2. 提交新增报价后，服务端再次解析默认值并写入 `quotes.payment_term`。
3. 报价详情和打印读取持久化条款；标准条款库是否合并需另行证明。
4. Approve 推进报价状态，不改付款条款。
5. 转 SO 时商业条款断开；SO 从未收状态开始。
6. 收款写入 `receipts`，回算 SO 已收、余额及 Paid/Partial。
7. DO 可形成 `ar_records` 应收，但不形成由付款天数推算的到期日。
8. AR 余额大于零时，用户可人工确认生成催收草稿/任务。
9. 供应商与 PO 的付款条款处于独立采购链，未与销售条款联动。

## 校验

1. **PT-V01** Quote Approve 行数量必须大于零。
2. **PT-V02** Quote Approve 行价格不得小于零。
3. **PT-V03** Quote Approve 必须人工确认。
4. **PT-V04** 只有 Draft 报价可 Approve。
5. **PT-V05** Approve 前至少有一个报价行。
6. **PT-V06** AR 催收要求人工确认。
7. **PT-V07** AR 余额不大于零时拒绝催收。
8. **PT-V08** 财务通用金额不得为负。
9. **PT-V09** 默认值 API 只接受 quote/quotation 实体。
10. **PT-V10** 同一 Quote 已存在 SO 时跳过重复转换。
11. **PT-V11** SO 余额不大于零时不再新增收款并标记已付。
12. **PT-V12** 未发现对付款条款格式、付款天数范围或到期日合法性的专用校验。

## 数据含义

| 数据 | 含义 |
|---|---|
| `quotes.payment_term` | 报价头付款条款短文本 |
| `quotes.validity_days` | 报价有效期，不是账期 |
| 平台默认 `payment_term` | 无历史报价时的默认建议，可在创建时持久化 |
| `customers.payment_days` | 客户账期天数预留，未驱动主 AR 到期 |
| `customers.credit_level` | 客户信用等级标签 |
| `quote_terms.term_content` | 标准法律/商业条款正文 |
| `sales_orders.payment_status` | SO 收款进度 |
| `received_amount` / `balance_amount` | SO 已收和未收金额 |
| `ar_records.ar_date` | AR 建立日期，不等于到期日 |
| `ar_records.balance` | 应收分录余额 |
| `receivables.due_date` | 备用 AR 模型到期日，非 finance 主路径 |
| `receipts.amount` | 实际收款金额 |
| `collection_tasks.due_days` | 催收任务逾期天数结构，生成链存在漂移 |
| `suppliers.payment_term` / `credit_days` | 供应商条款与账期 |
| `purchases.payment_term` | PO 付款条款 |
| `nde.payment.due_date` | 文档展示到期日，通常为空 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Draft` / `Sent` / `Negotiating` / `Won` / `Lost` | 报价生命周期 |
| `Unpaid` / `Partial` / `Paid` | SO 收款进度 |
| `Open` / `Closed` | AR/备用应收开放或关闭语境 |
| `Pending` | 催收任务待处理 |
| `pending` / `paid` | 独立 GFIP 分期计划状态 |
| `Healthy Customer` / `Needs Follow-up` / `Credit Watch` | 余额启发式健康标签，不是账龄状态 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | 报价付款条款有持久化列和默认链 | 强 | `runtime/v14/legacy_support.py`、`v15/ux/master_defaults.py` |
| E2 | Zero Duplicate 门禁验证最近报价继承 | 强 | `scripts/v18_p6_zero_duplicate_gate.py` |
| E3 | Canonical 新建报价将条款写库 | 强 | `apps/quotation/router.py`、`apps/quotation/services.py` |
| E4 | NDE 映射报价付款条款 | 强 | `document/nde_engine.py` |
| E5 | 转 SO 不传播付款条款 | 强 | `apps/sales/services.py`、`apps/sales/repository.py` |
| E6 | `ar_records` 无 due date | 强 | `runtime/v14/legacy_support.py`、`apps/finance/services.py` |
| E7 | 客户 payment days 未被默认解析读取 | 中 | `runtime/v14/legacy_support.py`、`v15/ux/master_defaults.py` |
| E8 | 标准付款条款库与头字段分离 | 强 | `runtime/v14/legacy_support.py` |
| E9 | 默认值 strip 标示为只读复核 | 强 | `templates/includes/v18/master_defaults_strip.html` |
| E10 | Customs Center 无付款账期规则 | 强（缺失证据） | `apps/customs_center/` |
| E11 | 模块文档目标表名与运行 AR 表不同 | 中 | `business_modules/finance.md`、`apps/finance/repository.py` |
| E12 | Legacy 新增路径固定 TT 100% | 强 | `apps/quotation/quote_pages.py` |

## UNKNOWN

1. **已创建报价的付款条款编辑入口 UNKNOWN。** 已查 `apps/quotation/`、`templates/quote_*.html` 及更新语句。
2. **客户 `payment_days` 的维护 UI/API UNKNOWN。** 已查 `apps/customer/` 和模板字段。
3. **payment days 驱动 AR 到期日的规则 UNKNOWN/未实现。** 已查 `apps/finance/`、Legacy DDL。
4. **正式 30/60/90 账龄分桶 UNKNOWN。** 已查 Finance 应用、模板和 reports。
5. **标准 Payment 条款自动并入 NDE 正文 UNKNOWN。** 已查 NDE 与报价打印服务。
6. **collection_tasks 的生产列模型 UNKNOWN。** 已查 DDL、Finance 服务和测试写入，发现字段漂移。
7. **GFIP 分期计划与 canonical SO/AR 集成 UNKNOWN。** 已查 `v15/gfip/`、Sales、Finance。
8. **采购单付款条款的实际读写入口 UNKNOWN。** 已查 `apps/procurement/`。
9. **双新增报价路由的运行优先级 UNKNOWN。** 已查 quotation router、quote_pages 和挂载逻辑；需运行路由表。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\v18_p6_zero_duplicate_gate.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\payment_intel.py`
