# Quote Approve vs Convert SO 校验对照

**Evidence strength:** Strong  
**结论：** Approve 是 Draft→Sent 的局部人工确认门，Convert 是 Quote→SO 的物化门；二者没有前置依赖。Approve 转态时校验 Draft、行与 Human Confirm，并校验提交的 qty/price；但 line patch 发生在 Draft 状态 gate 之前。Convert 只校验 Quote 存在和应用层未重复，不能用“可 Convert”推断报价已完整或已批准。

## 校验矩阵

| 校验维度 | Approve | Convert SO | 差异/风险 |
|---|---|---|---|
| Quote 存在 | Hard | Hard | 共同门 |
| 当前状态 | 转为 Sent 时必须 Draft；patch 次序在前 | 不检查 | 非 Draft 构造 POST 可先改行；任意状态可能转 |
| Human Confirm | 服务端要求 | 无；仅浏览器 confirm | UI 提示不可等同 Type A |
| 至少一行 | Hard | 不检查 | 可创建空 SO |
| qty | patch 时 `>0` | 不重验 | 脏行可传播 |
| price | patch 时 `>=0` | 不重验 | 零价可传播 |
| amount | 更新行时重算 | 直接复制行值 | Convert 不复算 |
| 头总额 | Approve 路径重汇总 | 直接复制现值 | 可与行不一致 |
| customer | 不硬校验 | 不硬校验 | 两侧均缺 |
| salesperson | 不硬校验 | 不硬校验 | 两侧均缺 |
| 币种/汇率 | 非门 | 不校验且 SO insert 不承接 | 商业语义丢失 |
| 付款/交付条件 | 非门 | 不校验/不完整复制 | 下游上下文不足 |
| validity/expiry | 不按日期阻断 | 不检查 | 过期 Quote 可转 |
| sample/product | 非门 | 非门 | 来源与行不保证一致 |
| requirement/opportunity | 非门 | best-effort 传播 | 失败不回滚 |
| 中心审批记录 | 不要求；本地 Type A | 不要求 | approval center 非依赖 |
| 已有 SO | 不适用 | 应用层查询 Hard | Convert 独有门 |
| 服务端 RBAC | Approve route 有管理门 | handler 未见等价显式门 | 权限不对称 |
| HTTP 语义 | POST | GET | Convert 有直链/CSRF 风险 |
| 最终状态 | Sent | `已确认` | 中英状态空间混杂 |

## 业务规则

| ID | 规则 |
|---|---|
| CCM-R01 | Approve 与 Convert 是两条独立 route/service 链。 |
| CCM-R02 | Approve 只接受 Draft。 |
| CCM-R03 | Approve 要求至少一条报价行。 |
| CCM-R04 | Approve 要求服务端 `human_confirm`。 |
| CCM-R05 | Approve 可先 patch qty/price 并重算金额。 |
| CCM-R06 | Approve 成功将 Quote 写为 Sent。 |
| CCM-R07 | Convert 不调用 Approve，也不查询其操作日志。 |
| CCM-R08 | Convert 不要求 Sent/Approved/Won 状态。 |
| CCM-R09 | Convert 不要求行、客户、owner、有效期、币种完整。 |
| CCM-R10 | Convert 仅要求 Quote 存在。 |
| CCM-R11 | Convert 通过查询已有关联 SO 防止顺序重复。 |
| CCM-R12 | Convert 直接复制头 total 和行字段，不执行报价完整性重算。 |
| CCM-R13 | Convert 的 lifecycle/commission 副作用不是提交前 gate。 |
| CCM-R14 | Convert 成功写中文 `已确认`，与 Approve 的 Sent 不同。 |
| CCM-R15 | SO Approve 的行门属于后续阶段，不能补成 Convert 前置校验。 |
| CCM-R16 | UI 权限可见性与 confirm 只能算弱门，不能替代 handler/POST/CSRF。 |
| CCM-R17 | Approve service 在 Draft 状态 gate 之前执行 line patches 与 total 重算。 |
| CCM-R18 | `action=draft` 不验证当前状态；正常 UI 仅以 readonly/隐藏按钮限制非 Draft。 |

## 校验清单

