# 期间重估 / 期末关账证据

## Scope 与结论

本页回答：Legacy 是否存在外币**期间重估**作业，以及**会计期末关账**实体是否与重估绑定。交叉引用 [`../fx-revaluation-deepen/revaluation_job.md`](../fx-revaluation-deepen/revaluation_job.md)、[`../locale-commerce/currency.md`](../locale-commerce/currency.md)、[`../finance/README.md`](../finance/README.md)。

**可确认硬结论：** 对 `apps/finance/`、`runtime` DDL、`business_modules/`、`templates/`、`docs/reports/`、`core/capabilities/currency/` 定向检索，`revaluation` / `period_close` / `fiscal_period` / `accounting_period` / `unrealized` / `汇兑` / `重估` / `关账` **零活动命中**。`business_modules/finance.md` 自称 “financial close authority”，但 Owned Routes/交付物未列重估或期间关闭。唯一相近实体 `commission_periods` 为销售佣金期间，不是会计关账。EOC exchange risk 为展示启发式。故期间重估与期末关账在 Legacy 为**强缺口**。

## 业务规则（稳定 ID）

1. **PRC-R01** 未观察到名为 revaluation / FX revalue / 期末调汇的路由、页面或服务方法。
2. **PRC-R02** 未观察到按日/按月批量重估调度任务绑定 `currency_settings`。
3. **PRC-R03** 未观察到 `accounting_period` / `fiscal_period` / `period_close` 财务实体。
4. **PRC-R04** 存在 `commission_periods`（period_name/start/end/status），语义为佣金期间，非 GL 关账。
5. **PRC-R05** `currency_settings.exchange_rate` 变更（若发生）无敞口重算引擎可触发——维护路径本身亦缺口。
6. **PRC-R06** AR/AP/`receipts`/资金账户无“重估后本位币余额”列。
7. **PRC-R07** 资金账户 `current_balance` 不因期末汇率调整而改写。
8. **PRC-R08** 未观察到 journal / GL entry 表与期间重估联动。
9. **PRC-R09** `profit_snapshots` 表名存在于 finance DDL 邻域，未见 FX 重估字段消费路径。
10. **PRC-R10** `business_modules/finance.md` 列出发票/收付/报表职责与 close authority 叙述，**未**列重估或 period-close 交付物。
11. **PRC-R11** Finance Owned Routes 含 invoices/payments/AR/AP/reports，无 `/revalue`、`/period_close` 类路径。
12. **PRC-R12** Scheduler/批处理文档描述通用队列，未绑定 FX 重估任务定义。
13. **PRC-R13** GTFIP 等报告可保留 “exchange rates” 外部接口叙述，属保留插口，非已实现期末作业。
14. **PRC-R14** `core/capabilities/currency` 仅 health/bridge，无 revalue API。
15. **PRC-R15** EOC `_exchange_risk_score`（若存在）为离散度启发式分数，不是会计重估分录。
16. **PRC-R16** 传播链上游 Quote FX 快照与收付硬编码亦不构成期末重估价源队列。
17. **PRC-R17** 因此：不得将 Finance “close authority” 规格意图迁移为已交付关账+重估能力。
18. **PRC-R18** 与邻包 `revaluation_job.md` 结论一致并加深：关账实体与重估作业在传播视角仍为零证据。

## 校验（强 / 弱 / 缺失）

1. **PRC-V01（强缺口）** 重估前会计期间必须 Open——无期间状态机。
2. **PRC-V02（缺失）** 重估汇率必须带生效日且取期末日。
3. **PRC-V03（缺失）** 仅货币性项目参与重估。
4. **PRC-V04（缺失）** 重估分录借贷平衡。
5. **PRC-V05（缺失）** 重复运行重估幂等或先冲销再跑。
6. **PRC-V06（缺失）** 已关账期间禁止重跑或改汇率。
7. **PRC-V07（缺失）** 重估后 AR/AP/现金本位币与台账勾稽。
8. **PRC-V08（缺失）** 关账检查清单含未过账收付/未重估外币。
9. **PRC-V09（弱/规格）** 模块叙述 “close authority” 不构成可执行校验。
10. **PRC-V10（缺失）** 多账套/多公司分别关账与重估。
11. **PRC-V11（缺失）** 重估损益过账权限与审批。
12. **PRC-V12（弱/展示）** EOC 风险分缺汇率时给默认值，非会计控制。

