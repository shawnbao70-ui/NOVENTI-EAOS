# 端到端回退能力矩阵（End-to-End Reversal Matrix）— Legacy Knowledge

**Evidence strength:** Strong for positive postings and status-only changes; strong negative for coordinated return/reversal orchestration  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与评级

本页横向核对 SO、DO、库存、Inventory Ledger、Receipt、SO payment mirror、`ar_records`、TC commission 与 lifecycle trace 的正向和逆向能力。

- **Strong**：存在活动命令、服务端校验和持久化。
- **Weak**：只能人工/状态补偿，不能绑定原交易或保证对称。
- **Missing**：在规定路径未观察到活动逆向命令/状态机。

## 2. End-to-End Matrix

| Domain fact | Positive path | Reverse/cancel path | Rating | Honest boundary |
|-------------|---------------|---------------------|--------|-----------------|
| Quote→SO | Convert 建 SO/lines/TC | 无 unconvert/delete orchestration | Missing | quote 已确认不可恢复整链 |
| SO status | Approve/Open、Delivery Created、Delivered | 手工 status update/Reopen→Open | Weak | status-only，不反向 posting |
| DO create | SO→DO header/lines | 无 delete/void linked reversal | Missing | 可重开但不是撤销 DO |
| DO Ship | 库存双写 + ledger + Shipped | 无 symmetric unship | Missing | Reopen 不退库 |
| DO Complete | DO Complete + SO Delivered | Reopen DO/SO Open | Strong status / Weak business | 仅状态对称 |
| inventory qty | Ship−qty、Adjust delta | 正数 Adjust 可加回 | Weak | 人工输入，无 source link |
| product stock mirror | Ship/Adjust 同步 delta | Adjust 可加回 | Weak | 无原 Ship 守恒 |
| inventory ledger | DO Ship/Adjustment append | 无 linked reversal entry | Missing | 原 ledger 永久留存 |
| Ship idempotency | stage + ledger remark guard | 无 reversal-aware reset | Missing | Reopen 后仍 already_shipped |
| Receipt | 建 full remaining receipt | 无 void/refund/delete command | Missing | 现金事实不可逆 |
| SO payment mirror | Receipt 后另 commit 更新 | 无 reverse trigger | Missing | receipt/mirror 可部分成功 |
| Operational AR | SO−Receipt live aggregate | 依赖 receipt reversal（缺失） | Missing | 不读 ar_records |
| `ar_records` accrual | DO Post AR positive Unpaid | 无 credit/reverse/cancel writer | Missing | duplicate warning 不阻断 |
| Credit Note | registry/NDE/template | 无 AR posting application | Metadata-only | 文档不等于贷项 |
| TC commission | Convert 写 Pending | 无 void/reverse/update/delete | Missing | SO cancel/Reopen 不联动 |
| lifecycle trace | post-commit best-effort links | 无 unlink/saga compensation | Missing | trace 与业务均可部分 |
| Customer Return/RMA | planned/graph vocabulary | 无 authorization/receipt/disposition | Missing | 非运行主链 |

