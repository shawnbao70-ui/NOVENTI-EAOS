# Convert、Create DO 与 Ship 信用门禁

## Scope与证据强度

本页建立 Quote Approve→Convert→SO Approve→Create DO→DO Ship 的实际门禁矩阵。强结论是各步均不检查 credit_limit、经营余额、AR 逾期或 customer_status；现有硬门禁属于单据、人工确认、库存和幂等。

## 业务规则（稳定ID）

1. **CSG-R01** Quote Approve 只允许 Draft、有行、有效行项且人工确认。
2. **CSG-R02** Quote 库存不足只产生 AI warning，不阻断批准。
3. **CSG-R03** Convert 要求 Quote 存在。
4. **CSG-R04** Convert 先查同 quote_id 的 SO，顺序执行时可防重复。
5. **CSG-R05** Convert 不要求 Quote 已 Sent/Approved。
6. **CSG-R06** Convert 不查客户信用、余额、逾期或状态。
7. **CSG-R07** Convert 成功后建 pending_delivery/uncollected SO 并确认 Quote。
8. **CSG-R08** Convert 页面按钮按 Sales Orders/add 隐藏，但路由无服务端 RBAC。
9. **CSG-R09** SO Approve 要求 pending stage、有行和 human_confirm。
10. **CSG-R10** SO Approve 不查客户信用、余额、逾期或状态。
11. **CSG-R11** Create DO 只要求 SO 存在。
12. **CSG-R12** Create DO 不要求 SO=Open。
13. **CSG-R13** Create DO 不查客户信用、余额、逾期或状态。
14. **CSG-R14** Create DO 不预留或扣减库存。
15. **CSG-R15** Create DO 无同 SO 幂等，可重复创建 DO。
16. **CSG-R16** Create DO 按钮按 Delivery Orders/add 隐藏，但路由无服务端 RBAC。
17. **CSG-R17** Ship 要求 DO 存在且归一状态为 open。
18. **CSG-R18** Ship 拒绝已 shipped/complete。
19. **CSG-R19** Ship 检查 DO Ship ledger，形成二次幂等防线。
20. **CSG-R20** Ship 对每行硬检库存存在且 on_hand≥qty。
21. **CSG-R21** Ship 要求 human_confirm 且 POST 需要 Delivery Orders/edit。
22. **CSG-R22** Ship 不查客户信用、余额、逾期或状态。
23. **CSG-R23** Ship 不创建 AR；AR 在独立 DO invoice/Post AR 步骤。
24. **CSG-R24** 主 AR 结构未提供 day-aging 驱动的 Ship gate。

## 流程

| 步骤 | 信用/余额/逾期/客户态 | 实际硬门禁 | 权限 |
|---|---|---|---|
| Quote Approve | 均不查 | Draft、行项、qty/price、human_confirm | Quotes edit/approve |
| Convert Quote→SO | 均不查 | Quote 存在、顺序幂等 | UI add；路由缺 RBAC |
| SO Approve | 均不查 | pending、有行、human_confirm | view/edit |
| Create DO | 均不查 | SO 存在 | UI add；路由缺 RBAC |
| DO Ship | 均不查 | open、未发运、ledger、库存、human_confirm | view/edit |

## 校验（强/弱/缺失）

