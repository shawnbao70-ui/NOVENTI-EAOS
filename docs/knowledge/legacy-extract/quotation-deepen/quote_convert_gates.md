# 报价转销售订单门槛与双路径差异

**Evidence strength:** Strong for both implementations; strong negative for Sent/Won prerequisite  
**Sales cross-reference:** [`../sales/sales_order.md`](../sales/sales_order.md)

## Scope 与关键结论

转 SO 的活动 Sales 服务硬门槛只有“报价存在”和“该报价尚无销售订单”。UI 另有 `Sales Orders.add` 可见性和浏览器确认，但 `/convert_so/{quote_id}` 本身是 GET 写操作，路由未显示权限参数。服务不要求报价为 Sent、Won 或中心 Approved，也不要求报价有行；空报价可建立空 SO，之后才在 SO Approve 被“必须有行”拦截。

代码中同时保留 Sales 主路径与 Quotation 残留路径。Enterprise bootstrap 先挂载业务 page routers，再用路径过滤挂载 v14 residual，因此同名冲突下由 Sales 主路径生效，Quotation 实现被跳过。两者复制相同商业快照并写 `已确认`，但只有 Sales 主路径 best-effort 建立 lifecycle link。订单后续含义以 [`../sales/sales_order.md`](../sales/sales_order.md) 为准。

## 业务规则

| ID | 规则 |
|---|---|
| QCG-R01 | 转单先按 quote id 读取报价；不存在则返回报价列表。 |
| QCG-R02 | 已存在任一 `sales_orders.quote_id=quote_id` 时不重复创建，返回订单列表。 |
| QCG-R03 | SO 编号按 `SO` + 四位补零 quote id 生成，不使用独立序列。 |
| QCG-R04 | SO 头复制报价 id、客户、业务员、报价日期和总额。 |
| QCG-R05 | 初始 SO 状态、收款状态来自 locale 翻译值，可能把显示文本写入数据库。 |
| QCG-R06 | 报价行的产品、数量、单价、金额逐行复制到 SO 行；成本、毛利率不复制。 |
| QCG-R07 | 空报价也能建立 SO 头；复制循环为空不会回滚头。 |
| QCG-R08 | 转单成功后报价状态写中文 `已确认`，而非 Won 或 Sent。 |
| QCG-R09 | 转单不校验报价是 Draft/Sent/Negotiating/Won/Lost 中哪一状态。 |
| QCG-R10 | 转单不依赖 Quote Approve 或 Approval Center 的 Approved 记录。 |
| QCG-R11 | 转单 UI 和新建 SO 表单最终都导向 `/convert_so/{quote_id}`；表单提交的 salesperson 选择被忽略。 |
| QCG-R12 | Sales 主路径尝试计算佣金并写 Pending 台账；失败被吞掉，不阻断 SO 创建。 |
| QCG-R13 | Sales 主路径尝试 `link_sales_order_from_quote`；失败被吞掉，不阻断转单。 |
| QCG-R14 | Quotation 残留路径未观察到 lifecycle link，形成相同商业结果但不同追踪结果。 |
| QCG-R15 | 转单不是 SO 批准：新 SO 后续仍需独立 Human Approved 才进入 Open。 |
| QCG-R16 | 建立 SO 不扣库存、不建交付、不记应收；这些是后续独立动作。 |
| QCG-R17 | 详情/列表 Convert CTA 的浏览器 confirm 是人工提示，不是可审计服务端确认令牌。 |

## 当前硬门与缺失门

| Gate | 当前结果 | 说明 |
|---|---|---|
| 报价存在 | Hard | 不存在即返回 |
| 未有源报价 SO | Hard | 查询后返回；数据库唯一约束未证实 |
| Sales Orders add 权限 | UI/入口级 | 列表 CTA 可见性有检查；convert 路由本身未见 |
| 浏览器确认 | UI | GET 链接 confirm |
| 报价已 Sent/Won | Missing | Draft、Lost 等也可转 |
| 报价有行 | Missing | 可产生空 SO |
| 客户有效/未冻结 | Missing | 未见客户状态 gate |
| 报价未过期 | Missing | 未使用 validity |
| 价格/币种/汇率复核 | Missing | 直接复制快照 |
| 中心审批 Approved | Missing | 无读取 |
| 并发唯一性 | Weak | 先查后插，未见事务唯一约束 |

## 双路径差异