| ID | 控制 | 强度 |
|---|---|---|
| CCM-V01 | Approve: Quote exists | Hard |
| CCM-V02 | Approve: status Draft | Hard |
| CCM-V03 | Approve: at least one item | Hard |
| CCM-V04 | Approve: human_confirm | Hard |
| CCM-V05 | Approve patch: qty > 0 | Hard when supplied |
| CCM-V06 | Approve patch: price >= 0 | Hard when supplied |
| CCM-V07 | Convert: Quote exists | Hard |
| CCM-V08 | Convert: no prior SO by quote_id | Hard query guard |
| CCM-V09 | Convert: status approved/sent | Missing |
| CCM-V10 | Convert: at least one item | Missing |
| CCM-V11 | Convert: total/line reconciliation | Missing |
| CCM-V12 | Convert: customer/owner validity | Missing |
| CCM-V13 | Convert: expiry/commercial header | Missing |
| CCM-V14 | Convert: trace propagation success | Missing |
| CCM-V15 | Convert: DB-level concurrency uniqueness | UNKNOWN |
| CCM-V16 | Approve: patch 前验证 Draft | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `Draft` | Approve 唯一允许的源状态；Convert 无视 |
| `Sent` | Approve 成功状态，不是 Convert 必须状态 |
| `已确认` | Convert 后写入的中文状态 |
| `human_confirm` | Type A 人工确认参数，只在 Approve 服务端生效 |
| `quote_items` count | Approve 硬门；Convert 不使用 |
| qty/price patch | Approve 页内修改载荷 |
| line amount | patch 后计算值；Convert 直接复制 |
| header total | Approve 重汇总目标；Convert 源快照 |
| `sales_orders.quote_id` | Convert 来源和防重复查询键 |
| customer/salesperson | 两条路径均未做强有效性校验 |
| currency/exchange rate | Quote 商业头；Convert 未保证承接 |
| validity days | 展示/默认数据，未形成日期 gate |
| operation log | Approve 动作审计，不是中心审批依赖 |
| lifecycle link | best-effort 追溯副作用 |
| patch ordering | qty/price 更新早于 Draft/行/Human Confirm gate |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| CCM-E01 | Approve route 管理权限与 POST 入口 | 强 | `apps/quotation/router.py` |
| CCM-E02 | Approve 检查 Draft/行/human_confirm | 强 | `apps/quotation/services.py::apply_approve_action` |
| CCM-E03 | Approve 更新行并重算头 total | 强 | `apps/quotation/services.py`、`repository.py` |
| CCM-E04 | Convert GET route 进入 Sales service | 强 | `apps/sales/router.py` |
| CCM-E05 | Convert 只有存在/重复 guard | 强 | `apps/sales/services.py::convert_so` |
| CCM-E06 | SO insert 复制 Quote 头 | 强 | `apps/sales/repository.py::insert_sales_order` |
| CCM-E07 | item copy 不重验业务值 | 强 | `apps/sales/services.py::_copy_quote_items_to_so` |
| CCM-E08 | lifecycle 调用 best-effort | 强 | `apps/sales/services.py`、`v15/business_lifecycle/workflow.py` |
| CCM-E09 | Quote UI 的 Convert 权限可见性与 confirm | 强 | `templates/quotes.html` |
| CCM-E10 | SO Approve 才另有行 gate | 强 | `apps/sales/services.py::apply_so_approve` |
| CCM-E11 | V18 报告界定 Quote Approve Type A | 中等佐证 | `docs/reports/V18_Quote_Approve_Gate_Report.md` |
| CCM-E12 | line patch/total update 先于 action/status gates | 强 | `apps/quotation/services.py::apply_approve_action` |
| CCM-E13 | 非 Draft UI readonly 且隐藏动作，但 POST route 仍只按 edit 权限接收 | 强 | `templates/quote_approve.html`、`apps/quotation/router.py` |

## UNKNOWN + 已查路径

1. **业务为何不要求 Sent 才 Convert UNKNOWN。** 已查：Quotation/Sales services、business_modules、reports。
2. **`已确认` 是否等价 Won/Approved UNKNOWN。** 已查：i18n、templates、status handlers、reports。
3. **Convert route 是否由全局 middleware 补 RBAC/CSRF UNKNOWN。** 已查：router、startup、middleware、templates。
4. **DB 是否唯一约束 sales_orders.quote_id UNKNOWN。** 已查：Sales repository、DDL、upgrade scripts。
5. **客户/owner 失效应在哪一层阻断 UNKNOWN。** 已查：validators、Quotation/Sales services、customer repository。
6. **过期报价是否业务允许转换 UNKNOWN。** 已查：validity fields、quote pages、convert、reports。
7. **中心 Approval Center 是否在部署配置中另行拦截 UNKNOWN。** 已查：quotation approval utils、governance modules、routes。
8. **多步骤 Convert 的原子事务边界 UNKNOWN。** 已查：service/repository commit、DB dependency。

## 交叉引用

- Approve 权威：[`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md)
- Convert 权威：[`../quotation-deepen/quote_convert_gates.md`](../quotation-deepen/quote_convert_gates.md)
- 桥接完整性：[`../sample-quote-bridge-deepen/quote_completeness.md`](../sample-quote-bridge-deepen/quote_completeness.md)
