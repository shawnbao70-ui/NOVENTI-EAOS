# 报价转销售订单（Quote → SO Convert）— Legacy Knowledge

**Evidence strength:** Strong for active Sales conversion; mixed for duplicate conversion surfaces and lifecycle hook  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述报价转换为销售订单的活动规则、一报价一单保护、报价行复制、报价状态回写、生命周期链接和佣金钩子。销售订单总体语义交叉引用 `../sales/sales_order.md`，此处只深化转换边界。

活动 `apps/sales` 路径证据强；Quotation 侧存在平行业务入口，具体路由优先级与是否仍可达需按运行挂载判定；V15 lifecycle 与佣金写入均为 best-effort，不能当作事务成功条件。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| SC-R1 | 转换以现有 quote ID 为输入 | 不支持无报价直接建立完整 SO |
| SC-R2 | 活动 Sales 路径先查 `sales_orders.quote_id` | 已有记录则返回订单列表 |
| SC-R3 | “一报价一单”是应用层先查后写 | 未证实数据库唯一约束或并发原子性 |
| SC-R4 | SO 编号由报价 ID 派生为 `SO` 加四位补零 | 不是独立序列 |
| SC-R5 | SO 复制报价的客户、业务员、报价日期和总额 | 属于转换时快照 |
| SC-R6 | SO 初始履约状态使用 `pending_delivery` 翻译值 | 持久值可能受 locale 影响 |
| SC-R7 | SO 初始收款状态使用 `uncollected` 翻译值 | 后续 Finance 写 `Paid/Partial` |
| SC-R8 | 所有 quote items 复制为 SO items | 产品、数量、价格、金额被快照 |
| SC-R9 | 空报价也可完成转换 | 行项目门槛延后到 V18 SO Approve |
| SC-R10 | 转换后报价状态直接写为中文 `已确认` | 与 Draft/Sent/Won 词汇并行 |
| SC-R11 | 服务端未要求报价为 Sent、Won 或 Human Approved | 转换门与 Quote Approve 相互独立 |
| SC-R12 | 转换创建 Pending 佣金台账项 | 基数为 SO 总额，费率取业务员等级 |
| SC-R13 | 没有业务员时不创建佣金项 | SO 本身仍可创建 |
| SC-R14 | 无等级或费率时可创建零费率佣金项 | 零金额仍可能成为 Pending 台账 |
| SC-R15 | 佣金钩子异常被吞掉 | SO 转换不会因佣金失败回滚 |
| SC-R16 | 生命周期 Quote→SO 链接同样 best-effort | 链接失败不影响转换结果 |
| SC-R17 | 新建 SO 表单中的 salesperson 选择不覆盖报价业务员 | POST 最终只按 quote ID 转换 |
| SC-R18 | 转换入口是 GET 且 router 本身未见 add 权限检查 | UI 权限不等于服务端写门 |
| SC-R19 | SO header、佣金、行项目、报价状态并非显式单事务编排 | 中途异常可能留下部分事实 |
| SC-R20 | EAOS 不得把成功返回等同于佣金和 lifecycle 均成功 | 两个钩子允许静默失败 |
| SC-R21 | 转换不写 `quote_versions`，也不把 `quotes.version` 冻结到 SO | SO 只保留来源 quote ID 与商业字段子集 |
| SC-R22 | 报价 currency、exchange rate、payment term、delivery term 和 remark 未复制到 SO header | SO 不具备完整商业头快照 |
| SC-R23 | Canonical Sales router 先于 V14 residual 挂载 | 同 method/path 的遗留转换副本通常被去重 |

---

## 3. Process

### 3.1 活动 Sales 转换

1. 接收 quote ID，读取报价；不存在则返回报价列表。
2. 按 `quote_id` 查已有 SO；命中则返回 SO 列表。
3. 创建 SO header，复制客户、业务员、日期、金额及初始状态。
4. 尝试按业务员等级计算并写入 Pending 佣金。
5. 复制报价行到 SO 行。
6. 将报价状态写为 `已确认`。
7. 尝试写 Quote→SO lifecycle 链接，随后返回 SO 列表。

### 3.2 新建 SO 表面

1. 页面列出全部报价和 Active 业务员。
2. POST 接收 quote ID 与 salesperson ID。
3. salesperson ID 未进入转换，页面重定向到 quote-based convert。

### 3.3 失败边界