## 3. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| E2E-R1 | Legacy 正向链由多个独立动作组成 | Convert、Ship、Complete、Post AR、Receipt 各自提交 |
| E2E-R2 | 没有单一 Return/Reversal aggregate | 无统一回退编号 |
| E2E-R3 | SO status 可手工覆盖 | 只改标签，不执行补偿 |
| E2E-R4 | DO Complete 可 Reopen | 只恢复 DO/SO Open |
| E2E-R5 | Reopen 不撤销 Ship | 库存和 ledger 不变 |
| E2E-R6 | 原 Ship ledger 阻断再次 Ship | 状态回退后动作不可重演 |
| E2E-R7 | Inventory Adjust 可补偿数量 | 不引用原 Ship/RMA |
| E2E-R8 | Adjust 不更新 DO/SO/AR/Receipt/TC | 局部补偿 |
| E2E-R9 | Post AR 可重复 | warning 不阻断 |
| E2E-R10 | AR 无 canonical reversal writer | Reopen/return 不减余额 |
| E2E-R11 | Receipt 与 SO mirror 分两次 commit | 可出现收款有、镜像旧 |
| E2E-R12 | Receipt 无 void/refund | Operational AR 无反向来源 |
| E2E-R13 | ar_records 与 SO−Receipt 是平行 AR | 任一局部修改不自动对账 |
| E2E-R14 | Credit Note 仅文档能力 | 无财务影响 |
| E2E-R15 | TC 只写 Pending | 无取消/冲销后继 |
| E2E-R16 | Lifecycle link post-commit best-effort | 无统一 saga |
| E2E-R17 | Return/RMA 主实体缺失 | 无授权与行级守恒 |
| E2E-R18 | 退款、贷项、退库、佣金冲销无顺序政策 | 无法证实先后依赖 |
| E2E-R19 | 每个局部入口使用不同权限名 | 不构成统一 reversal 权限 |
| E2E-R20 | 多个逆向候选是 GET mutation 或手工表单 | 缺不可变批准证据 |
| E2E-R21 | 部分回退不会生成系统级异常状态 | 只能人工发现 |
| E2E-R22 | EAOS 不得以所有状态回到 Open 宣称交易已回退 | 价值与库存事实未还原 |

## 4. Forward / Reverse Sequence

### 4.1 Positive chain

`Quote Convert → SO Pending/Open → DO create → Ship inventory/ledger → Complete → Post AR → Receipt/SO payment mirror`

TC 在 Convert 时写 Pending；lifecycle links 在主 commit 后 best-effort。

### 4.2 Only observable rollback-like actions

1. Reopen DO：DO/SO status 回 Open。
2. Inventory Adjust：人工数量增减。
3. SO status menu：status-only 覆盖。

三者互不编排，也不会自动执行 Receipt refund、AR credit 或 TC reversal。

### 4.3 Expected but missing reverse chain

`Return Authorization → Freeze/validate quantities → Return Receipt & quarantine → reverse inventory ledger → Credit AR → Refund/Apply credit → reverse commission → close DO/SO/RMA → audit`

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| E2E-V1 | Reopen 需 complete DO + edit permission | Hard |
| E2E-V2 | Adjust 非零且不形成负库存 | Hard |
| E2E-V3 | Post AR 需 Human Confirm | Hard |
| E2E-V4 | 同 DO AR 唯一 | Missing |
| E2E-V5 | Return qty ≤ delivered−already returned | Missing |
| E2E-V6 | 每个 reversal 必须引用 original fact | Missing |
| E2E-V7 | inventory/AR/cash/TC 必须同一 reversal scope | Missing |
| E2E-V8 | 退款不得超过净收款 | Missing |
| E2E-V9 | credit 不得超过 open AR | Missing |
| E2E-V10 | commission reversal 必须对应 original TC | Missing |
| E2E-V11 | reversal 需 actor/reason/time/approval | Missing as unified control |
| E2E-V12 | 任一步失败必须 rollback/compensate | Missing |
| E2E-V13 | repeated reversal 必须 idempotent | Missing |
| E2E-V14 | 最终各事实源必须 reconciliation | Missing |

## 6. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| SO status | 流程标签，可 status-only 更新 |
| DO status | open/shipped/complete 标签 |
| Reopen | DO/SO 状态回开 |
| inventory qty | 实际 on-hand 事实之一 |
| product stock | inventory 镜像 |
| inventory ledger | append-like movement history |
| DO Ship ledger | 原出库事实和防重标记 |
| Manual Adjustment | 通用数量补偿 |
| Receipt | 正向客户现金收款 |
| SO payment fields | Receipt 汇总镜像 |
| operational AR | SO total−Receipt sum |
| `ar_records` | DO-sourced正向 accrual |
| Credit Note | 文档元数据/打印 |
| TC Pending | Convert 时 commission snapshot |
| lifecycle links | post-commit traceability |
| RMA | 未建模 |
| reversal ID | 未建模 |
| reversal reason/actor | 无统一模型 |
| returned qty/disposition | 未建模 |
| reconciliation status | 未建模 |

