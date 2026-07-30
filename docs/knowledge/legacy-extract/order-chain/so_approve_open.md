# 销售订单批准并开启（SO Approve → Open）— Legacy Knowledge

**Evidence strength:** Strong for V18 Type A service and template; weak for a unified SO state machine  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述 V18 Type A SO Approve 表面如何把 pending-stage 订单变为 `Open`，以及 Human Approved、行项目门槛和权限边界。它不把 Approve 解释为建 DO、扣库存、记 AR 或收款。

Approve GET/POST、状态归类和服务端三项门槛证据强；Legacy 同时允许其他状态通过通用 GET 路由直接覆盖，因此全局状态机证据弱。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| SA-R1 | V18 SO Approve 是独立于 Quote→SO Convert 的第二个人工门 | 转换不会自动 Open |
| SA-R2 | Approve 的唯一业务写结果是 SO `status='Open'` | 不建 DO、不扣库存、不记 AR |
| SA-R3 | 当前状态必须归类为 pending | open/cancelled/shipped/complete 不可批准 |
| SA-R4 | 未识别状态默认归类为 pending | 非规范状态可能意外获得批准资格 |
| SA-R5 | SO 必须至少存在一行 | 空 SO 被服务器拒绝 |
| SA-R6 | POST 必须携带 `human_confirm='1'` | UI Type A 确认不是纯装饰 |
| SA-R7 | POST action 只有 approve 执行状态变化 | cancel/draft/未知 action 不 Open |
| SA-R8 | Approve GET 要 Sales Orders view | 只生成审阅上下文 |
| SA-R9 | Approve POST 要 Sales Orders edit | 写门与查看门分开 |
| SA-R10 | 通用状态入口传 `Open` 时重定向 Approve | Open 不能从该快捷入口直接写 |
| SA-R11 | 其他状态仍可由 `so_status` GET 直接写 | 取消、已发货、已完成绕过 Type A |
| SA-R12 | Approve 页展示客户、SO、行数、总额与当前状态 | 作为人工审阅摘要 |
| SA-R13 | `can_approve` 同时要求 pending 与非空行 | 控制 UI action 显示 |
| SA-R14 | 行门槛只验证“存在” | 不验证 qty、price、amount、产品有效性 |
| SA-R15 | total_amount 可为零仍可批准 | 服务端无正金额门 |
| SA-R16 | actor 被接收但只保留给未来日志桥 | 未观察到批准审计写入 |
| SA-R17 | Approve 不检查报价状态或 Quote Human Approved | 上游门不构成本门前置 |
| SA-R18 | Approve 不检查库存可用量 | 库存门在后续 DO Ship |
| SA-R19 | Approve 不检查付款、信用、客户冻结或币种 | Open 是履约准备标签而非信用放行 |
| SA-R20 | EAOS 不得把 AI summary/recommendation 视为授权 | 唯一授权来自权限与人类确认 |
| SA-R21 | `Delivery Created` 未被显式归类，因 catch-all 仍属于 pending | 已建 DO 的 SO 可再次 Approve 回写为 Open |
| SA-R22 | SO Approve 未接 `approval_requests`/Approval Center | Type A Human Approved 是独立门控 |
| SA-R23 | Canonical Sales 页面先挂载，V14 residual 对同 method/path 后挂载去重 | Approve 权威实现不在 residual |

---

## 3. Process

### 3.1 Approve 页面

1. 校验 Sales Orders view。
2. 读取 SO header 与行；不存在则 404。
3. 将当前 status 归入 pending/open/cancelled/shipped/complete。
4. 构建 Type A 审阅摘要和 `can_approve`。
5. 无行或非 pending 时隐藏批准动作并显示提示。

### 3.2 Human Approved POST

1. 校验 Sales Orders edit。
2. 读取 action；cancel 返回详情，draft 留在审批页，其他非 approve 无写入。
3. 重新读取 SO 当前状态并要求 pending。
4. 重新读取订单行并要求至少一行。
5. 要求 `human_confirm='1'`。
6. 将状态写为 `Open` 并返回详情。

### 3.3 相邻动作

