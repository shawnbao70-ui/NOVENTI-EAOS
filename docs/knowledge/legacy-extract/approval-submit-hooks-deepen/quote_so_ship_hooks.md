# Quote / SO / Convert / Ship — 是否创建中央审批记录

## Scope 与证据强度

本页固定销售主链四个动作与中央 `approval_records` 的提交/消费关系。强结论：**四者均不调用 `create_approval`，均不读写 `approval_records`**；门禁为本地状态 +（Type A 路径上的）`human_confirm`。交叉引用（只读不改）：[`../approval-center-deepen/business_hook_gaps.md`](../approval-center-deepen/business_hook_gaps.md)、[`../quotation-deepen/`](../quotation-deepen/)、[`../order-chain/`](../order-chain/)、[`create_approval_call_sites.md`](create_approval_call_sites.md)。

## 业务规则（稳定 ID）

1. **QSH-R01** Quote Approve（`apply_approve_action`）硬门：Draft、有行、`human_confirm=="1"`；成功写 Quote `Sent` + 可选操作日志；**不** `create_approval`。
2. **QSH-R02** Quote Approve **不**查询 Pending/Approved 中央记录。
3. **QSH-R03** Convert SO（`convert_so`）硬门：quote 存在 + 尚无同 quote SO；**不**要求 Quote Sent/Approved，**不**查中心。
4. **QSH-R04** Convert 成功：建 SO、尝试佣金、复制行、quote 已确认、可选 lifecycle link；**无**审批回调。
5. **QSH-R05** Convert 路由为 `GET /convert_so/{quote_id}`（mutation）；与中心提交无关。
6. **QSH-R06** SO Approve（`apply_so_approve`）硬门：pending 阶段、有行、`human_confirm`；成功写 SO `Open`；**不**通知 Approval Center。
7. **QSH-R07** Ship（`apply_do_ship` / `ship_delivery_order`）硬门：DO 阶段/库存/ledger 幂等 + Type A `human_confirm`；**不**读中心。
8. **QSH-R08** 中心 Approve/Reject 只更新 `approval_records`（+主路径 history）；**不**调用 quotation/sales/inventory 释放函数。
9. **QSH-R09** 类型种子含 `QUOTE`，不产生报价自动提交闭环。
10. **QSH-R10** Hub 模板相关链接到 purchases/quotes/sales_orders 仅为导航，不是 gate。
11. **QSH-R11** `create_quote_approval` 与中央分离；Type A 路径未见调用。
12. **QSH-R12** Integration Queue 3.2：Approval → SO/Quote = **No chain hook**。
13. **QSH-R13** V15：Approval before SO/PO **Never triggered**。
14. **QSH-R14** Human Approved（V18）≠ `approval_records.approval_status=Approved`。
15. **QSH-R15** Ship 后 Post AR 同属本地 Type A，仍不挂钩中心（邻近边界）。
16. **QSH-R16** 不得把「存在 Approval Center UI」解释为销售链已提交中央票。

## 挂钩矩阵

| 业务动作 | 创建中央记录？ | 消费中央结果？ | 实际硬门 |
|---|---|---|---|
| Quote Approve | 否 | 否 | Draft、行、human_confirm → Sent |
| Convert Quote→SO | 否 | 否 | quote 存在、无重复 SO |
| SO Approve | 否 | 否 | pending、行、human_confirm → Open |
| DO Ship | 否 | 否 | open/库存/ledger、human_confirm |
| Center Approve/Reject | — | 不推进上表 | 更新 approval_records |

## 校验（强/弱/缺失）

1. **QSH-V01（强）** `apply_approve_action` 源码无 approval_records / create_approval。
2. **QSH-V02（强）** `convert_so` 无审批查询/插入。
3. **QSH-V03（强）** `apply_so_approve` 无审批查询/插入。
4. **QSH-V04（强）** `apply_do_ship` / `ship_delivery_order` 无审批查询/插入。
5. **QSH-V05（强）** `apps/approval/services.py` 无 source_module 分支回调。
6. **QSH-V06（缺失）** Convert 必须中心 Approved。
7. **QSH-V07（缺失）** Ship 必须中心 Approved。
8. **QSH-V08（缺失）** 中心 Approved 回调 Sent/Open/Ship。
9. **QSH-V09（强）** Integration_Queue / V15 负向一致。
10. **QSH-V10（弱）** Hub 导航链接不能当接线证据。
11. **QSH-V11（缺失）** 金额/毛利自动升级中心策略。
12. **QSH-V12（强）** 全库业务 `create_approval(` 调用点缺失（见 CAS）。