1. **CSG-V01（强）** Quote Approve 仅 Draft。
2. **CSG-V02（强）** Quote Approve 至少一行且 qty>0、price≥0。
3. **CSG-V03（强）** Quote/SO/Ship 不可逆动作要求 human_confirm。
4. **CSG-V04（强）** Convert 要求 Quote 存在。
5. **CSG-V05（强/顺序）** Convert 先查 SO quote_id 防重复。
6. **CSG-V06（缺失）** Convert 不要求 Quote approved。
7. **CSG-V07（缺失）** Convert 服务端 RBAC 缺失。
8. **CSG-V08（强）** SO Approve 仅 pending 且有行。
9. **CSG-V09（强）** Create DO 要求 SO 存在。
10. **CSG-V10（缺失）** Create DO 不要求 SO Open。
11. **CSG-V11（缺失）** Create DO 无幂等和服务端 RBAC。
12. **CSG-V12（强）** Ship 要求 open 且未完成。
13. **CSG-V13（强）** Ship 通过 ledger 检查重复。
14. **CSG-V14（强）** Ship 要求库存行存在且足量。
15. **CSG-V15（缺失）** 所有步骤都无信用额度 gate。
16. **CSG-V16（缺失）** 所有步骤都无 AR overdue gate。
17. **CSG-V17（缺失）** 所有步骤都无客户暂停/失效 gate。
18. **CSG-V18（缺失）** 多 DO 累计发货未对 SO 数量上限复核。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.status` | Quote 工作流标签；Convert 不要求特定值 |
| `sales_orders.quote_id` | Quote→SO 追溯与顺序幂等键 |
| `sales_orders.status` | pending/Open/Delivery Created 等 |
| `payment_status` | uncollected/Partial/Paid，不阻断 DO |
| `sales_orders.total_amount` | 经营余额分子，不执行 gate |
| `delivery_orders.status` | Pending/open/已出库/Delivered |
| `human_confirm` | Type A 人工确认标志 |
| `can_approve` | 模板按钮条件，不是信用条件 |
| `inventory.stock_qty` | Ship 硬检库存来源 |
| `products.stock_qty` | Ship 同步更新的产品库存 |
| `inventory_ledger.trans_type` | `DO Ship` 过账类型 |
| `inventory_ledger.remark` | `DO-{do_no}` 幂等匹配 |
| `ar_records` | DO invoice 后创建的应收 |
| `ar_records.balance` | 独立台账余额，不阻断 Ship |
| Customer balance | SO−Receipt 展示余额 |
| `credit_limit` | 未进入流程的预留字段 |
| `customer_status` | 未进入流程的 CRM 标签 |
| `insufficient_stock` | Ship 的库存硬拒绝 |

## 状态词汇

| 对象 | 词汇 |
|---|---|
| Quote | Draft、Sent、已确认 |
| SO | pending_delivery、Open、Delivery Created |
| DO | Pending/open、已出库、Delivered |
| Payment | uncollected、Partial、Paid |
| 信用 | 无 Credit Hold/Override 执行态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CSG-E01 | Quote Approve 校验无信用查询 | 强 | `apps/quotation/services.py` |
| CSG-E02 | Convert 仅查 Quote 与重复 SO | 强 | `apps/sales/services.py` |
| CSG-E03 | Convert 路由无 has_permission | 强 | `apps/sales/router.py` |
| CSG-E04 | SO Approve 只查阶段、行、确认 | 强 | `apps/sales/services.py` |
| CSG-E05 | Create DO 只查 SO 且不减库存 | 强 | `apps/sales/services.py` |
| CSG-E06 | Create DO 路由无服务端 RBAC | 强 | `apps/sales/router.py` |
| CSG-E07 | Ship 状态、ledger、库存硬门禁 | 强 | `apps/inventory/services.py`、`repository.py` |
| CSG-E08 | Quote Convert UI 权限/confirm | 弱/UI | `templates/quotes.html` |
| CSG-E09 | A-003 说明 Create DO 不减库存 | 强 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |
| CSG-E10 | A-013 说明 Convert UI confirm | 强 | `docs/reports/Business_Strong_A013_Quote_Ops_Report.md` |
| CSG-E11 | A-015 说明 credit heuristic | 强 | `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **Convert 双路由实际匹配顺序 UNKNOWN。** 已查路径：sales router、quotation quote_pages、bootstrap。
2. **Create DO 与 v14 residual 双注册优先级 UNKNOWN。** 已查路径：sales router、platform residual、bootstrap。
3. **全局 middleware 是否补足未守卫路由 RBAC UNKNOWN。** 已查路径：security middleware、route handlers。
4. **主 AR 是否有外部 day-aging 作业 UNKNOWN。** 已查路径：Finance、jobs、reports、schema。
5. **GFIP/LC 是否外部阻断 Ship UNKNOWN。** 已查路径：v15 integration modules、Inventory Ship。
6. **生产数据是否存在 Paused/Invalid 状态 UNKNOWN。** 已查路径：Customer forms/locales/schema。
7. **Create DO 是否业务上应要求 SO Open UNKNOWN。** 已查路径：V18 design、business_modules/sales。
8. **多 DO 累计 Ship 是否允许超过 SO qty UNKNOWN。** 已查路径：Create DO、Ship loops。
9. **信用余额币种与折算政策 UNKNOWN。** 已查路径：Quote/SO/Receipt/Customer aggregate。
10. **是否有离线人工信用复核 UNKNOWN。** 已查路径：Approval Center、reports、business_modules。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