Open 之后建 DO 仍是独立 GET 动作；发货时才校验库存并扣减。直接把状态写成已发货/已完成只是标签写入，不等于履约过账。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| SA-V1 | SO 必须存在 | Hard | GET 404，POST 返回 not_found |
| SA-V2 | GET 需要 Sales Orders view | Hard route gate | |
| SA-V3 | POST 需要 Sales Orders edit | Hard route gate | |
| SA-V4 | 当前 stage 必须 pending | Hard | 防重复 Open |
| SA-V5 | 必须至少一行 | Hard | 仅 count 门 |
| SA-V6 | 必须 Human Confirm | Hard | 值必须为 `1` |
| SA-V7 | 行 qty 必须大于零 | Missing | 未检查 |
| SA-V8 | 行 price/amount 必须有效 | Missing | 未检查 |
| SA-V9 | SO 总额必须大于零且等于行合计 | Missing | 零金额可通过 |
| SA-V10 | 报价必须已批准 | Missing | 无上游 gate |
| SA-V11 | 客户/信用必须可交易 | Missing | 无冻结或 credit hold |
| SA-V12 | 库存必须足够 | Deferred | DO Ship 才检查 |
| SA-V13 | actor 与批准时间必须审计 | Missing | actor 未持久化 |
| SA-V14 | 所有状态变化必须走状态机 | Missing | 通用 GET 可直接写其他值 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.status` | 混合语言的履约/流程标签 |
| stage `pending` | Pending、待发货、空值及未识别值的归类 |
| stage `open` | 状态字符串 `Open` |
| stage `cancelled` | 中文已取消或含 cancel 的值 |
| stage `shipped` | 已发货、Shipped |
| stage `complete` | 已完成、Completed 或含 complete |
| `sales_order_items` existence | V18 批准的最低行门槛 |
| `can_approve` | UI 派生布尔值，不是持久状态 |
| `human_confirm` | Type A 人工确认表单值 |
| action `approve` | 唯一触发 Open 写入的 action |
| action `draft` | 不改订单状态，返回审批页 |
| action `cancel` | 取消当前表单，不等于取消 SO |
| actor | 会话用户名参数；当前未落审计 |
| `Open` | 已人工批准可继续履约，不代表已发货 |
| `Delivery Created` | 后续创建 DO 后的 SO 状态，不由 Approve 产生 |
| `approval_requests` | 水平审批中心数据；未接入本 SO Approve |

---

## 6. State Vocabulary

| Value / family | Meaning / caveat |
|----------------|------------------|
| Pending / 待发货 / empty | 可进入 Approve 的 pending family |
| Open | Human Approved 的写结果 |
| Delivery Created | 已建 DO，不代表库存减少 |
| 已发货 / Shipped | 可能是实际发货或手工标签 |
| 已完成 / Completed / Delivered | 完成 family，来源并不统一 |
| 已取消 / Cancelled / Canceled | 取消 family |
| draft action | 保存/停留审批表面，不是 SO Draft 状态 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 非规范 status 默认 pending 是否为有意兼容策略 | sales services/templates、i18n、reports |
| Approve actor 是否由其他中间件自动记录 | sales router/service、audit center、operation logs |
| SO Open 是否应强制 Quote Sent | sales/quotation services、V18 reports |
| 零金额或零数量行能否在生产数据出现 | quote/sales validators、repositories、templates |
| 通用状态 GET 的 CSRF/审计控制 | sales router、security middleware、permission reports |
| 直接“已发货/已完成”是否有下游补偿 | sales/inventory services、delivery reports |
| Approve 后是否应自动建 DO | sales/inventory business modules、V18 report |
| 多租户/owner 对象级批准隔离 | sales repositories、tenant scope、permission reports |
| `Delivery Created` 再 Approve 回 Open 是否为有意兼容 | stage mapping、status routes、delivery reports；当前代码允许 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | stage 归类、Approve context 与 apply 门槛 |
| `apps/sales/router.py` | GET/POST 权限和 Open 重定向 |
| `apps/sales/repository.py` | 状态写入与行读取 |
| `apps/sales/validator.py` | 无通用 SO validator |
| `apps/sales/v14_residual.py` | 状态/残留表面边界 |
| `apps/quotation/services.py` | Quote Approve 是独立上游门 |
| `apps/inventory/services.py` | 后续发货库存门 |
| `templates/so_approve.html` | Type A、human confirm、行摘要 |
| `templates/sales_order_detail.html` | 状态快捷动作及“status only”提示 |
| `templates/includes/v18/type_a_chrome.html` | Human Approved 表面约定 |
| `business_modules/sales.md` | Sales 领域边界 |
| `business_modules/approval.md` | Approval 元数据边界 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | V18 SO Approve 设计与验证 |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | SO 状态事实审计 |
| `docs/reports/Permission_Assessment_Report.md` | 路由权限风险背景 |
| `bootstrap/v14_residual.py` | canonical first-match 路由去重 |
| `bootstrap/enterprise_cutover.py` | business pages 与 residual 挂载顺序 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
