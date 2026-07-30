# 报价生命周期与中英状态混用

**Evidence strength:** Strong for stored values and active actions; weak for a coherent transition policy  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## Scope 与关键结论

活动报价主线以 `Draft / Sent / Negotiating / Won / Lost` 五个英文值显示和统计，但状态动作允许在这些值之间直接覆盖，未形成顺序状态机。Quote Approve 只实现 `Draft → Sent` 的受控人工发布；转 SO 则不校验当前报价状态，成功后写入列表枚举之外的中文 `已确认`。空值在多个页面被当作 Draft/open，进一步说明“展示归类”不等于规范状态。

## 业务规则

| ID | 规则 |
|---|---|
| QLC-R01 | 普通新增报价默认写 `Draft`；默认币种通常为 USD、汇率 1、有效期 30 天。 |
| QLC-R02 | 引导/语音报价在人工确认且客户、产品、数量有效后创建 Draft，并跳到 Approve 页。 |
| QLC-R03 | 样品转报价也以 Draft 创建；创建本身不代表已发送或已成交。 |
| QLC-R04 | 活动状态动作只接受 `Draft / Sent / Negotiating / Won / Lost` 五个英文值。 |
| QLC-R05 | 状态动作不校验合法前序，因此可直接 Draft→Won、Lost→Draft 等任意覆盖。 |
| QLC-R06 | Quote Approve 是唯一观察到的窄状态门：仅 Draft、有行且人工确认时转 Sent。 |
| QLC-R07 | Save Draft 可以保存 Draft 行修订而不推进状态。 |
| QLC-R08 | 列表把 Won、Lost、Negotiating、Sent 分组，其余值（包括空值、中文 `已确认`）落入 Draft 展示分支。 |
| QLC-R09 | Dashboard 的 open quotes 包括 Draft、Sent、NULL 和空字符串，不含 Negotiating。 |
| QLC-R10 | 转 SO 是独立动作；不由 Sent 自动触发，也不由状态菜单触发。 |
| QLC-R11 | 转 SO 成功把报价状态硬写为中文 `已确认`，该值不在状态动作白名单中。 |
| QLC-R12 | Won KPI 只统计英文 `Won`；`已确认` 不计入 Won，转单可能使成交统计与订单事实分离。 |
| QLC-R13 | 复制报价生成新的 Draft，并复制旧报价行快照；不继承旧状态为 Sent/Won。 |
| QLC-R14 | 打印/Proforma、AI 建议和状态展示不会静默推进报价状态。 |
| QLC-R15 | `quote_history`、`quote_versions` 和文档事件能力存在，但未观察到所有状态覆盖均形成统一、不可变的生命周期事件。 |

## 流程