## 7. State Vocabulary

| Domain | Positive states | Reverse states observed |
|--------|-----------------|-------------------------|
| SO | Open/Delivery Created/Delivered | Open label only |
| DO | Open/Shipped/Complete | Reopen→Open |
| Inventory | DO Ship/Adjustment | positive Adjustment only |
| Receipt | created | none |
| AR | Unpaid | Closed vocabulary only; writer UNKNOWN |
| TC | Pending | none |
| RMA | none | none |

## 8. Failure / Partial-Reversal Shapes

| Shape | Facts after action | Risk |
|-------|--------------------|------|
| Reopen only | DO/SO Open; stock, AR, cash, TC unchanged | 运营误认已回退 |
| Adjust only | stock increased; DO/AR/cash/TC unchanged | 无退货授权或财务联动 |
| Duplicate AR | multiple Unpaid rows for same DO | receivable inflation |
| Receipt mirror failure | receipt committed; SO mirror stale | list/detail drift |
| Credit Note print only | 文档存在；AR unchanged | legal/accounting误认 |
| TC unchanged after cancel | Pending commission remains | over-accrual |
| lifecycle partial | business reversed manually, trace unchanged | lineage drift |

## 9. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 完整销售退货/RMA aggregate | sales/inventory/service/runtime DDL |
| unship/reverse ledger 命令 | inventory services/repository/templates |
| Receipt void/refund | finance routes/services/residual/templates |
| AR credit/reversal/write-off | finance repository/service/NDE |
| TC reversal on SO cancel/return | sales/commission/finance |
| 统一 reversal approval/permission | approval/module catalog/routes |
| 部分失败补偿或 saga/outbox | apps/core/v15 workflow/jobs |
| duplicate AR/SO/return 的对账作业 | scripts/reports/schedulers |
| 退回件 lot/serial/quarantine | inventory/quality/GFIP |
| 生产线下流程是否补齐缺失环节 | business modules/reports only；不可由源码证实 |

## 10. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | SO/DO正向与 status-only 更新 |
| `apps/sales/repository.py` | SO/DO/TC facts |
| `apps/inventory/services.py` | Ship/Complete/Reopen/Adjust/Post AR |
| `apps/inventory/repository.py` | inventory dual-write/ledger |
| `apps/inventory/router.py` | reversal-like routes/permissions |
| `apps/finance/services.py` | Receipt/AR positive paths |
| `apps/finance/repository.py` | Receipt separate commits、AR readers |
| `apps/finance/receipt_ar_expense_pages.py` | Finance residual surfaces |
| `runtime/v14/legacy_support.py` | schemas/document registry |
| `v15/business_lifecycle/workflow.py` | post-commit links |
| `apps/service/README.md` | RMA/service planned |
| `document/nde_engine.py` | Credit Note document-only boundary |
| `templates/delivery_order_detail.html` | Reopen and Post AR surfaces |
| `templates/adjust_inventory.html` | Manual compensation |
| `templates/receipts.html` | positive receipt surface |
| `templates/tc_ledger.html` | read-only Pending commission |
| `business_modules/inventory.md` | inventory authority |
| `business_modules/finance.md` | finance spec/runtime boundary |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | delivery behavior |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | Post AR behavior |
| `docs/knowledge/legacy-extract/commission-ledger-deepen/tc_ledger_states.md` | EAOS 只读 TC 交叉引用 |
| `docs/knowledge/legacy-extract/finance/receipts_ar.md` | EAOS 只读 Finance 交叉引用 |
| `docs/knowledge/legacy-extract/fulfillment-deepen/returns_reversal.md` | EAOS 只读 fulfillment 交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后三项为 EAOS 只读交叉引用）。
