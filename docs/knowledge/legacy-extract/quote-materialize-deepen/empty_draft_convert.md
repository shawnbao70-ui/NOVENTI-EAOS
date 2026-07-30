# 空行 Draft 可 Convert：完整证据链

**Evidence strength:** Strong  
**结论：** 活动主路径允许 Sample→Quote 只建零金额 Draft 头；Convert SO 只检查 Quote 存在和未重复转换，不检查状态或行数；空 item 集合的复制循环自然结束，SO 头仍已创建，Quote 随后被写为 `已确认`。下游 SO Approve 才可能以“至少一行”阻断。

## 端到端链

1. Sample360 触发 `GET /create_quote_from_sample/{sample_id}`。
2. Quotation service 读取 Sample；即使读取结果为空，也未见硬拒绝。
3. Repository 插入 `quotes` 头：Draft、可空 customer、来源 sample_id；INSERT 不传 `total_amount`，因此金额依赖 schema 默认（现有运行语义为零）。
4. 路径只尝试商业头默认和 lifecycle link；没有创建 `quote_items`。
5. Quote 列表对有权限用户显示 Convert，并以浏览器 confirm 提示。
6. `GET /convert_so/{quote_id}` 进入 Sales service。
7. Service 只硬检查 Quote 存在、该 quote_id 尚无 SO。
8. Repository 先插入 SO 头，直接复制 Quote 的 customer/owner/total。
9. `_copy_quote_items_to_so` 读取空集合，循环零次，不将“零行”视为错误。
10. best-effort commission/lifecycle 失败也可被吞掉。
11. Quote 状态更新为中文 `已确认`，请求重定向到 SO detail。
12. 直到 SO Approve 才有 SO 行数检查，因此风险在下游迟报。

## 业务规则

| ID | 规则 |
|---|---|
| EDC-R01 | Sample→Quote 允许只建 Quote 头。 |
| EDC-R02 | 该头初始为 Draft；INSERT 不写 total_amount，零金额依赖 schema 默认。 |
| EDC-R03 | Quote create 不要求至少一行。 |
| EDC-R04 | Quote Approve 要求至少一行，但 Convert 不依赖 Approve。 |
| EDC-R05 | Convert 不要求状态为 Sent/Approved/Won。 |
| EDC-R06 | Convert 的源 Quote 必须存在。 |
| EDC-R07 | 已存在引用同 quote_id 的 SO 时，service 阻止重复转换。 |
| EDC-R08 | SO 头在 item copy 之前创建。 |
| EDC-R09 | 空 item 查询结果是合法 iterable，复制零行不会抛错。 |
| EDC-R10 | SO total 直接复制 Quote 头零金额，不按行重新求和。 |
| EDC-R11 | customer/salesperson 可空或零，不构成 Convert 门。 |
| EDC-R12 | lifecycle/commission 是 best-effort，不补完整性门。 |
| EDC-R13 | 成功转换后 Quote 写 `已确认`，即使 SO 无行。 |
| EDC-R14 | Convert 是 GET 变更动作；UI confirm 不是服务端完整性校验。 |
| EDC-R15 | SO Approve 的行门只能迟延发现空单，不能撤销既有转换事实。 |
| EDC-R16 | residual Quotation convert 路径的存在增加部署漂移风险，但活动 Sales 主路径已足以证明空转。 |

## 校验