报价不存在和已转换有显式分支；佣金与 lifecycle 失败被静默忽略。未观察到覆盖 header、台账、行复制与报价状态的统一补偿流程。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| SC-V1 | 报价必须存在 | Hard | 不存在不创建 SO |
| SC-V2 | 同 quote ID 不得已有 SO | Hard at application read | 先查后写 |
| SC-V3 | 数据库必须唯一约束 `quote_id` | UNKNOWN / not proven | 并发保护不足 |
| SC-V4 | 报价必须为 Sent/Won/Approved | Missing | 服务端不检查 |
| SC-V5 | 报价必须至少一行 | Missing at convert | 空 SO 可创建 |
| SC-V6 | 行数量必须大于零 | Missing at convert | 仅后续 approve 看“有行” |
| SC-V7 | 行价格/金额必须非负且重算一致 | Missing at convert | 原样复制 |
| SC-V8 | header 总额必须等于行金额合计 | Missing at convert | 直接复制报价 header |
| SC-V9 | 转换调用者必须有 Sales Orders add | Missing at route | GET 入口无 gate |
| SC-V10 | 报价归属必须与当前用户一致 | Missing at convert | 未见对象级 owner 复核 |
| SC-V11 | 佣金率必须有效 | Weak | 无等级视为零 |
| SC-V12 | SO、行、佣金、报价状态必须原子提交 | Missing | 多步骤和静默异常 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `quotes.id` | 转换输入及 SO 编号派生源 |
| `sales_orders.quote_id` | 来源报价弱业务键，也是应用层防重键 |
| `sales_orders.so_no` | `SO` + quote ID 补零形成的显示编号 |
| `sales_orders.customer_id` | 从报价复制的 sold-to |
| `sales_orders.salesperson_id` | 从报价复制的订单归属与佣金主体 |
| `sales_orders.order_date` | 复制 quote date，不是转换执行时间 |
| `sales_orders.total_amount` | 报价 header 总额快照 |
| `sales_orders.status` | 初始履约标签，可能是翻译结果 |
| `sales_orders.payment_status` | 初始收款标签，后由 Finance 驱动 |
| `sales_order_items` | quote items 的转换时商业快照 |
| `quote_versions` | 报价版本表；转换不写入 |
| `quotes.version` | 报价版本文本；转换不复制到 SO |
| `quotes.status='已确认'` | 转换后的中文确认标签，不等同统一 Won |
| `sales_levels.commission_rate` | 业务员等级上的百分比 |
| `tc_ledger.source_type` | 转换佣金来源类型 `Sales Order` |
| `tc_ledger.source_no` | SO 编号，非 SO 外键 |
| `tc_ledger.status='Pending'` | 待结算佣金事实 |
| lifecycle link | 可选 Quote→SO 追踪，不是转换提交凭证 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Draft / Sent / Won | Quotation 主状态族；转换未强制 |
| `已确认` | 转换后报价写值，与英文状态并行 |
| `pending_delivery` / 待发货 | SO 转换初始履约状态 |
| `uncollected` / Unpaid | SO 初始收款语义 |
| Pending | `tc_ledger` 佣金待结算状态 |
| Converted | 由 `sales_orders.quote_id` 存在推导，不是独立状态 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| `sales_orders.quote_id` 在生产 schema 是否有唯一索引 | runtime/v14 schema、database migrations、sales repository |
| 两个转换实现的实际优先级与可达性 | apps/sales、apps/quotation、bootstrap/runtime route reports |
| 并发点击转换是否会生成两个 SO | sales service/repository、schema/index、transaction searches |
| 佣金失败是否有离线补录或告警 | sales/finance services、tc_ledger templates、reports |
| quote `已确认` 与 Sent/Won 的正式映射 | quotation services/templates、i18n、business reports |
| 生命周期链接失败是否有修复作业 | v15/business_lifecycle、scheduler、audit reports |
| 报价商业头未复制到 SO 是有意边界还是缺口 | quotation and sales schemas/services/templates；已证实当前不复制 |
| 转换后修改报价是否影响 SO | quotation update/copy/history 与 sales read paths |
| `new_sales_order` 的 salesperson 字段为何保留 | sales template/router/service、UX reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 活动转换、佣金钩子、行复制、lifecycle hook |
| `apps/sales/repository.py` | SO 防重查询、header/item/佣金持久化 |
| `apps/sales/router.py` | GET 转换及新建 SO 路由权限边界 |
| `apps/sales/validator.py` | 空 validator 诚实缺口 |
| `apps/sales/v14_residual.py` | 残留销售与佣金表面 |
| `apps/quotation/services.py` | Quote Approve 与转换前状态边界 |
| `apps/quotation/quote_pages.py` | 平行转换实现 |
| `apps/quotation/repository.py` | 报价 header/items 数据来源 |
| `templates/new_sales_order.html` | quote 与 salesperson 选择表面 |
| `templates/quote_detail.html` | Convert UI 和报价状态表面 |
| `business_modules/sales.md` | Sales 域所有权 |
| `business_modules/quotation.md` | Quotation 域边界 |
| `v15/business_lifecycle/workflow.py` | Quote→SO 链接 |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | SO 活动事实审计 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | 报价销售链提取证据 |
| `docs/knowledge/legacy-extract/sales/sales_order.md` | 当前 EAOS 交叉引用，不作为 Legacy 新证据 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