## 数据含义

| 数据 | 在挂钩语境中的含义 |
|---|---|
| `quotes.status=Sent` | 本地 Type A 结果，非中心 Approved |
| `sales_orders.quote_id` | Convert 追溯/幂等，非审批外键 |
| `sales_orders.status=Open` | 本地 SO Approve 结果 |
| `delivery_orders.status` | Ship 门禁状态，非中心状态 |
| `human_confirm` | 本地确认位（表单值 `"1"`） |
| `approval_records.source_*` | 若有记录可指向业务，但主链不读写 |
| `type_code=QUOTE` | 类型种子，非自动提交 |
| `quote_approval` | 辅助表；非中心、非 Type A 主路径 |
| `approval_history` | 中心审计；销售动作不写 |
| `pending_approvals` | 中心个人队列；销售动作不入队 |
| Integration「No chain hook」 | 治理缺口标签 |
| Hub 导航链接 | UX 相关入口 |
| `generate_no("APR")` | 中心编号；销售链未触发 |
| inventory_ledger DO Ship | 发运过账；与审批无关 |

## 状态词汇

| 链上状态 | 是否依赖中心 |
|---|---|
| Quote Draft/Sent/已确认 | 否 |
| SO pending_delivery/Open | 否 |
| DO open/已出库 | 否 |
| Center Pending/Approved/Rejected | 平行，未接 |
| Human Approved | 本地 Type A 语义，非中心态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| QSH-E01 | Quote Approve 本地门与 Sent | 强 | `apps/quotation/services.py` |
| QSH-E02 | Convert 两硬门无审批 | 强 | `apps/sales/services.py` |
| QSH-E03 | Convert GET 路由 | 强 | `apps/sales/router.py` |
| QSH-E04 | SO Approve → Open 本地门 | 强 | `apps/sales/services.py` |
| QSH-E05 | Ship human_confirm/库存门 | 强 | `apps/inventory/services.py` · `router.py` |
| QSH-E06 | Center 无业务回调 | 强 | `apps/approval/services.py` |
| QSH-E07 | create_approval 仅定义 | 强 | `runtime/v14/legacy_support.py` + 全库检索 |
| QSH-E08 | No chain hook | 强 | `docs/reports/Integration_Queue.md` |
| QSH-E09 | V15 未触发审批 | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| QSH-E10 | quote_approval helper 分离 | 强 | `apps/quotation/utils.py` |
| QSH-E11 | Hub 仅导航到 quotes/SO | 弱/UI | `templates/approvals.html` |
| QSH-E12 | 邻包挂钩缺口结论一致 | 强 | `../approval-center-deepen/business_hook_gaps.md` |

## UNKNOWN + 已查路径

1. **运营是否用线下流程补中心审批再手工点 V18 UNKNOWN。** 已查：business_modules、A-022、V15、templates、quotation/sales/inventory services。
2. **Convert 双路由（sales vs residual）是否任一侧插入审批 UNKNOWN。** 已查：`apps/sales/router.py`、`apps/sales/v14_residual.py`、`services.convert_so`。
3. **采购 PURCHASE 类型与 PO Approve 是否存在隐藏挂钩（销售链外）UNKNOWN。** 已查：create_approval 调用点、Integration 3.3、apps/approval、apps/procurement 抽样。
4. **GFIP/外部网关是否拦截 Ship 并要求中心票 UNKNOWN。** 已查：inventory ship、V15/Integration、approval apps。
5. **佣金/信用例外是否计划经中心但未编码 UNKNOWN。** 已查：sales commission try、credit-control-deepen 交叉意图路径、approval seeds。
6. **`quote_approval` 行是否被任何报表计入「已审批报价」UNKNOWN。** 已查：quotation utils counts、quote approve 服务、templates/approval*。
7. **历史库中是否存在人工插入的 source_module=Quotation 中央行 UNKNOWN。** 已查：代码提交路径（无）；运行时 DB 内容不可从此包断言。

## 只读来源路径汇总

`apps/quotation/services.py` · `apps/quotation/utils.py` · `apps/sales/services.py` · `apps/sales/router.py` · `apps/sales/v14_residual.py` · `apps/inventory/services.py` · `apps/inventory/router.py` · `apps/approval/services.py` · `runtime/v14/legacy_support.py` · `templates/approvals.html` · `docs/reports/Integration_Queue.md` · `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` · `../approval-center-deepen/business_hook_gaps.md` · `create_approval_call_sites.md`
