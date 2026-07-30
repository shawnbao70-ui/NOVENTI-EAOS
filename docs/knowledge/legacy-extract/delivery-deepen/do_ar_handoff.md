# DO→AR / Invoice 交界深化

## Scope与证据强度

本页只深化 DO 生命周期末端到 AR 应计、收款和 NDE Invoice 打印的交界；不复制既有 Delivery 或 Finance 正文。

- **强证据：** Inventory Type A 路由、Finance AR INSERT、DDL、权限、Ship/Complete/Reopen 服务。
- **中证据：** NDE 打印与 gates 证明页面/版式，不证明税务开票。
- **明确分层：** Post AR 是应收应计；NDE Invoice 是商业版式；Tax Center 是独立税务域。
- **核心风险：** Legacy 双路由、重复 AR 软守卫、两套 AR 口径和收款不回写 `ar_records`。

## 业务规则

1. **DA-R01** DO Invoice 动作创建 `ar_records` 应计，不是税务发票或商业发票签发。
2. **DA-R02** V18 Type A Post AR 必须提交人工确认。
3. **DA-R03** 只有 approve 动作调用 Legacy AR 写入服务。
4. **DA-R04** Finance 模块的旧 `/create_ar/{do_id}` 设计上重定向到 Type A 页面。
5. **DA-R05** 平台 residual 仍保留同名静默 INSERT 路径，形成路由冲突风险。
6. **DA-R06** Ship 只允许 open DO，且 ledger 提供重复出库守卫。
7. **DA-R07** Complete 只允许 shipped DO。
8. **DA-R08** Reopen 只允许 complete DO，且不回补库存。
9. **DA-R09** Complete/Reopen 不修改或冲销已有 AR。
10. **DA-R10** 已有 AR 只显示警告，仍允许再次插入。
11. **DA-R11** 重复提示按 `ar_records.source_no = do_no` 计数。
12. **DA-R12** AR 金额等于 DO 头总额，不生成行级 AR。
13. **DA-R13** AR 初始 status 为 Unpaid，balance 等于 amount。
14. **DA-R14** 收款挂在 SO，不回写 `ar_records.balance/status`。
15. **DA-R15** 未 Ship 的 DO 仍可 Post AR，页面仅告警。
16. **DA-R16** 建 DO 不扣库存，Ship 才扣。
17. **DA-R17** Complete 后 SO 变 Delivered，Reopen 后 SO 变 Open；AR 不随之变化。
18. **DA-R18** AR/Invoice 打印可使用商业 Invoice 模板，但版式不构成税务凭证。

## 流程

1. SO 生成 Pending DO，并复制总额与行项。
2. 用户可先 Ship；系统扣库存并写 `DO Ship` 台账，但 Post AR 没有硬依赖此步骤。
3. 用户进入 DO Invoice Type A 页面；页面显示 DO 阶段和已有 AR 警告。
4. 用户人工确认后，Inventory 服务调用 Finance Legacy AR 写入。
5. Finance 插入一条 Unpaid `ar_records`，金额和余额均取 DO 总额。
6. 用户可通过 `/print_preview/ar/{id}` 生成 Invoice 版式。
7. 收款在 SO 级建立 receipt 并更新 SO 付款状态，不核销该 AR 行。
8. Complete/Reopen 只改变 DO/SO 状态，不影响 AR。

## 校验

1. **DA-V01** Post AR 前 DO 必须存在。
2. **DA-V02** Type A Post AR 必须人工确认。
3. **DA-V03** Ship 前 DO 必须存在。
4. **DA-V04** Ship 要求 open 阶段。
5. **DA-V05** Ship 要求无重复 ledger。
6. **DA-V06** Ship 要求库存记录存在。
7. **DA-V07** Ship 要求库存充足。
8. **DA-V08** Complete 要求 shipped。
9. **DA-V09** 已 complete 不可重复 Complete。
10. **DA-V10** Reopen 要求 complete。
11. **DA-V11** 查看 Invoice 页面要求 AR.view 或 DO.view。
12. **DA-V12** 确认 Post AR 要求 AR.add 或 DO.edit。
13. **DA-V13** Ship Type A 分别要求 DO view/edit。
14. **DA-V14** 打印要求登录和对应模块打印权限。

缺失：重复 AR 硬阻断、Ship 前置硬门、税/币种校验、AR 与 Receipt 核销校验。

## 数据含义

