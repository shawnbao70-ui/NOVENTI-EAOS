# 转单佣金事务边界（Commission Atomicity）— Legacy Knowledge

**Evidence strength:** Strong for statement order, shared connection and commit point; mixed for exception rollback and connection lifecycle  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页聚焦 canonical Quote→SO 中 SO header、`tc_ledger`、SO items、quote status 的事务关系。正常路径四类 SQL 使用同一 repository connection，并由最后的 quote 状态更新执行 commit；但 TC helper 宽泛吞异常，所以业务契约允许“SO 成功、佣金缺失”。异常时没有显式 rollback、失败记录或补偿。

佣金计算/费率语义交叉引用 `../commission-ledger-deepen/commission_on_convert.md`。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| CA-R1 | canonical Convert 先插 SO header | TC 依赖新 SO ID |
| CA-R2 | SO insert 本身不 commit | 正常时等待后续统一提交点 |
| CA-R3 | TC helper 紧接 SO header 执行 | 早于 items 和 quote 写回 |
| CA-R4 | TC 从已插 SO 读取 salesperson/total | 使用同 connection 的未提交行 |
| CA-R5 | 有 salesperson 才尝试写 TC | 缺 salesperson 时静默跳过 |
| CA-R6 | 无等级时费率退为 0 | 仍可写零佣金 Pending |
| CA-R7 | TC insert 自身不 commit | 正常时与 SO/items/quote 同批提交 |
| CA-R8 | TC helper 捕获所有异常并继续 | TC 不是 Convert 成功条件 |
| CA-R9 | TC 后复制 quote items | 失败时未见显式 rollback |
| CA-R10 | 最后 quote 更新为已确认并 commit | canonical 主 SQL 正常提交点 |
| CA-R11 | 正常成功时 SO、TC、items、quote 状态共同提交 | 基于同 connection 与单一可见 commit |
| CA-R12 | “同事务”不等于“佣金必有” | helper 可以不写或失败被吞 |
| CA-R13 | TC schema 无 source 唯一约束 | 并发双 SO 可产生重复台账 |
| CA-R14 | source_no 是 SO number 文本 | 不以 SO ID/quote ID 约束 |
| CA-R15 | commission rate/amount 是 Convert 时快照 | 后改等级不重算 |
| CA-R16 | SO 取消/退货/改额不自动冲销 TC | 业务后续不原子 |
| CA-R17 | 未见漏记扫描、重试队列或 outbox | 静默缺口可能长期存在 |
| CA-R18 | legacy Quotation 副本也内联计佣 | 标准运行通常被 route filter 跳过 |
| CA-R19 | legacy 副本异常输出与 canonical 静默策略不同 | 双实现的可观测性漂移 |
| CA-R20 | Convert 成功 redirect 不证明 TC 存在 | 必须分别核验 |
| CA-R21 | commission calculator 使用平行表/口径 | 不补 canonical TC |
| CA-R22 | EAOS 不得把 Pending TC 解释为已批准或已发放 | Finance 支付链未接 |
| CA-R23 | 未观察到活动 `UPDATE`/`DELETE tc_ledger` 状态路径 | Convert 快照缺少后继状态机 |
| CA-R24 | Finance 应用未观察到读写 canonical `tc_ledger` | 无佣金对账或付款闭环 |

## 3. Process 与原子边界

### 3.1 正常路径

1. Insert SO header，不 commit。
2. Read new SO；尝试计算并 insert Pending TC，不 commit。
3. 复制所有 quote items，不 commit。
4. Update quote status to `已确认`。
5. Repository commit：提交前述成功 SQL。
6. 主 commit 后再执行 lifecycle hook。

### 3.2 TC 失败路径

1. SO header 已在当前 connection。
2. TC 读取/计算/insert 抛异常或无 salesperson。
3. helper 吞异常或跳过。
4. items 和 quote status 继续。
5. commit 产生无 TC 的 SO。

### 3.3 Items/quote 失败路径

异常会离开 Convert；代码未观察到显式 rollback。未提交 statement 最终如何清理取决于 connection/request 生命周期，标为 UNKNOWN，不能声称已可靠回滚。

## 4. Validation

