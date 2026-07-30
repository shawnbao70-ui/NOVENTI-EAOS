# 转销售订单时佣金写入（Commission on Convert）— Legacy Knowledge

**Evidence strength:** Strong for canonical Sales calculation/write; mixed for transactionality and duplicate conversion surfaces  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块只描述 Quote→SO 转换期间向 `tc_ledger` 写入销售佣金的活动路径。销售订单总体规则见 `../sales/sales_order.md`，结算总览见 `../finance/settlement-rules.md`；此处深化写入顺序、计算快照、失败边界和幂等缺口。

Canonical `apps/sales` 服务与 repository 证据强。正常 SQL 步骤共用 connection，并在报价状态更新时提交；但佣金钩子被宽泛异常处理包围，失败后 SO 与订单行仍会提交。lifecycle link 位于该提交之后且独立 best-effort，因此“SO 已创建”不能证明佣金已记录。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| COC-R1 | 佣金钩子由 canonical Quote→SO 转换触发 | 不是收款、发货或关账触发 |
| COC-R2 | SO header 插入后立即尝试佣金写入 | 行项目复制和报价状态回写发生在后 |
| COC-R3 | 佣金归属取新 SO 的 `salesperson_id` | 不从当前操作者或客户 owner 推导 |
| COC-R4 | 佣金基数取 SO header `total_amount` | 不取已收款额或毛利 |
| COC-R5 | 费率取业务员所属 `sales_levels.commission_rate` | Commission Center rule 不参与 |
| COC-R6 | 金额为销售额乘费率百分比并四舍五入两位 | 未观察到税和币种转换 |
| COC-R7 | 台账来源类型固定 `Sales Order` | 不是 Quote、Receipt 或 Invoice |
| COC-R8 | 来源号保存 SO number | 不是 SO ID 外键 |
| COC-R9 | 新台账状态固定 `Pending` | 未观察到自动批准 |
| COC-R10 | 无 salesperson 时跳过台账写入 | SO 仍继续创建 |
| COC-R11 | 查不到等级时费率退化为零 | 仍可能写零佣金 Pending 行 |
| COC-R12 | 佣金计算或写入异常被静默忽略 | 不阻断转换，也无用户提示 |
| COC-R13 | canonical 一报价一单 guard 间接降低重复佣金 | 仅应用层先查后写 |
| COC-R14 | `tc_ledger` 未见 source 唯一约束 | 并发或其他入口仍可能重复 |
| COC-R15 | legacy Quotation 转换副本也内联写 TC，但失败只输出到 stdout，且无 lifecycle link | 运行时冲突路由通常由 canonical Sales 优先 |
| COC-R16 | 佣金费率与金额在写入时形成快照 | 后改职级不自动重算旧行 |
| COC-R17 | SO 取消、退货、改单未见自动冲销佣金 | Pending 行可脱离商业现状 |
| COC-R18 | 收款不会重新计算 canonical `tc_ledger` | 并行 calculator 才按收款额演示 |
| COC-R19 | 台账写入没有 actor、quote ID、SO ID、currency 或 rule ID | 可追溯性依赖弱文本键 |
| COC-R20 | EAOS 不得把转换成功视为佣金成功 | 必须分别核验订单与台账结果 |
| COC-R21 | 正常路径的 SO、TC、行和 quote 更新在同一 connection 上于 quote 状态更新时提交 | 钩子失败被吞后仍提交无 TC 的 SO |
| COC-R22 | Convert route 无服务端 RBAC，UI 仅以 Sales Orders add 隐藏按钮 | 可直链触发 GET mutation |

---

## 3. Process

### 3.1 Canonical 转换钩子

1. 校验 quote 存在且未有 SO。
2. 插入 SO header，得到 SO ID 与 SO number。
3. 读取 SO salesperson 与 total amount。
4. 若 salesperson 存在，则左连接其 level 并读取 commission rate。
5. 计算两位小数佣金，写 `tc_ledger` Pending 行。
6. 无论钩子成功与否，继续复制行、更新 quote 状态并尝试 lifecycle link。

### 3.2 失败与修复边界

钩子错误无告警、无失败记录、无自动重试。未观察到从现有 SO 扫描漏记佣金并补账的活动作业，也未观察到取消 SO 后反向冲销。

### 3.3 与演示 calculator 的区别

