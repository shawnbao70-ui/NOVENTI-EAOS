# 付款分配到 AP / Invoice

## Scope 与结论

本页深化 [`../ap-payment-deepen/ap_payment_posting.md`](../ap-payment-deepen/ap_payment_posting.md) 与 [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)。结论：供应商付款是 `supplier + bank account` 级资金登记，不选择、引用或更新 AP/Invoice；Legacy 没有 payment allocation。

## 业务规则（稳定 ID）

1. **PAL-R01** 付款 POST 需要 `Treasury.add`；列表与详情需要 `Treasury.view`。
2. **PAL-R02** 表单输入 supplier、bank account、amount、method、remark。
3. **PAL-R03** 表单没有 `ap_id`、`invoice_id` 或 allocation rows。
4. **PAL-R04** `payment_no` 为 `PAY` 加服务器秒级时间戳。
5. **PAL-R05** `payment_date` 使用服务器当前日期，不采用供应商凭证日。
6. **PAL-R06** `account_type` 固定写 `BANK`。
7. **PAL-R07** 付款先 INSERT `treasury_payment_records`。
8. **PAL-R08** 随后按 `account_id` 将 bank `current_balance` 减去 amount。
9. **PAL-R09** bank update 内执行 commit，提交前述 payment INSERT 与余额更新。
10. **PAL-R10** 付款不读取该 supplier 的 AP 或 Invoice。
11. **PAL-R11** 付款不更新 `ap_records.paid_amount/balance_amount/status`。
12. **PAL-R12** 付款不更新 `purchase_invoices.paid_amount/balance_amount/status`。
13. **PAL-R13** 一笔付款不能结构化分配到多条 AP。
14. **PAL-R14** 一条 AP 也不能由多笔付款形成可审计的累计 allocation。
15. **PAL-R15** 供应商级 payment 不能证明已清哪张发票。
16. **PAL-R16** `remark` 是自由文本，不能替代 allocation FK。
17. **PAL-R17** Payment360 展示付款事实与 supplier，不展示核销明细。
18. **PAL-R18** `treasury_payment_records` 没有 currency、status、approval、reversal 或 unapplied amount。
19. **PAL-R19** 并存的 `treasury_payments` DDL 同样无 AP/Invoice 链，且未见活动 writer。
20. **PAL-R20** allocation/clearing 缺失使付款后 AP Dashboard 仍可显示原全额未付。

## 实际流程

1. 用户选择 supplier 与 bank account，提交 amount/method/remark。
2. Route 做 Treasury add 权限检查。
3. Service 生成 payment 编号与日期。
4. Repository 写 payment record。
5. Repository 扣内部 bank mirror 并 commit。
6. 流程结束；没有“选择 AP→分摊→更新余额→关闭”阶段。

## 校验（强 / 弱 / 缺失）

1. **PAL-V01（强）** 新增付款要求 Treasury.add。
2. **PAL-V02（强）** 查看付款要求 Treasury.view。
3. **PAL-V03（强/解析层）** supplier/account/amount 为必填 Form 参数。
4. **PAL-V04（弱/UI）** HTML required 要求选择 supplier/account 并填写 amount。
5. **PAL-V05（部分）** payment insert 与 bank update 共享一次最终 commit。
6. **PAL-V06（缺失）** 服务端不验证 amount>0；负数可能反向增加 bank mirror。
7. **PAL-V07（缺失）** 不验证 bank balance 足够。
8. **PAL-V08（缺失）** 不验证 supplier/account 实体存在及 update 命中。
9. **PAL-V09（缺失）** 不验证 payment supplier 与 AP supplier 一致。
10. **PAL-V10（缺失）** 不验证 allocation 总额≤payment。
11. **PAL-V11（缺失）** 不验证 allocation 总额≤AP balance。
12. **PAL-V12（缺失）** 不阻止对已付/关闭 AP 再付款。
13. **PAL-V13（缺失）** 不验证 bank 与 AP/Invoice 币种。
14. **PAL-V14（缺失）** payment_no 未见 UNIQUE 或 idempotency key。
15. **PAL-V15（缺失）** 无逐笔审批、人类确认记录、GL 平衡与银行回执校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `treasury_payment_records.id` | 资金登记主键 |
| `payment_no` | 秒级生成的内部付款号 |
| `payment_date` | 服务器登记日 |
| `supplier_id` | 供应商级归属，不是 AP allocation |
| `account_type` | 固定 `BANK` |
| `account_id` | 被扣内部银行账户 |
| `amount` | 本次登记资金流出 |
| `payment_method` | 自由文本支付方式 |
| `remark` | 自由文本备注 |
| `treasury_bank_accounts.current_balance` | 系统内部银行余额镜像 |
| `ap_records.invoice_id` | AP 的 Invoice 锚点；付款不使用 |
| `ap_records.balance_amount` | AP Dashboard 余额；付款不更新 |
| `purchase_invoices.balance_amount` | Invoice 镜像余额；付款不更新 |
| allocation amount | 未建模 |
| unapplied amount | 未建模 |
| payment currency | 未存于 payment record |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| PAL-E01 | 付款路由、Form 字段、权限 | 强 | `apps/finance/router.py` |
| PAL-E02 | 编号、日期与顺序调用 | 强 | `apps/finance/services.py` |
| PAL-E03 | Payment INSERT 与 bank 扣减/commit | 强 | `apps/finance/repository.py` |
| PAL-E04 | Payment/AP/Invoice DDL 无 allocation FK | 强 | `runtime/v14/legacy_support.py` |
| PAL-E05 | 表单无 AP/Invoice 选择 | 强 | `templates/payment_records.html` |
| PAL-E06 | Payment360 无分配明细 | 强 | `templates/payment_record_360.html` |
| PAL-E07 | AP Dashboard 仅汇总 AP 字段 | 强 | `apps/finance/services.py`、`templates/ap_dashboard.html` |
| PAL-E08 | 人工付款与诚实 UI 边界 | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |
| PAL-E09 | Finance 设计意图对照 | 弱/意图 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **生产是否有人直接 SQL 更新 AP UNKNOWN。** 已查：UI/API/services/jobs/scripts；未读生产库。
2. **付款与 bank update 异常时连接层 rollback 结果 UNKNOWN。** 已查：service、repository、SQLite adapter、bootstrap。
3. **无效 account_id 导致零行 update 时是否仍作为成功付款 UNKNOWN。** 已查：repository rowcount/error handling；未执行生产测试。
4. **`treasury_payments` 是否由外部集成写入 UNKNOWN。** 已查：全库 INSERT、imports、plugins、jobs。
5. **实际付款审批是否在系统外完成 UNKNOWN。** 已查：Approval、Finance routes、reports。
6. **同秒 payment_no 碰撞的生产后果 UNKNOWN。** 已查：DDL/indexes/retry；无 UNIQUE 证据。
7. **多币种、汇率与汇差政策 UNKNOWN。** 已查：payment/bank schema、FX、Finance docs。
8. **供应商预付款如何标识和后续分配 UNKNOWN。** 已查：advance/prepay/unapplied/allocation 搜索。
9. **银行流水/回执是否由外部插件对账 UNKNOWN。** 已查：bank_transactions writers、integrations、reports。

## 只读来源路径

`apps/finance/`、`apps/approval/`、`templates/`、`runtime/v14/legacy_support.py`、`core/database/`、`business_modules/`、`docs/reports/`。
