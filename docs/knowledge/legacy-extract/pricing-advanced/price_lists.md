# 价目表、客户价与等级价

## Scope与证据强度

本页判断 Legacy 中何者可称“价目表”。强证据来自产品主数据、报价行、客户历史价查询和报价页面；中等证据来自 `product_price_rules` DDL；`business_modules/product.md` 声明的 `product_prices` 属边界目标，未在活动 DDL/运行调用中得到同等证明。

结论：运行主链以产品主数据成本、人工毛利率和历史报价提示为核心。没有证据证明存在带名称、版本、有效期、客户分配和优先级的正式价目表引擎。

## 业务规则（稳定ID）

1. **PL-R01** 产品记录按 SKU 保存单一 `cost_price` 和 `sale_price`，它们是主数据参考，不是带版本的价目表行。
2. **PL-R02** 新增报价行并不以 `sale_price` 作为运行权威；正常路径以采用成本和目标毛利率反推成交单价。
3. **PL-R03** 人工提交成本不大于零时回退到产品主数据 `cost_price`；产品成本仍可为零。
4. **PL-R04** 报价详情的“客户价格历史”查询该客户最近 10 条报价行，按报价日期倒序。
5. **PL-R05** 报价详情的最近/最低/最高/平均价统计跨该客户所有产品，不是当前 SKU 专属价目。
6. **PL-R06** `resolve_product_line_hint` 可取“客户+产品”最近正数单价作为建议；建议不静默覆盖人工定价。
7. **PL-R07** 语音/引导报价在历史单价高于成本时，用该价格反推毛利率，再走统一报价行公式；否则采用成本有值时的默认 25% 毛利率。
8. **PL-R08** 报价复制原样保留每行成本、毛利率、单价和金额；不会按当前产品价重新定价。
9. **PL-R09** `product_price_rules` 结构可表达客户等级、国家、币种、国别系数、汇率、成本、利润率、折扣和结果价，但未发现报价主链读取或匹配它。
10. **PL-R10** `business_modules/product.md` 将 `product_prices` 描述为价格等级表，这是目标边界声明，不能替代运行 DDL/调用证据。
11. **PL-R11** 产品详情允许查看/编辑 `sale_price`；成本价显示受 `Cost Price.view` 权限保护，而销售价未见同级隐藏。
12. **PL-R12** `apps/product/utils.py` 的价格更新帮助器使用 `selling_price`，主表与页面使用 `sale_price`，因此该帮助器不能被视为可靠价目维护入口。

## 流程

### 主运行路径

1. 产品维护单个参考成本与销售价。
2. 建报价时选择产品；页面可带出成本，服务端在成本无效时再回退主成本。
3. 服务按目标毛利率形成报价行成交价并持久化。
4. 报价详情展示客户级历史价格统计，供人判断。
5. 引导报价可额外读取客户+SKU 最近单价，但仍只把它转成毛利率建议。
6. 复制报价时保留旧价格快照，不重新查产品或规则表。

### 预留等级价路径

`product_price_rules` 只证明可存多维规则。已查活动路由、服务和仓储，未形成“选客户等级→按日期/数量匹配→生成报价价→记录命中规则”的闭环。

## 校验（强/弱/缺失）