| 维度 | Sales 主路径 | Quotation 残留路径 |
|---|---|---|
| 实现 | `apps/sales/services.py` + repository | `apps/quotation/quote_pages.py` |
| 路由 | `/convert_so/{quote_id}` | 同一路由签名 |
| 报价存在检查 | 有 | 有 |
| 重复 SO 检查 | 有 | 有 |
| 复制头/行 | 有 | 有 |
| 写 `已确认` | 有 | 有 |
| 佣金 | 调用 best-effort helper | 存在内联等价逻辑的证据，细节以部署 owner 为准 |
| lifecycle link | 有，异常吞掉 | 未观察到 |
| 权限/确认 | 路由无显式 request gate；UI 提示 | Enterprise bootstrap 中因同名路径被 residual filter 跳过 |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QCG-V01 | quote id 对应报价必须存在 | Hard |
| QCG-V02 | 同 quote id 不得已有 SO | Hard query guard |
| QCG-V03 | 数据库必须唯一约束 `sales_orders.quote_id` | UNKNOWN |
| QCG-V04 | 报价必须至少有一行 | Missing |
| QCG-V05 | 报价必须 Sent 或 Won | Missing |
| QCG-V06 | 报价不得 Lost/过期 | Missing |
| QCG-V07 | 调用者必须有 Sales Orders.add | UI 可见性有，服务端路由缺口 |
| QCG-V08 | Convert 必须使用 POST + CSRF/确认令牌 | Missing；当前 GET |
| QCG-V09 | 头总额必须等于行金额合计 | Missing at convert；直接复制 |
| QCG-V10 | 所有行产品仍有效 | Missing |
| QCG-V11 | 空 SO 创建失败时必须回滚 | Missing/未见事务边界 |
| QCG-V12 | 生命周期链接失败必须回滚或进入补偿队列 | Missing；异常吞掉 |
| QCG-V13 | SO 编号必须在并发下唯一 | UNKNOWN |
| QCG-V14 | 多租户读写必须一致限定 | UNKNOWN；查询文本未见局部 tenant 条件 |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sales_orders.quote_id` | SO 对源报价的直接引用，也是重复转单查询键 |
| `so_no` | `SO{quote_id:04d}` 派生业务号 |
| `customer_id` | 从报价头复制的 sold-to |
| `salesperson_id` | 从报价复制；新建 SO 表单选择值未生效 |
| `order_date` | 复制报价日期，不是实际转换时间 |
| `total_amount` | 复制报价头总额，不在转单时按行重算 |
| SO `status` | locale `pending_delivery` 的持久化结果 |
| `payment_status` | locale `uncollected` 的持久化结果 |
| `sales_order_items.product_id` | 报价行产品引用快照 |
| `sales_order_items.qty` | 转单时复制的报价数量 |
| `sales_order_items.price` | 转单时复制的报价单位价 |
| `sales_order_items.amount` | 转单时复制的报价行金额 |
| 报价 `status='已确认'` | 已发生转单的中文写回标志 |
| `tc_ledger` Pending | 转单触发的佣金待处理记录 |
| lifecycle quote→SO link | 业务链追踪关系；主路径 best-effort |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QCG-E01 | 报价存在与重复 SO 两道硬校验 | 强 | `apps/sales/services.py`、`repository.py` |
| QCG-E02 | SO 编号和头字段复制 | 强 | `apps/sales/services.py` |
| QCG-E03 | 报价行四字段复制 | 强 | `apps/sales/services.py`、`repository.py` |
| QCG-E04 | 报价状态写 `已确认` | 强 | `apps/sales/repository.py` |
| QCG-E05 | 生命周期链接为 best-effort | 强 | `apps/sales/services.py` |
| QCG-E06 | 同名残留转单实现 | 强 | `apps/quotation/quote_pages.py` |
| QCG-E07 | UI 权限与 confirm | 强 | `templates/quotes.html`、`quote_dashboard.html`、`quote_detail.html` |
| QCG-E08 | convert 路由是 GET 且无 request 参数 | 强 | `apps/sales/router.py` |
| QCG-E09 | 新建 SO 表单忽略 salesperson 并重定向转换 | 强 | `apps/sales/router.py`、`services.py` |
| QCG-E10 | Sales validator 为空 | 强 | `apps/sales/validator.py` |
| QCG-E11 | SO 后续批准/交付/收款分离 | 强 | `apps/sales/services.py`、`templates/so_approve.html` |
| QCG-E12 | Chain extraction 与 bootstrap 顺序确认 Sales owner | 强/中 | `bootstrap/enterprise_cutover.py`、`bootstrap/v14_residual.py`、`docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` |

## UNKNOWN + 已查路径

1. **不经 Enterprise bootstrap 的替代启动方式是否仍会装载残留 `/convert_so` UNKNOWN。** 已查：`apps/sales/router.py`、`apps/quotation/quote_pages.py`、`bootstrap/enterprise_cutover.py`、`bootstrap/v14_residual.py`、Volume009 报告；标准 Enterprise 挂载已确认 Sales 优先。
2. **`sales_orders.quote_id` 是否有数据库唯一约束 UNKNOWN。** 已查：`apps/sales/repository.py`、`runtime/v14/legacy_support.py`、数据库升级脚本。
3. **转单失败的事务回滚范围 UNKNOWN。** 已查：Sales/Quotation 两实现、repository commit 点；未见显式原子事务说明。
4. **Draft/Lost 报价可转单是有意政策还是缺陷 UNKNOWN。** 已查：`business_modules/quotation.md`、Sales/Quotation 服务、V18/A013 报告。
5. **locale 变化后 SO 初始状态的跨语言稳定性 UNKNOWN。** 已查：`apps/sales/services.py`、`locales/en.json`、`zh_CN.json`、`zh_TW.json`。
6. **客户冻结、信用额度、制裁或过期报价应否阻断 UNKNOWN。** 已查：`apps/customer/`、`apps/quotation/`、`apps/sales/`、商业条款知识页。
7. **佣金失败后的补偿与对账 UNKNOWN。** 已查：`apps/sales/services.py`、`tc_ledger` 引用、`docs/reports/`。

## 交叉引用

- Sales 权威及转后流程：[`../sales/sales_order.md`](../sales/sales_order.md)
- 报价审批分离：[`quote_approve.md`](quote_approve.md)
- 中英状态影响：[`quote_lifecycle.md`](quote_lifecycle.md)
- 价格快照来源：[`quote_lines_pricing.md`](quote_lines_pricing.md)
