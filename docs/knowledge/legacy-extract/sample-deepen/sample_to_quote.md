# 样品转报价交界与追溯字段

## Scope与证据强度

本页深化 `/create_quote_from_sample/{sample_id}`。强证据覆盖 Draft 报价创建、客户继承、商业头默认和 `quotes.sample_id`；中等证据覆盖 requirement/opportunity 的条件传播，因为 helper 依赖列存在并吞掉异常。

该动作只建立报价头，不自动把样品测量、需求、产品绑定、目标价、图片或库存数量转成报价行。报价计价交叉引用 [`../pricing-advanced/quote_pricing_engine.md`](../pricing-advanced/quote_pricing_engine.md)。

## 业务规则（稳定ID）

1. **SQ-R01** Sample360 的 Create Quote 是独立人工动作，并有浏览器确认。
2. **SQ-R02** 服务按 `QT` 加秒级时间戳生成报价编号。
3. **SQ-R03** 新报价 customer_id 优先取样品 customer_id；样品不存在时当前服务仍可能以空客户继续创建。
4. **SQ-R04** 新报价日期为服务器当天，状态固定 Draft。
5. **SQ-R05** 报价 INSERT 直接保存 `sample_id`，形成 Quote→Sample 主追溯。
6. **SQ-R06** 商业头使用客户默认解析：最近客户报价优先，其次品牌币种，最后平台默认。
7. **SQ-R07** 创建后再更新 currency、exchange_rate、validity_days、payment_term、delivery_time 和 remark。
8. **SQ-R08** `link_quote_from_sample` 再读取样品；若 quotes 有相应列，则传播 sample_id、requirement_id、opportunity_id。
9. **SQ-R09** 若样品有 requirement_id，helper 回写业务需求 quote_id，并在 requirement_links 存在时追加 from_sample 关系。
10. **SQ-R10** 追溯 helper 的表/列不存在或内部失败时可静默降级，报价头创建仍完成。
11. **SQ-R11** 创建路径不自动生成 `quote_items`；新报价金额为默认/空值，需后续人工选品计价。
12. **SQ-R12** 样品绑定的 product_id 不会自动成为报价行。
13. **SQ-R13** `sample_requirements.target_price`、供应商价格和分析数据不会自动影响报价价格。
14. **SQ-R14** 未见按 sample_id 查重；同一样品可反复点击生成多个 Draft 报价。
15. **SQ-R15** 当前路由未见 Quotes.add 或 Samples.view 服务端权限门。
16. **SQ-R16** Lifecycle context 可从样品列出下游报价，也可从报价返回样品，但它是查询投影，不替代持久追溯字段。
17. **SQ-R17** 转样报价不设置 `salesperson_id`，与普通新增报价路径不一致；按销售员过滤的后续可见性存在风险。
18. **SQ-R18** 仓库同时保留 `quote_pages.py` 同名 legacy 实现；该副本硬编码 USD 且缺完整商业头和 lifecycle link，实际挂载优先级决定运行行为。
19. **SQ-R19** 同 requirement 多次转报价时，需求头 `quote_id` 指向最后一次生成的报价，而关系链接可并存。

## 流程

1. 用户在 Sample360 点击 Create Quote 并确认。
2. Quotation 服务读取样品。
3. 生成 QT 编号，提取 customer_id。
4. 解析该客户商业头默认。
5. 插入 Draft 报价头，包含 currency 和 sample_id。
6. 更新完整商业头字段。
7. 尝试传播 requirement/opportunity，回写需求下游和关系链接。
8. 重定向报价详情。
9. 用户后续添加报价行、批准及转 SO；样品动作本身不计价。

## 校验（强/弱/缺失）