Commission calculator 另写 `salesperson_commissions`，使用固定样例和已收金额计算。它不更新、批准或替代 canonical `tc_ledger`。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| COC-V1 | quote 必须存在 | Hard upstream | |
| COC-V2 | quote 不得已有 SO | Hard application guard | 非 DB 唯一 |
| COC-V3 | SO 必须有 salesperson 才尝试计佣 | Hard branch | 缺失则静默跳过 |
| COC-V4 | salesperson.level_id 必须有效 | Weak | 无等级退化为 0 |
| COC-V5 | commission rate 必须在 0–100 | Missing | 无范围校验 |
| COC-V6 | sales amount 必须为正 | Missing | 零或负金额未阻止 |
| COC-V7 | 同 source_type/source_no 只能一条有效台账 | Missing | 无唯一约束/查重 |
| COC-V8 | SO 与台账业务结果必须一致 | Missing | 同批提交仍允许钩子失败后提交无 TC 的 SO |
| COC-V9 | 佣金失败必须可见可重试 | Missing | 异常被吞 |
| COC-V10 | source_no 必须对应实际 SO | Weak | 文本，无 FK |
| COC-V11 | 订单取消必须冲销台账 | Missing | 无反向事件 |
| COC-V12 | 计算必须保存币种/规则版本 | Missing | schema 无字段 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.id` | 新订单主键；未写入 TC ledger |
| `sales_orders.so_no` | 台账弱来源键 |
| `sales_orders.salesperson_id` | 佣金受益人来源 |
| `sales_orders.total_amount` | canonical 佣金计算基数 |
| `salespersons.level_id` | 业务员到费率等级的关联 |
| `sales_levels.commission_rate` | canonical 执行费率，百分比 |
| `tc_ledger.salesperson_id` | 台账归属销售员 |
| `tc_ledger.source_type` | canonical 固定 `Sales Order` |
| `tc_ledger.source_no` | SO number 文本 |
| `tc_ledger.sales_amount` | 计算时订单总额快照 |
| `tc_ledger.commission_rate` | 计算时等级费率快照 |
| `tc_ledger.commission_amount` | 两位小数计算结果 |
| `tc_ledger.status` | 初始 Pending；非付款证明 |
| `tc_ledger.create_time` | 钩子执行时间 |
| `salesperson_commissions` | 收款额演示计算的平行表 |
| commission currency | UNKNOWN；台账不保存 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Pending | 转换新建 TC 行的唯一可证状态 |
| Active | salesperson/level 可用标签，不是台账状态 |
| Converted | 由 SO 存在推导，不是佣金状态 |
| Missing ledger | 可能由无 salesperson、异常或并发失败造成 |
| Zero commission | 费率缺失退化为零后仍可能有台账 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| `tc_ledger` 是否有生产环境唯一索引 | runtime/v14 DDL、database migrations、sales repository |
| 钩子失败是否有日志、告警或补偿作业 | sales service、audit/log paths、scheduler、reports |
| 双转换入口的实际佣金行为是否完全一致 | sales canonical、quotation legacy、bootstrap route ownership |
| SO 取消/退货后佣金如何冲销 | sales status、inventory returns、finance commission paths |
| SO 金额修改后是否重算旧台账 | sales update/history、tc_ledger update searches |
| 台账币种应来自 Quote 还是企业本位币 | quotation currency、sales schema、finance/locale paths |
| 零费率 Pending 行是否为有意记录 | sales service、commission templates、reports |
| 佣金应在订单、发货、开 AR 还是回款时确认 | sales/finance/inventory flows、business modules |
| 漏记 SO 的人工补账入口 | commission center、TC ledger template/routes；未见 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 转换顺序、计算、静默异常 |
| `apps/sales/repository.py` | 费率查询与 TC ledger insert |
| `apps/sales/router.py` | canonical convert 路由与权限缺口 |
| `apps/sales/v14_residual.py` | Commission surfaces 与 calculator |
| `apps/quotation/quote_pages.py` | 平行转换实现 |
| `apps/quotation/services.py` | Quote Approve 与 Convert 分离 |
| `runtime/v14/legacy_support.py` | tc_ledger、levels、parallel tables DDL |
| `templates/tc_ledger.html` | 台账只读字段 |
| `templates/commission_calculator.html` | 平行收款口径表面 |
| `Business_Module_Registry.md` | Sales/Finance 双重边界声明 |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | Commission 未达到生产结算成熟度 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Quote→SO 链与 owner |
| `docs/knowledge/legacy-extract/sales/sales_order.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/finance/settlement-rules.md` | EAOS 只读结算总览 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