1. **PL-V01（强）** 新增报价行前必须找到产品；不存在时不新增。
2. **PL-V02（强）** 客户+SKU 历史提示只接受既往正数单价。
3. **PL-V03（弱）** `product_code` 可用于产品识别，但未见它对价目规则形成外键完整性。
4. **PL-V04（缺失）** 未见正式价目表名称、唯一代码和版本校验。
5. **PL-V05（缺失）** 未见价格有效起止日期及日期重叠校验。
6. **PL-V06（缺失）** 未见数量阶梯的最小量、最大量、区间不重叠校验。
7. **PL-V07（缺失）** 未见客户等级存在性或客户到等级的强关联校验。
8. **PL-V08（缺失）** 未见币种一致性或历史价格跨币种归一校验。
9. **PL-V09（缺失）** 未见同一 SKU 多个规则的优先级、冲突消解或唯一命中校验。
10. **PL-V10（缺失/不一致）** `sale_price` 与 `selling_price` 字段名未统一，辅助更新路径可能失效。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `products.cost_price` | SKU 默认成本输入；无日期、批次或币种字段 |
| `products.sale_price` | SKU 单一参考销售价 |
| `quote_items.price` | 报价行实际成交/报出单价 |
| `quote_items.cost_price` | 报价采用成本快照 |
| `quote_items.profit_rate` | 形成或反映成交价的毛利率 |
| 客户价格历史 | 指定客户最近 10 条报价行；不是合同价 |
| `last_unit_price` | 客户+SKU 最近正数报价单价建议 |
| `product_price_rules.customer_level` | 预留的等级匹配维度 |
| `product_price_rules.country` | 预留的国家匹配维度 |
| `product_price_rules.currency` | 预留的规则币种 |
| `country_factor` | 预留国别系数，未见运行解释 |
| `selling_price` / `final_price` | 规则表预留结果字段，未证明对报价生效 |
| `product_prices` | 模块规范声明的目标表名；运行存在性不确定 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| `Draft` | 价格仍可在报价批准页人工修改 |
| `Sent` | 人工批准后已发送；不证明价格表锁定 |
| `Active` | 报价模板可用状态；未发现正式价目表 Active 状态 |
| 主数据价 | 产品上的成本/销售参考值 |
| 历史价 | 既往报价快照 |
| 建议价 | 只供人工决策，不自动提交 |
| 等级价 | 仅有结构预留，未证实运行命中 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| PL-E01 | 产品表只有单值成本价和销售价 | 强 | `runtime/v14/legacy_support.py` |
| PL-E02 | 新增报价行取产品成本但不使用 `sale_price` 定价 | 强 | `apps/quotation/services.py`、`apps/quotation/repository.py` |
| PL-E03 | 客户历史价为最近 10 条报价行 | 强 | `apps/quotation/repository.py` |
| PL-E04 | 页面展示最近/最低/最高/平均和明细 | 强 | `apps/quotation/services.py`、`templates/quote_detail.html` |
| PL-E05 | 客户+SKU 最近价只是提示 | 强 | `v15/ux/master_defaults.py` |
| PL-E06 | 引导报价可用最近价反推毛利率 | 强 | `apps/quotation/services.py` |
| PL-E07 | 多维价格规则只有 DDL，未发现活动调用 | 中/缺失证据 | `runtime/v14/legacy_support.py`、`apps/product/`、`apps/quotation/` |
| PL-E08 | `product_prices` 只见于模块边界声明 | 弱 | `business_modules/product.md` |
| PL-E09 | 产品页面直接维护 `sale_price` | 强 | `templates/product_detail.html`、`apps/product/repository.py` |
| PL-E10 | 报告记录 `selling_price` 与 `sale_price` 不一致 | 中 | `docs/reports/V151E_Volume008_Product_Business_Chain_Extraction_Report.md` |

## UNKNOWN + 已查路径

1. **正式 `price_lists` / `price_list_items` 表是否存在：UNKNOWN。** 已查路径：`runtime/v14/legacy_support.py`、`database/`、`apps/product/`、`apps/quotation/`。
2. **`business_modules/product.md` 所称 `product_prices` 是否在其他部署落地：UNKNOWN。** 已查路径：`business_modules/product.md`、Legacy DDL、Python/SQL 调用点。
3. **客户是否有持久化价格等级：UNKNOWN。** 已查路径：`apps/customer/`、`apps/product/`、`product_price_rules` DDL。
4. **数量阶梯价是否存在：UNKNOWN。** 已查路径：`apps/quotation/`、`apps/product/`、`templates/`、`business_modules/`。
5. **等级/国家/币种规则的匹配优先级：UNKNOWN。** 已查路径：`apps/product/`、`apps/quotation/`、`apps/finance/`、`runtime/v14/legacy_support.py`。
6. **价目表有效期、审批、版本和发布状态：UNKNOWN。** 已查路径：`apps/quotation/`、`templates/`、`docs/reports/`。
7. **历史客户价是否应排除 Lost/Draft 报价：UNKNOWN。** 已查路径：`apps/quotation/repository.py`、`services.py`；当前查询未按状态过滤。
8. **`selling_price` 辅助更新是否因外部迁移补列而可用：UNKNOWN。** 已查路径：`apps/product/utils.py`、Legacy products DDL、Volume 008 报告。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