1. **SQ-V01（强/类型）** 路由 sample_id 为整数路径参数。
2. **SQ-V02（弱/UI）** Sample360 使用浏览器 confirm。
3. **SQ-V03（弱）** 商业头解析有 USD/1等回退，避免字段完全空缺。
4. **SQ-V04（缺失）** 未在创建前硬拒绝不存在的样品。
5. **SQ-V05（缺失）** 未要求样品状态为 New/分析完成/Stocked。
6. **SQ-V06（缺失）** 未要求样品已绑定产品或已完成测量。
7. **SQ-V07（缺失）** 未按 sample_id 防重复报价。
8. **SQ-V08（缺失）** 未见 Quotes.add/Samples.view 服务端权限检查。
9. **SQ-V09（缺失）** 未验证客户存在、Active 或可报价。
10. **SQ-V10（缺失）** 未验证 requirement_id/opportunity_id 指向有效记录。
11. **SQ-V11（缺失）** 未要求至少一条报价行才完成“转报价”。
12. **SQ-V12（缺失）** 编号无数据库唯一性/并发冲突处理证据。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sample_id`（路由） | 来源样品 id |
| `samples.customer_id` | 新报价客户来源 |
| `quotes.sample_id` | 报价对来源样品的直接追溯 |
| `quotes.customer_id` | 从样品继承的客户 |
| `quote_no` | QT+秒级时间戳编号 |
| `quote_date` | 创建当天 |
| `Draft` | 新报价初始状态 |
| `currency/exchange_rate` | 客户商业头默认/快照 |
| `validity_days` | 默认或历史报价继承的有效天数 |
| `payment_term/delivery_time` | 默认或历史商业条件 |
| `samples.requirement_id` | 可选业务需求追溯源 |
| `samples.opportunity_id` | 可选商机追溯源 |
| `business_requirements.quote_id` | requirement 下游报价回写 |
| `requirement_links` | 可选 from_sample 关系记录 |
| `quote_items` | 此动作不创建的报价行集合 |
| `sample_requirements.target_price` | 样品分析参考目标价，不自动传播 |

## 状态词汇

| 状态/词汇 | 含义 |
|---|---|
| Draft | 样品转出后的报价状态 |
| New | 样品状态；不阻止转报价 |
| Stocked | 样品入库状态；不是转报价前置 |
| from_sample | requirement link 的关系类型 |
| last_quote | 商业头默认来源之一 |
| brand/platform | 商业头后备来源 |
| Linked | 查询/字段可追溯，不是独立状态 |
| Converted | UNKNOWN；样品自身不会被更新为“已转报价” |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SQ-E01 | Sample360 提供 Create Quote CTA 和确认 | 强 | `templates/sample360.html` |
| SQ-E02 | Quotation 路由直接调用 create_quote_from_sample | 强 | `apps/quotation/router.py` |
| SQ-E03 | 服务创建 Draft、继承客户并解析商业头 | 强 | `apps/quotation/services.py` |
| SQ-E04 | repository INSERT保存 sample_id且无行项 | 强 | `apps/quotation/repository.py` |
| SQ-E05 | 默认链来自最近报价/品牌/平台 | 强 | `v15/ux/master_defaults.py` |
| SQ-E06 | lifecycle helper 条件传播需求/商机并回写需求 | 强/可降级 | `v15/business_lifecycle/workflow.py` |
| SQ-E07 | context360 可双向展示 Sample↔Quote | 中 | `v15/business_lifecycle/context360.py` |
| SQ-E08 | A-005 报告验证样品、报价与需求追溯 | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| SQ-E09 | 既有样品权威页确认该动作不代表发样 | 强（交叉） | `../sample/sample.md` |
| SQ-E10 | legacy 同名路由存在且行为与服务版不同 | 强（分叉证据） | `apps/quotation/quote_pages.py`、`apps/quotation/v14_residual.py` |
| SQ-E11 | requirement 回写与链接采用覆盖/并存组合 | 强 | `v15/business_lifecycle/workflow.py` |

## UNKNOWN + 已查路径

1. **同一样品允许生成多少个报价及主报价选择规则 UNKNOWN。** 已查路径：Quotation service/repository、Sample360、lifecycle context。
2. **样品不存在时是否由其他中间件阻止空客户报价 UNKNOWN。** 已查路径：router、service、repository、middleware。
3. **样品分析何时被视为可报价 UNKNOWN。** 已查路径：Sample status、analysis tables、Quote CTA。
4. **target_price 应否自动成为报价参考 UNKNOWN。** 已查路径：sample_requirements、Quotation pricing、templates。
5. **绑定 product_id 应否自动创建报价行 UNKNOWN。** 已查路径：create_quote_from_sample、quote item insertion、A-005报告。
6. **图片、测量和材料报告是否随报价打印 UNKNOWN。** 已查路径：Quote print/NDE、Sample print模板、Quotation服务。
7. **requirement/opportunity 列在所有部署是否存在 UNKNOWN。** 已查路径：lifecycle migrations、PRAGMA条件 helper、Legacy DDL。
8. **Create Quote 服务端权限和审计日志 UNKNOWN。** 已查路径：Quotation router/services、permission checker、write_log调用。
9. **样品自身是否需要记录 quote_id/converted 状态 UNKNOWN。** 已查路径：samples schema、Sample services、lifecycle workflow。
10. **转样报价 salesperson_id 应取客户 owner、当前用户还是保持空值 UNKNOWN。** 已查路径：Quotation 普通新增与转样路径、客户 owner 字段、权限过滤。
11. **生产运行时实际挂载服务版还是 legacy 同名路由 UNKNOWN。** 已查路径：Quotation router、quote_pages、v14_residual 与 app 路由注册。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