| ID | 校验点 | Convert 实际 |
|---|---|---|
| EDC-V01 | Quote id 可解析 | Route hard type |
| EDC-V02 | Quote 存在 | Hard |
| EDC-V03 | 同 Quote 未转换 | Hard query guard |
| EDC-V04 | Quote 为 Draft | 不检查 |
| EDC-V05 | Quote 已 Approve/Sent | 不检查 |
| EDC-V06 | 至少一条 Quote item | 不检查 |
| EDC-V07 | customer 非空且有效 | 不检查 |
| EDC-V08 | salesperson 非空且有效 | 不检查 |
| EDC-V09 | total 与行合计相等 | 不检查 |
| EDC-V10 | qty/price/amount 合法 | 不检查 |
| EDC-V11 | 报价未过期 | 不检查 |
| EDC-V12 | POST/CSRF 与服务端 RBAC | 缺失/弱 |
| EDC-V13 | 空 SO 不得提交 | 仅后续 SO Approve |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.id` | Convert 源键 |
| `quotes.status=Draft` | 未经 Approve 的初态，但 Convert 不读取为门 |
| `quotes.total_amount` | 创建 INSERT 未写；空报价的零值依赖 schema 默认 |
| `quotes.customer_id` | 复制到 SO，可为空 |
| `quotes.salesperson_id` | 复制到 SO，可为零/空风险 |
| `quote_items=[]` | 合法查询结果；不等于 service error |
| `sales_orders.quote_id` | 来源引用与应用层防重复依据 |
| SO header | 在复制 items 前持久化的目标主体 |
| SO total | Quote 头 total 的直接快照 |
| `sales_order_items=[]` | 空循环后的目标行集合 |
| Quote `已确认` | 转换成功标记，不代表完整性已验证 |
| lifecycle link | 可选追溯副作用 |
| commission | best-effort 副作用 |
| SO Approve gate | 下游行完整性门，而非 Convert 原子门 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| EDC-E01 | Sample route 进入只建头服务 | 强 | `apps/quotation/router.py`、`services.py::create_quote_from_sample` |
| EDC-E02 | insert_quote_from_sample 只 INSERT quotes | 强 | `apps/quotation/repository.py` |
| EDC-E03 | 创建链无 item insert | 强负向 | `apps/quotation/services.py` |
| EDC-E04 | Convert route 直接调用 sales convert | 强 | `apps/sales/router.py` |
| EDC-E05 | Convert 只有存在/重复两项前置检查 | 强 | `apps/sales/services.py::convert_so` |
| EDC-E06 | SO header insert 先于 item copy | 强 | `apps/sales/services.py`、`repository.py` |
| EDC-E07 | item copy 是普通迭代，空集合零次执行 | 强 | `apps/sales/services.py::_copy_quote_items_to_so` |
| EDC-E08 | Convert 后更新 Quote 为已确认 | 强 | `apps/sales/repository.py::update_quote_status_confirmed` |
| EDC-E09 | Quote Approve 有行门，Convert 未复用 | 强对照 | `apps/quotation/services.py::apply_approve_action` |
| EDC-E10 | SO Approve 才检查 SO 行 | 强 | `apps/sales/services.py::apply_so_approve` |
| EDC-E11 | UI Convert 是 confirm + GET | 强 | `templates/quotes.html` |

## UNKNOWN + 已查路径

1. **空 Quote→空 SO 是有意占位还是缺陷 UNKNOWN。** 已查：Quotation/Sales services、routers、templates、reports。
2. **SO header/item insert 是否由外层统一事务包裹 UNKNOWN。** 已查：Sales service/repository、DB dependency、middleware。
3. **数据库是否唯一约束 `sales_orders.quote_id` UNKNOWN。** 已查：repository、runtime DDL、upgrade scripts。
4. **并发双 Convert 能否都越过应用层查询 UNKNOWN。** 已查：convert service、repository、schema。
5. **customer 为空时数据库/下游物流何处失败 UNKNOWN。** 已查：SO insert、approval、DO creation、finance reports。
6. **`已确认` 与 Sent/Won 的权威状态含义 UNKNOWN。** 已查：Quotation state handlers、i18n、templates、reports。
7. **失败后是否有自动清理空 SO UNKNOWN。** 已查：Sales delete/cancel/rollback paths、jobs、reports。
8. **residual convert 在当前部署是否仍可达 UNKNOWN。** 已查：router registration、quote_pages、app startup。

## 交叉引用

- 桥接完整性权威：[`../sample-quote-bridge-deepen/quote_completeness.md`](../sample-quote-bridge-deepen/quote_completeness.md)
- Quote→SO 门：[`../quotation-deepen/quote_convert_gates.md`](../quotation-deepen/quote_convert_gates.md)
- Quote Approve：[`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md)