1. 创建来源可以是普通表单、引导报价或样品转报价，落库为 Draft。
2. Draft 可新增/删除行、打开 Approve 页并保存草稿。
3. Approve 在三道门通过后写 Sent。
4. 用户也可通过状态菜单把记录直接写成任一英文白名单值。
5. Convert SO 不依赖上述顺序；成功后创建订单并把报价写成 `已确认`。
6. 列表、Dashboard、报表分别按自己的硬编码集合归类，中文状态会出现统计漂移。

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QLC-V01 | 状态写入必须属于五值英文列表 | Hard（状态动作） |
| QLC-V02 | 状态转换必须满足允许的前后序 | Missing |
| QLC-V03 | Approve 前状态必须为 Draft | Hard（Approve 路径） |
| QLC-V04 | Approve 前至少一条报价行 | Hard |
| QLC-V05 | Approve 必须提交 `human_confirm=1` | Hard |
| QLC-V06 | Sent 必须有实际发送时间/渠道/收件人 | Missing |
| QLC-V07 | Negotiating 必须从 Sent 进入并保留原因 | Missing |
| QLC-V08 | Won/Lost 必须记录决定日期和原因 | Missing |
| QLC-V09 | 转 SO 前必须是 Sent 或 Won | Missing |
| QLC-V10 | `已确认` 必须映射到规范英文状态 | Missing/violated |
| QLC-V11 | NULL/空状态必须迁移为规范值 | Missing；当前只在展示时回退 |
| QLC-V12 | 状态变更必须使用版本/并发条件 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.status` | 自由文本式报价业务状态；实际出现英文五值及中文 `已确认` |
| `Draft` | 可编辑、可进入 Quote Approve 的草稿 |
| `Sent` | Quote Approve 成功后的“已发送”标签；真实发送证据未绑定 |
| `Negotiating` | 洽谈中展示/统计标签；进入和退出条件未执行 |
| `Won` | 英文成交标签，并进入 won KPI |
| `Lost` | 英文丢单标签，并进入 lost KPI |
| `已确认` | Convert SO 成功后的报价状态；不是五值白名单成员 |
| NULL / `''` | Dashboard 按 open，列表通常按 Draft 外观显示 |
| `quote_date` | 报价日期，也是转 SO 时复制为订单日期的来源 |
| `validity_days` | 报价有效天数；未观察到到期自动失效 |
| `quote_no` | 报价业务编号；生命周期动作日志使用的对象标识 |
| `quote_history` | 状态/历史能力槽位；全路径覆盖程度不明 |
| `quote_versions` | 报价版本能力槽位；未证明与每次状态/改价强绑定 |
| `open_quotes` | Dashboard 的 Draft/Sent/空值口径，不是统一“活动报价”政策 |
| `won_quotes` | 仅 `status='Won'` 的统计口径 |

## 中英状态对照与诚实边界

| 存储值 | 中文显示/业务解读 | 注意 |
|---|---|---|
| Draft | 草稿 | 未发送 |
| Sent | 已发送 | 只证明人工批准动作，不证明邮件送达 |
| Negotiating | 洽谈中 | 可直接手改 |
| Won | 已成交 | 与是否已转 SO 无强约束 |
| Lost | 已丢单 | 可被直接覆盖回来 |
| 已确认 | 已确认/已转单后的写回值 | 列表可能按 Draft 样式，Won KPI 不识别 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QLC-E01 | 创建默认 Draft、USD、汇率和有效期 | 强 | `apps/quotation/services.py` |
| QLC-E02 | 五值状态白名单与直接更新 | 强 | `apps/quotation/services.py`、`quote_pages.py` |
| QLC-E03 | Draft→Sent 三道门 | 强 | `apps/quotation/services.py` |
| QLC-E04 | Draft 才显示 Approve CTA | 强 | `templates/quotes.html`、`quote_detail.html` |
| QLC-E05 | 状态菜单可选全部五值 | 强 | `templates/quote_detail.html` |
| QLC-E06 | 列表其余状态落入 Draft 分支 | 强 | `templates/quotes.html` |
| QLC-E07 | Dashboard open/won 等硬编码口径 | 强 | `apps/quotation/repository.py` |
| QLC-E08 | 转单写 `已确认` | 强 | `apps/sales/repository.py`、`apps/quotation/quote_pages.py` |
| QLC-E09 | 中文 locale 对五值的展示翻译 | 强 | `locales/zh_CN.json` |
| QLC-E10 | 引导创建经人工确认形成 Draft | 强 | `apps/quotation/services.py`、`templates/quote_voice.html` |
| QLC-E11 | Approve 报告确认发布与转单分离 | 中 | `docs/reports/V18_Quote_Approve_Gate_Report.md` |
| QLC-E12 | Ops 报告确认状态动作和转单诚实分离 | 中 | `docs/reports/Business_Strong_A013_Quote_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **Sent 是否对应真实邮件/门户发送、送达或查看事件 UNKNOWN。** 已查：`apps/quotation/`、`templates/quote*.html`、`apps/communication/`、`docs/reports/`。
2. **Negotiating 的正式进入、退出和回退规则 UNKNOWN。** 已查：`apps/quotation/services.py`、`repository.py`、`quote_pages.py`、报价模板。
3. **Won/Lost 的必填原因、决定人和决定时间 UNKNOWN。** 已查：`apps/quotation/`、`quote_history` 相关能力、`docs/reports/`。
4. **`已确认` 应映射为 Sent、Won 还是 Converted UNKNOWN。** 已查：`apps/sales/`、`apps/quotation/`、`locales/`、`business_modules/quotation.md`。
5. **有效期到期后的自动状态处理 UNKNOWN。** 已查：`apps/quotation/`、quote monitor/scheduler 引用、`docs/reports/`。
6. **状态变更是否在所有路径写入统一历史 UNKNOWN。** 已查：`apps/quotation/history.py`、`utils.py`、`services.py`、文档事件代码。
7. **并发状态覆盖的冲突处理 UNKNOWN。** 已查：`apps/quotation/repository.py`、`services.py`；未见版本条件更新。

## 交叉引用

- 报价基线：[`../crm/quotation.md`](../crm/quotation.md)
- 转单后的订单状态：[`../sales/sales_order.md`](../sales/sales_order.md)
- 人工发布门：[`quote_approve.md`](quote_approve.md)