| ID | Validation | Strength |
|----|------------|----------|
| CA-V1 | quote 存在且无既有 SO | Hard upstream |
| CA-V2 | TC 仅在 salesperson 存在时尝试 | Hard branch |
| CA-V3 | commission rate 在 0–100 | Missing |
| CA-V4 | sales amount 必须为正 | Missing |
| CA-V5 | source_type/source_no 唯一 | Missing |
| CA-V6 | SO 成功必须恰有一条 TC | Missing |
| CA-V7 | TC 失败必须阻断/rollback SO | Missing by design |
| CA-V8 | TC 失败必须写 durable failure | Missing |
| CA-V9 | 整个 Convert 异常必须显式 rollback | Missing |
| CA-V10 | TC 必须保存 currency/rule version | Missing |
| CA-V11 | SO 取消/改额必须冲销或重算 | Missing |
| CA-V12 | 漏记和重复台账必须可对账 | Missing |

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.id` | 已插订单主键；TC 不保存该 FK |
| `sales_orders.so_no` | TC 的弱文本来源号 |
| `sales_orders.salesperson_id` | 受益人来源 |
| `sales_orders.total_amount` | commission base |
| `sales_levels.commission_rate` | Convert 时读取的执行费率 |
| `tc_ledger.salesperson_id` | 台账归属 |
| `tc_ledger.source_type` | 固定 Sales Order |
| `tc_ledger.source_no` | SO number 文本 |
| `tc_ledger.sales_amount` | 订单额快照 |
| `tc_ledger.commission_rate` | 等级费率快照 |
| `tc_ledger.commission_amount` | 两位小数计算结果 |
| `tc_ledger.status=Pending` | 待处理标签，不是支付事实 |
| `tc_ledger.create_time` | helper 执行时间 |
| repository connection | SO/TC/items/quote 共用的 SQL 会话 |
| quote status commit | canonical 主 SQL commit 点 |
| missing TC | 可由无 salesperson 或静默异常产生 |
| zero TC | 有台账但 amount=0 |
| duplicate TC | source 无 unique 导致的并发风险 |
| commission currency | 未持久化 |
| failure event | 未建模 |
| Finance settlement link | 未建模 |
| TC reversal | 未建模 |

## 6. State Vocabulary

| State / term | Meaning |
|--------------|---------|
| Pending | 新 TC 唯一可证状态 |
| missing ledger | SO 有效、TC 不存在 |
| zero commission | TC 存在但费率/金额为零 |
| duplicate ledger | 同源文本多行，无专用标志 |
| committed SO | 不等于 commission complete |
| paid/approved | canonical TC 未观察到活动转换 |

## 7. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| TC statement 抛错后 SQLite transaction 的请求级最终处理 | sales service/repository、core database/context |
| 未提交异常请求是否自动 rollback/close | middleware/dependencies/runtime globals |
| 生产 tc_ledger 是否手工加 source unique | runtime DDL、database migrations |
| 漏记 TC 是否有日志或告警 | sales service、audit/log、reports |
| 漏记/重复佣金对账作业 | scheduler/jobs/finance/commission paths |
| SO 取消/退货后的冲销政策 | sales/inventory/finance flows |
| SO 改额后的重算政策 | sales update/history、tc_ledger writers |
| commission currency 的正式来源 | quote currency、SO schema、Finance |
| 零佣金 Pending 是否是有意审计记录 | templates/reports/business modules |

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 写入顺序、helper 异常吞并 |
| `apps/sales/repository.py` | SO/TC/items insert 与 quote commit |
| `apps/sales/router.py` | canonical Convert 入口 |
| `apps/quotation/quote_pages.py` | legacy 平行 TC 写入 |
| `apps/quotation/v14_residual.py` | legacy route source |
| `runtime/v14/legacy_support.py` | TC/SO schemas 与 constraints |
| `core/database/context.py` | connection/transaction 边界核对 |
| `core/database/repository_base.py` | repository connection 语义 |
| `templates/tc_ledger.html` | TC 展示字段与状态 |
| `apps/sales/v14_residual.py` | commission calculator/ledger surface |
| `apps/finance/` | 未消费 canonical TC 的负向证据 |
| `templates/commission_calculator.html` | 平行计算口径 |
| `bootstrap/v14_residual.py` | canonical/residual route 去重 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Convert owner/链路 |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | commission 成熟度边界 |
| `docs/knowledge/legacy-extract/commission-ledger-deepen/commission_on_convert.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/commission-ledger-deepen/tc_ledger_states.md` | EAOS TC 状态交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
