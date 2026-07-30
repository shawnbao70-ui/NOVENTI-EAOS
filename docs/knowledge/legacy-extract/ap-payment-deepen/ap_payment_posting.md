# AP 付款写入与镜像

## Scope与证据强度

本页区分 AP 过账与 Treasury 付款登记。强事实是付款写 `treasury_payment_records` 并扣内部银行余额；它没有 AP/Invoice 外键，不构成核销。

## 业务规则（稳定ID）

1. **APP-R01** AP 过账由采购发票和 ap_records 双写完成。
2. **APP-R02** 供应商付款由 POST add_payment_record 登记。
3. **APP-R03** 付款要求 Treasury.add；查看要求 Treasury.view。
4. **APP-R04** payment_no 为 PAY+秒级时间戳。
5. **APP-R05** payment_date 使用服务端当前时间。
6. **APP-R06** account_type 固定为 BANK。
7. **APP-R07** 表单选择 supplier、bank account、amount、method、remark。
8. **APP-R08** 表单不选择 AP 或采购发票。
9. **APP-R09** 付款插入 treasury_payment_records。
10. **APP-R10** 付款后直接将 bank current_balance 减 amount。
11. **APP-R11** 付款不更新 ap_records paid/balance/status。
12. **APP-R12** 付款不更新 purchase_invoices paid/balance/status。
13. **APP-R13** 付款不生成 GL/journal 分录。
14. **APP-R14** 付款不写专用 audit/write_log。
15. **APP-R15** UI confirm 是浏览器确认，不是审批工作流。
16. **APP-R16** treasury_payment_records 没有 status/reversal 字段。
17. **APP-R17** Payment360 只展示资金事实，不展示分配。
18. **APP-R18** cash accounts 存在，但此付款路径仅使用银行账户。
19. **APP-R19** treasury_payments DDL 并存但无活动 INSERT。
20. **APP-R20** 同秒编号、双 POST 和同 AP 重复付款均无幂等防线。

## 流程

1. 用户在 Payment Records 选择供应商、银行账户、金额与方法。
2. 路由校验 Treasury.add。
3. Service 生成 PAY 编号和服务器日期。
4. Repository 插入 treasury_payment_records。
5. 银行账户 current_balance 扣减付款额。
6. 提交后跳回付款列表。
7. AP 与采购发票不被读取或更新。

## 校验（强/弱/缺失）

1. **APP-V01（强）** POST 需要 Treasury.add。
2. **APP-V02（强）** 列表/详情需要 Treasury.view。
3. **APP-V03（弱/UI）** supplier/account/amount 为 required。
4. **APP-V04（缺失）** 服务端不验证 amount>0。
5. **APP-V05（缺失）** 不验证银行余额充足。
6. **APP-V06（缺失）** 不验证供应商与 AP 一致。
7. **APP-V07（缺失）** 不验证分配额≤AP余额。
8. **APP-V08（缺失）** 不阻止已付 AP 再付款。
9. **APP-V09（缺失）** 不验证 payment 与 bank/AP 币种。
10. **APP-V10（部分）** 付款和扣银行顺序执行并 commit。
11. **APP-V11（缺失）** payment_no 无 UNIQUE/idempotency key 证据。
12. **APP-V12（缺失）** 无服务端审批或 audit。
13. **APP-V13（缺失）** 无 reversal/void 校验。
14. **APP-V14（缺失）** 无 GL 借贷平衡校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `payment_no` | PAY 时间戳编号 |
| `payment_date` | 服务端登记日 |
| `supplier_id` | 付款供应商，不等于 AP 分配 |
| `account_type` | 固定 BANK |
| `account_id` | 银行账户主键 |
| `amount` | 本次资金流出 |
| `payment_method` | 自由文本付款方法 |
| `remark` | 备注，不是 allocation |
| `current_balance` | 内部银行余额镜像 |
| `bank.currency` | 账户币种，未与付款校验 |
| `ap_records.paid_amount` | 不随付款更新 |
| `ap_records.balance_amount` | 不随付款更新 |
| `purchase_invoices.balance_amount` | 不随付款更新 |
| `treasury_payments` | 孤立并行 DDL 表 |
| `human confirm` | UI 确认提示 |

## 状态词汇

| 词汇 | 实际语义 |
|---|---|
| Posted/Registered | 付款记录已插入、银行镜像已扣 |
| Cleared/Allocated | 未实现 |
| Reversed/Voided | 未实现 |
| Human-approved | UI confirm，不是审批状态 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| APP-E01 | 付款路由与权限 | 强 | `apps/finance/router.py` |
| APP-E02 | 付款 service 流程 | 强 | `apps/finance/services.py` |
| APP-E03 | payment insert/bank deduct | 强 | `apps/finance/repository.py` |
| APP-E04 | 平行 treasury handler | 强 | `apps/finance/treasury_pages.py` |
| APP-E05 | 四个 Treasury/AP DDL | 强 | `runtime/v14/legacy_support.py` |
| APP-E06 | 付款表单无 AP 选择 | 强 | `templates/payment_records.html` |
| APP-E07 | Payment360 无分配明细 | 强 | `templates/payment_record_360.html` |
| APP-E08 | AP UI 明示人工付款 | 中 | `templates/ap_dashboard.html` |
| APP-E09 | A-020 未重写付款 handler | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **付款与扣银行失败时原子 rollback UNKNOWN。** 已查路径：service、repository commit、connection wrapper。
2. **treasury_payments 与 treasury_payment_records 权威选择 UNKNOWN。** 已查路径：DDL、全库 INSERT。
3. **生产环境是否有 GL 插件 UNKNOWN。** 已查路径：Finance、journal、ledger、plugins。
4. **现金账户付款是否有隐藏入口 UNKNOWN。** 已查路径：Treasury routes/templates/services。
5. **付款审批是否在外部分支集成 UNKNOWN。** 已查路径：Approval app、payment引用。
6. **payment_no 同秒碰撞行为 UNKNOWN。** 已查路径：DDL/index/retry。
7. **多币种付款与汇差政策 UNKNOWN。** 已查路径：Payment DDL、bank currency、FX。
8. **付款撤销/退款的线下流程 UNKNOWN。** 已查路径：void/reverse/refund routes、reports。
9. **双 handler 实际挂载优先级 UNKNOWN。** 已查路径：router、treasury_pages、bootstrap。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