| 数据 | 含义 |
|---|---|
| `delivery_orders.do_no` | DO 号，同时成为 AR 来源号 |
| `delivery_orders.total_amount` | AR 全额应计来源 |
| `delivery_orders.status` | DO 履约阶段 |
| `delivery_order_items` | Ship 行；Post AR 不形成对应 AR 行 |
| `ar_records.source_no` | 来源 DO 号 |
| `ar_records.ar_no` | 独立 AR 编号列，Post AR 主路径不填 |
| `ar_records.amount` | 应计金额 |
| `ar_records.balance` | 初始等于 amount，收款不自动扣减 |
| `ar_records.status` | 初始 Unpaid |
| `ar_records.ar_date` | 应计日期 |
| `inventory_ledger` 的 DO remark | Ship 幂等依据，与 AR 幂等无关 |
| `receipts.so_id` | 收款锚点在 SO |
| `receipts.amount` | 实收金额，不回写 AR |
| `tax_records` | 独立税务记录 |
| `accounts_receivable` | 规格目标表；运行主表为 `ar_records` |
| `receivables` | 另一遗留应收 schema，DO 链未使用 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Pending` / `待出库` | DO open |
| `已出库` / `Shipped` | DO shipped |
| `Delivered` / `已完成` | DO complete |
| `Unpaid` | 新 AR 状态 |
| `Closed` | Receivable Center 排除的关闭态 |
| `Delivered` | Complete 后 SO 状态 |
| `Open` | Reopen 后 SO 状态 |
| `Human Approved` | Type A 人工确认，不等于税务审核 |

## 双轨 AR 口径

- **`ar_records` 轨：** Post AR 写入，Receivable Center 汇总 balance。
- **SO−Receipts 轨：** AR Dashboard 按客户用 SO 总额减收款，不读取 Post AR 行。
- **`receivables` 遗留轨：** DDL 存在，未见 DO 触发。

因此不同 Finance 页面可能给出不同 AR 数字，不能直接互称同一账本余额。

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | Type A Post AR 路由和权限 | 强 | `apps/inventory/router.py` |
| E2 | Inventory 调用 Finance AR 写入 | 强 | `apps/inventory/services.py` |
| E3 | AR INSERT 字段、金额和状态 | 强 | `apps/finance/services.py` |
| E4 | Finance legacy 路由重定向 | 强 | `apps/finance/router.py` |
| E5 | Platform residual 有静默同名写入 | 强 | `apps/platform/v14_residual.py` |
| E6 | 重复 AR 只是软警告 | 强 | `apps/inventory/services.py` |
| E7 | Ship 扣库存和 ledger | 强 | `apps/inventory/services.py` |
| E8 | Complete/Reopen 不动 AR | 强 | `apps/inventory/services.py` |
| E9 | DO/AR DDL 结构 | 强 | `runtime/v14/legacy_support.py` |
| E10 | Type A gate 覆盖路由、模板和诚实文案 | 强 | `scripts/v18_so_do_invoice_gate.py` |
| E11 | NDE AR Invoice 无行项目 | 中 | `document/nde_engine.py` |
| E12 | 未发现 Receipt 更新 `ar_records` | 强（缺失证据） | `apps/finance/` |

## UNKNOWN

1. **同名 `/create_ar` 的运行 winner UNKNOWN。** 已查 Finance/Platform 路由与 bootstrap，需运行路由表。
2. **`ar_no` 是否由其他路径自动生成 UNKNOWN。** 已查 AR 写入和迁移脚本。
3. **`accounts_receivable` 目标表是否曾在生产存在 UNKNOWN。** 已查 V41 审计与 DDL。
4. **遗留 `receivables` 是否仍有写入口 UNKNOWN。** 已查 DO 链和 Finance repository。
5. **AR Closed/Paid 由谁更新 UNKNOWN。** 已查 Receipt 与全库 `UPDATE ar_records`。
6. **多 DO 对一 SO 的 Receipt 分配规则 UNKNOWN。** 已查 DO AR 与 SO Receipt 链。
7. **DO/AR tenant 隔离是否完整 UNKNOWN。** 已查 V41 patch 与服务 SQL。
8. **税务发票与 AR 的未来衔接点 UNKNOWN。** 已查 Tax Center 和 country templates。
9. **Customs 完成是否应触发 AR UNKNOWN。** 已查 Customs Center 与 GTFIP 交界，当前零耦合。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\platform\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\print_center\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\do_invoice.html`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\upgrade_patch.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\finance.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\shipment.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_SO_DO_Invoice_TypeA_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\v18_so_do_invoice_gate.py`
