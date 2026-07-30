# 重估作业 / 期间有无

## Scope 与结论

本页回答：Legacy 是否存在外币重估（revaluation）、未实现/已实现汇兑损益确认、以及会计期间关闭与重估的绑定。对 `apps/finance/`、`core/capabilities/currency/`、`runtime` DDL、`business_modules/`、`docs/reports/`、`templates/` 的定向检索结果为：**零命中** `revaluation` / `exchange gain` / `unrealized` / `fx difference` / `汇兑` / `重估` 等活动实现。Finance 模块规格自称 close authority，但未列出重估作业、期间实体或 GL 分录表。EOC 的 “exchange risk score” 是展示启发式，不是会计重估。

交叉引用：[`../finance/README.md`](../finance/README.md)、[`../locale-commerce/currency.md`](../locale-commerce/currency.md)。

## 业务规则（稳定 ID）

1. **REV-R01** 未观察到名为 revaluation / FX revalue / 期末调汇的作业入口或路由。
2. **REV-R02** 未观察到按日/按月批量重估调度器绑定币种字典。
3. **REV-R03** 未观察到 `accounting_period` / `fiscal_period` / `period_close` 财务实体驱动重估。
4. **REV-R04** 销售侧存在 `commission_periods`，语义为佣金期间，不是会计关账期间。
5. **REV-R05** 未观察到未实现汇兑损益（unrealized FX）科目或台账表。
6. **REV-R06** 未观察到已实现汇兑损益在收付款清账时自动确认。
7. **REV-R07** 未观察到 journal / GL entry 表与外币重估联动。
8. **REV-R08** `currency_settings.exchange_rate` 变更（若发生）不会触发敞口重算——因无活动维护路径与无敞口引擎。
9. **REV-R09** AR/AP 余额字段为原记金额口径，无“重估后本位币余额”列。
10. **REV-R10** 资金账户余额不因期末汇率调整而改写。
11. **REV-R11** EOC `_exchange_risk_score` 用非基准汇率离散度生成 0–65 启发式分数，仅供仪表盘风险展示。
12. **REV-R12** `business_modules/finance.md` 列出发票/收付/报表职责，未列重估或期间关闭交付物。
13. **REV-R13** Scheduler 中心文档描述通用队列能力，未绑定 FX 重估任务定义。
14. **REV-R14** GTFIP 文档保留 “exchange rates” 外部接口叙述，属保留插口，不是已实现作业。
15. **REV-R15** `apps/finance/` 内对 scheduler/cron/job/journal/gl_/revaluat 的代码检索无活动命中。
16. **REV-R16** 因此：期末重估与关账在 Legacy 中应记为**强缺口**，不得迁移为已交付能力。

## 校验（强 / 弱 / 缺失）

1. **REV-V01（强缺口）** 重估前期间必须 Open——无期间状态机可校验。
2. **REV-V02（缺失）** 重估汇率必须带生效日且取期末日。
3. **REV-V03（缺失）** 仅货币性项目参与重估。
4. **REV-V04（缺失）** 重估分录借贷平衡。
5. **REV-V05（缺失）** 重复运行重估幂等或冲销后再跑。
6. **REV-V06（缺失）** 已关账期间禁止重跑。
7. **REV-V07（缺失）** 重估后 AR/AP/现金本位币与台账勾稽。
8. **REV-V08（弱/展示）** EOC 在无汇率时给默认风险分，不构成会计控制。
9. **REV-V09（缺失）** 重估损益过账权限与审批。
10. **REV-V10（缺失）** 多账套/多公司分别关账。

## 数据含义

| 数据 / 概念 | Legacy 含义 |
|---|---|
| Revaluation job | **未建模** |
| Accounting period / period close | **财务关账实体未观察到** |
| `commission_periods` | 佣金期间，非 FX/GL 关账 |
| Unrealized FX gain/loss | **未建模** |
| Realized FX gain/loss | **未建模** |
| Journal / GL entry | 与 FX 重估联动 **未观察到** |
| `currency_settings.exchange_rate` | 配置/展示用数值，非期末重估价队列 |
| EOC exchange risk score | 仪表盘启发式，非敞口重估结果 |
| AR/AP `amount`/`balance` | 原始记账金额，非重估后本位币 |
| Bank/cash `current_balance` | 账户币余额，无期末调汇 |
| Scheduler job（通用） | 平台队列概念；无 FX 任务绑定证据 |
| GTFIP exchange-rate plug-in | 文档保留接口，非运行作业 |
| Finance close authority（模块叙述） | 规格意图，不等于已实现关账+重估 |
| `profit_snapshots` 等命名 | 存在利润快照类表名线索时，仍无 FX 重估字段证据 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| REV-E01 | finance 应用无 revaluat/journal/period-close 命中 | 强缺口 | `apps/finance/**/*.py` 检索 |
| REV-E02 | 全库 py/md/html 无 revaluation/exchange gain/unrealized 命中 | 强缺口 | 工作区定向检索 |
| REV-E03 | currency capability 无作业 API | 强 | `core/capabilities/currency/` |
| REV-E04 | EOC 风险分为启发式 | 强 | `v15/template_services/eoc.py` |
| REV-E05 | finance 模块规格无重估/关账表 | 强 | `business_modules/finance.md` |
| REV-E06 | commission_periods 属销售佣金 | 中 | `apps/sales/v14_residual.py` |
| REV-E07 | Scheduler 文档无 FX 任务 | 中 | `docs/reports/V151_Volume014_Scheduler_Center_Report.md` |
| REV-E08 | GTFIP 保留汇率接口叙述 | 中 | `docs/reports/GTFIP.md` |
| REV-E09 | locale-commerce 已标重估未证实 | 强 | [`../locale-commerce/currency.md`](../locale-commerce/currency.md) |
| REV-E10 | 无 jobs/ 目录承载批处理 | 中 | 仓库根 `jobs/` 检索为空 |

## UNKNOWN + 已查路径

1. **线下是否用 Excel 做月末调汇 UNKNOWN。** 已查：apps/finance、templates、reports；无导出“重估工作底稿”专用路径。
2. **外部 ERP/会计系统是否承接关账 UNKNOWN。** 已查：integration/business_modules、finance 依赖叙述。
3. **`profit_snapshots` 是否含隐藏 FX 字段 UNKNOWN。** 已查：finance DDL 段命名、services 引用；未见重估列消费。
4. **未来插件是否计划实现重估 UNKNOWN。** 已查：docs/reports 保留接口与 excellence 列表；无实现代码。
5. **多账套关账是否在 tenant 层另有表 UNKNOWN。** 已查：tenant_center、runtime DDL 期间相关名。
6. **人工改字典汇率后是否有人用报表重算敞口 UNKNOWN。** 已查：report_center、financial_reports 路由叙述、FX 关键字。
7. **佣金期间关闭是否被误称为财务关账 UNKNOWN（组织用语）。** 已查：commission_periods 页面与销售残余路由。

## 只读来源路径

`apps/finance/` · `apps/sales/` · `core/capabilities/currency/` · `v15/template_services/eoc.py` · `business_modules/finance.md` · `docs/reports/`（Scheduler、GTFIP、I18N audit、Enterprise Intelligence） · `runtime/v14/legacy_support.py` · 邻包 finance / locale-commerce
