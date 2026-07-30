# 业务挂钩缺口：Quote Approve / SO Approve / Convert / Ship

## Scope 与证据强度

本页固定 Approval Center 与销售主链四个动作的挂钩缺口。强负向证据：`create_approval` 无业务调用；Quote/SO/Convert/Ship 服务均不读 `approval_records`；Integration Queue 明确「Approval → SO/Quote = No chain hook」。交叉引用（只读不改）：

- [`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md)
- [`../quote-convert-policy-deepen/approve_convert_policy.md`](../quote-convert-policy-deepen/approve_convert_policy.md)
- [`../order-chain/so_convert.md`](../order-chain/so_convert.md)
- [`../order-chain/so_approve_open.md`](../order-chain/so_approve_open.md)
- [`../governance/approval.md`](../governance/approval.md)

## 业务规则（稳定 ID）

1. **BHG-R01** Quote Approve 成功只写 Quote `Sent` + 本地日志；不 `create_approval`。
2. **BHG-R02** Quote Approve 不查询中心 Pending/Approved。
3. **BHG-R03** Convert SO 硬门仅为 quote 存在 + 尚无同 quote SO；不查中心审批。
4. **BHG-R04** Convert 不要求 Quote 已 Sent/Approved（可跳过 Type A 与中心）。
5. **BHG-R05** Convert 成功建 SO / 尝试佣金 / 复制行 / 写 quote 已确认；无审批回调。
6. **BHG-R06** SO Approve 硬门为 pending + 有行 + human_confirm；不读中心。
7. **BHG-R07** SO Approve 成功只写 SO `Open`；不通知 Approval Center。
8. **BHG-R08** Ship 硬门为 DO 状态/ledger/库存/human_confirm；不读中心。
9. **BHG-R09** 中心 Approve/Reject **不**调用 quotation/sales/inventory 释放函数。
10. **BHG-R10** 默认类型含 `QUOTE`，但不产生报价提交闭环。
11. **BHG-R11** Hub 模板链接到 purchases/quotes/sales_orders 仅为导航，不是 gate。
12. **BHG-R12** `create_quote_approval` helper 存在于 quotation utils，与中心 `create_approval` 分离；未见 Type A 调用。
13. **BHG-R13** Integration Queue 3.2：Approval → SO/Quote = No chain hook。
14. **BHG-R14** V15：Approval before SO/PO never triggered。
15. **BHG-R15** Convert 路由为 GET mutation；中心亦为 GET 决策——两者均非统一命令编排。
16. **BHG-R16** Ship 之后的 Post AR 同属本地 Type A，仍不挂钩中心（边界：本页以 Ship 为主，AR 作邻近缺口）。

## 挂钩矩阵

| 业务动作 | 提交中心？ | 消费中心结果？ | 实际硬门 |
|---|---|---|---|
| Quote Approve | 否 | 否 | Draft、行、human_confirm |
| Convert Quote→SO | 否 | 否 | quote 存在、无重复 SO |
| SO Approve | 否 | 否 | pending、行、human_confirm |
| DO Ship | 否 | 否 | open、幂等 ledger、库存、human_confirm |
| Center Approve | — | 不推进上表 | 更新 approval_records |

## 校验（强/弱/缺失）

1. **BHG-V01（强）** Quote `apply_approve_action` 无 approval_records SQL。
2. **BHG-V02（强）** `convert_so` 无审批查询。
3. **BHG-V03（强）** `apply_so_approve` 无审批查询。
4. **BHG-V04（强）** Ship 路径无审批查询。
5. **BHG-V05（强）** `create_approval(` 业务调用点缺失。
6. **BHG-V06（缺失）** Convert 必须中心 Approved。
7. **BHG-V07（缺失）** Ship 必须中心 Approved。
8. **BHG-V08（缺失）** 中心 Approved 回调 Sent/Open/Ship。
9. **BHG-V09（强）** Center service 无 source_module 分支回调。
10. **BHG-V10（弱）** Hub 相关链接不能当作已接线证据。
11. **BHG-V11（缺失）** 高金额/低毛利自动升级中心（政策引擎未见）。
12. **BHG-V12（强）** Integration_Queue / V15 负向报告一致。

## 数据含义

| 数据 | 在挂钩语境中的含义 |
|---|---|
| `quotes.status=Sent` | 本地 Type A 结果，非中心 Approved |
| `sales_orders.quote_id` | Convert 追溯/幂等，非审批外键 |
| `sales_orders.status=Open` | 本地 SO Approve 结果 |
| `delivery_orders.status` | Ship 门禁状态，非中心状态 |
| `human_confirm` | 本地确认位 |
| `approval_records.source_module/source_no` | 若有记录可指向业务，但主链不读写 |
| `type_code=QUOTE` | 类型种子，非自动提交 |
| `quote_approval` | 辅助表，非中心、非 Type A 主路径 |
| `approval_history` | 中心审计；业务动作不写此表 |
| `pending_approvals` | 中心个人队列；销售动作不入队 |
| Integration「No chain hook」 | 治理缺口标签 |
| Hub 导航链接 | UX 相关入口 |
| `generate_no("APR")` | 中心编号；销售链未触发 |
| inventory_ledger `DO Ship` | 发运过账类型；与审批无关 |

## 状态词汇

| 链上状态 | 是否依赖中心 |
|---|---|
| Quote Draft/Sent/已确认 | 否 |
| SO pending_delivery/Open | 否 |
| DO open/已出库 | 否 |
| Center Pending/Approved/Rejected | 平行，未接 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| BHG-E01 | Quote Approve 本地门与日志 | 强 | `apps/quotation/services.py` |
| BHG-E02 | Convert 两硬门无审批 | 强 | `apps/sales/services.py` |
| BHG-E03 | Convert GET 路由 | 强 | `apps/sales/router.py` |
| BHG-E04 | SO Approve 本地门 | 强 | `apps/sales/services.py` |
| BHG-E05 | Ship human_confirm/库存门 | 强 | `apps/inventory/services.py` |
| BHG-E06 | Center 无业务回调 | 强 | `apps/approval/services.py` |
| BHG-E07 | create_approval 仅定义 | 强 | `runtime/v14/legacy_support.py` + 全库调用检索 |
| BHG-E08 | No chain hook | 强 | `docs/reports/Integration_Queue.md` |
| BHG-E09 | V15 未触发审批 | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| BHG-E10 | Approve vs Convert 政策负向 | 强 | `../quote-convert-policy-deepen/approve_convert_policy.md` |
| BHG-E11 | quote_approval helper 分离 | 强 | `apps/quotation/utils.py` |
| BHG-E12 | Hub 仅导航到 quotes/SO | 弱/UI | `templates/approvals.html` |

## UNKNOWN + 已查路径

1. **运营是否用线下流程补中心审批再手工点 V18 UNKNOWN。** 已查：business_modules、A-022、V15、templates。
2. **`/add_test_approval` 是否仍可达并被用于造数 UNKNOWN。** 已查：S013 deferred、A-022、Enterprise_Module_Recovery_Report。
3. **Convert 双路由（sales vs residual）是否任一侧插入审批 UNKNOWN。** 已查：`apps/sales/router.py`、`apps/sales/v14_residual.py`、services.convert_so。
4. **采购 PURCHASE 类型与 PO Approve 是否存在隐藏挂钩（本包销售链外）UNKNOWN。** 已查：create_approval 调用点、Integration 3.3、apps/approval。
5. **GFIP/外部网关是否拦截 Ship 并要求中心票 UNKNOWN。** 已查：inventory ship、v15 integration 报告索引、approval apps。
6. **佣金/信用例外是否计划经中心但未编码 UNKNOWN。** 已查：sales commission try、credit-control-deepen 交叉、approval seeds。

## 只读来源路径汇总

`apps/quotation/services.py` · `apps/quotation/utils.py` · `apps/sales/services.py` · `apps/sales/router.py` · `apps/inventory/services.py` · `apps/approval/services.py` · `runtime/v14/legacy_support.py` · `templates/approvals.html` · `docs/reports/Integration_Queue.md` · `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` · `../quote-convert-policy-deepen/approve_convert_policy.md` · `../quotation-deepen/` · `../order-chain/` · `../governance/approval.md`