## 数据含义

| 数据 / 概念 | Legacy 含义 |
|---|---|
| Revaluation job | **未建模** |
| Accounting period / period close | **财务关账实体未观察到** |
| `commission_periods` | 佣金期间（name/start/end/status），非 FX/GL 关账 |
| `currency_settings.exchange_rate` | 配置/展示用数值，非期末重估价队列 |
| Unrealized FX（期间） | **未建模**（详见 realized_unrealized_fx.md） |
| Journal / GL entry（重估） | **未观察到** |
| `profit_snapshots` | 利润快照类表名线索；无 FX 重估字段证据 |
| AR/AP `amount`/`balance` | 原始记账金额，非重估后本位币 |
| Bank/cash `current_balance` | 账户币余额，无期末调汇 |
| Finance “close authority” | 模块规格意图，≠ 已实现关账+重估 |
| Scheduler job（通用） | 平台队列概念；无 FX 任务绑定证据 |
| GTFIP exchange-rate plug-in | 文档保留接口，非运行作业 |
| EOC exchange risk score | 仪表盘启发式，非敞口重估结果 |
| Quote/SO/Receipt FX 快照链 | 传播断裂；不能充当期间重估价源 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| PRC-E01 | finance py 无 revaluat/period_close/unrealized 命中 | 强缺口 | `apps/finance/**/*.py` 检索 |
| PRC-E02 | 全库 py/html/md/sql 无 revaluation/汇兑/关账作业命中 | 强缺口 | 工作区定向检索 |
| PRC-E03 | finance 模块规格无重估/关账表与路由 | 强 | `business_modules/finance.md` |
| PRC-E04 | commission_periods 属销售佣金 | 强 | `runtime/v14/legacy_support.py` DDL；sales 佣金路径 |
| PRC-E05 | currency capability 无作业 API | 强 | `core/capabilities/currency/` |
| PRC-E06 | AR/AP/资金 DDL 无重估列 | 强 | `legacy_support.py` |
| PRC-E07 | Scheduler 报告无 FX 任务 | 中 | `docs/reports/` Scheduler 相关 |
| PRC-E08 | GTFIP 保留汇率接口叙述 | 中 | `docs/reports/GTFIP.md`（若存）/相关报告 |
| PRC-E09 | 邻包重估页已标强缺口 | 强 | [`../fx-revaluation-deepen/revaluation_job.md`](../fx-revaluation-deepen/revaluation_job.md) |
| PRC-E10 | locale-commerce 已标重估未证实 | 强 | [`../locale-commerce/currency.md`](../locale-commerce/currency.md) |
| PRC-E11 | 无 jobs/ 批处理目录承载 FX | 中 | 仓库根 jobs 检索 |
| PRC-E12 | Enterprise readiness 等报告谈 treasury/ledger 缺口，无 period FX close | 中 | `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` 等 |

## UNKNOWN + 已查路径

1. **线下是否用 Excel 做月末调汇 UNKNOWN。** 已查：apps/finance、templates、docs/reports；无“重估工作底稿”专用导出。
2. **外部会计/ERP 是否承接关账 UNKNOWN。** 已查：business_modules、integration 叙述、finance 依赖。
3. **`profit_snapshots` 是否含隐藏 FX 字段 UNKNOWN。** 已查：DDL 邻域命名、finance services 引用；未见重估列消费。
4. **多账套关账是否在 tenant 层另有表 UNKNOWN。** 已查：tenant/runtime 期间相关名检索。
5. **佣金期间关闭是否在组织用语上被误称“关账” UNKNOWN。** 已查：`commission_periods` DDL、销售佣金页面/残余路由。
6. **未来插件是否计划实现重估 UNKNOWN。** 已查：docs/reports 保留接口与 excellence 列表；无实现代码。
7. **人工改字典汇率后是否有人用报表重算敞口 UNKNOWN。** 已查：financial_reports 路由叙述、FX 关键字、report_center。

## 只读来源路径

`apps/finance/` · `apps/sales/` · `runtime/v14/legacy_support.py` · `core/capabilities/currency/` · `business_modules/finance.md` · `docs/reports/` · `templates/` · `v15/template_services/` · 邻包 fx-revaluation-deepen / locale-commerce / finance（只读）
